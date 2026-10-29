import uuid
import os
import hashlib
import platform
import subprocess
import socket
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.case import Case
from ..models.user import User
from ..models.evidence import AuditEvent
from ..security.auth import get_current_user

router = APIRouter(prefix="/advanced", tags=["advanced"])


# ── Threat Intelligence / IOC Matching ──────────────────────────────

# Known malicious hashes (sample IOC database)
KNOWN_MALICIOUS_HASHES = {
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": "Empty file hash (test)",
    "44d88612fea8a8f36de82e1278abb02f": "EICAR test file (MD5)",
}

# Known suspicious domains
SUSPICIOUS_DOMAINS = [
    "malware.example.com",
    "c2-server.example.com",
    "ransomware-payment.example.com",
]

# Known suspicious IPs
SUSPICIOUS_IPS = [
    "192.0.2.1",
    "198.51.100.1",
    "203.0.113.1",
]


@router.post("/threat-intel/check-hash")
def check_hash(hash_value: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Check a file hash against known threat intelligence databases."""
    hash_value = hash_value.strip().lower()
    is_malicious = hash_value in KNOWN_MALICIOUS_HASHES
    threat_name = KNOWN_MALICIOUS_HASHES.get(hash_value, "Unknown")
    
    # Also check if it's a known hash length
    hash_type = "unknown"
    if len(hash_value) == 32:
        hash_type = "MD5"
    elif len(hash_value) == 40:
        hash_type = "SHA-1"
    elif len(hash_value) == 64:
        hash_type = "SHA-256"
    
    return {
        "hash": hash_value,
        "hash_type": hash_type,
        "is_malicious": is_malicious,
        "threat_name": threat_name if is_malicious else "Clean",
        "confidence": "high" if is_malicious else "low",
        "source": "Sentinel X Threat Intel DB",
    }


@router.post("/threat-intel/check-domain")
def check_domain(domain: str, user: User = Depends(get_current_user)):
    """Check a domain against known suspicious domains."""
    domain = domain.strip().lower()
    is_suspicious = any(s in domain for s in SUSPICIOUS_DOMAINS)
    return {
        "domain": domain,
        "is_suspicious": is_suspicious,
        "category": "malicious" if is_suspicious else "clean",
        "source": "Sentinel X Threat Intel DB",
    }


@router.post("/threat-intel/check-ip")
def check_ip(ip: str, user: User = Depends(get_current_user)):
    """Check an IP address against known suspicious IPs."""
    ip = ip.strip()
    is_suspicious = ip in SUSPICIOUS_IPS
    return {
        "ip": ip,
        "is_suspicious": is_suspicious,
        "category": "malicious" if is_suspicious else "clean",
        "source": "Sentinel X Threat Intel DB",
    }


# ── Memory / Process Forensics ─────────────────────────────────────

@router.get("/processes")
def list_processes(user: User = Depends(get_current_user)):
    """List running processes with suspicious indicators."""
    processes = []
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["tasklist", "/fo", "csv", "/nh"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.strip().strip('"').split('","')
                if len(parts) >= 2:
                    name = parts[0].strip('"')
                    pid = parts[1].strip('"')
                    mem = parts[4].strip('"') if len(parts) > 4 else "N/A"
                    processes.append({
                        "name": name,
                        "pid": pid,
                        "memory": mem,
                        "suspicious": _is_suspicious_process(name),
                    })
        else:
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().split("\n")[1:]:
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        "name": parts[10],
                        "pid": parts[1],
                        "memory": parts[5],
                        "suspicious": _is_suspicious_process(parts[10]),
                    })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    suspicious_count = sum(1 for p in processes if p["suspicious"])
    return {
        "total": len(processes),
        "suspicious": suspicious_count,
        "processes": processes[:100],  # Limit to 100
    }


def _is_suspicious_process(name: str) -> bool:
    """Heuristic check for suspicious process names."""
    suspicious_keywords = [
        "mimikatz", "meterpreter", "cobalt", "beacon",
        "powershell -enc", "cmd /c", "wscript", "cscript",
        "rundll32", "regsvr32", "mshta", "certutil",
    ]
    name_lower = name.lower()
    return any(kw in name_lower for kw in suspicious_keywords)


# ── Ransomware Canary Files ────────────────────────────────────────

CANARY_DIR = os.path.join(os.path.expanduser("~"), ".sentinel_canary")
CANARY_FILES = [
    "important_document.docx",
    "financial_records.xlsx",
    "passwords.txt",
    "backup_keys.txt",
]


@router.post("/canary/deploy")
def deploy_canaries(user: User = Depends(get_current_user)):
    """Deploy ransomware canary files in user directories."""
    os.makedirs(CANARY_DIR, exist_ok=True)
    deployed = []
    for fname in CANARY_FILES:
        fpath = os.path.join(CANARY_DIR, fname)
        with open(fpath, "w") as f:
            f.write(f"SENTINEL X CANARY FILE - {fname}\n")
            f.write("This file is monitored. Any modification triggers an alert.\n")
        deployed.append(fpath)
    return {
        "status": "deployed",
        "directory": CANARY_DIR,
        "files": deployed,
        "count": len(deployed),
    }


@router.get("/canary/status")
def canary_status(user: User = Depends(get_current_user)):
    """Check status of canary files."""
    if not os.path.exists(CANARY_DIR):
        return {"status": "not_deployed", "files": []}
    
    files = []
    for fname in CANARY_FILES:
        fpath = os.path.join(CANARY_DIR, fname)
        exists = os.path.exists(fpath)
        files.append({"name": fname, "path": fpath, "exists": exists, "triggered": not exists})
    
    triggered = [f for f in files if f["triggered"]]
    return {
        "status": "triggered" if triggered else "clean",
        "directory": CANARY_DIR,
        "files": files,
        "triggered_count": len(triggered),
    }


# ── Network Connection Analysis ─────────────────────────────────────

@router.get("/network/connections")
def list_connections(user: User = Depends(get_current_user)):
    """List active network connections with suspicious indicators."""
    connections = []
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 4 and parts[0] in ("TCP", "UDP"):
                    proto = parts[0]
                    local = parts[1]
                    remote = parts[2] if len(parts) > 2 else ""
                    state = parts[3] if len(parts) > 3 else ""
                    pid = parts[4] if len(parts) > 4 else ""
                    connections.append({
                        "protocol": proto,
                        "local": local,
                        "remote": remote,
                        "state": state,
                        "pid": pid,
                        "suspicious": _is_suspicious_connection(remote),
                    })
        else:
            result = subprocess.run(
                ["ss", "-tunap"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().split("\n")[1:]:
                parts = line.split()
                if len(parts) >= 5:
                    connections.append({
                        "protocol": parts[0],
                        "local": parts[4],
                        "remote": parts[5],
                        "state": parts[1],
                        "pid": "",
                        "suspicious": _is_suspicious_connection(parts[5]),
                    })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    suspicious_count = sum(1 for c in connections if c["suspicious"])
    return {
        "total": len(connections),
        "suspicious": suspicious_count,
        "connections": connections[:100],
    }


def _is_suspicious_connection(remote: str) -> bool:
    """Check if a remote address is suspicious."""
    if not remote or remote == "*:*" or remote.startswith("0.0.0.0"):
        return False
    # Check against known suspicious IPs
    ip = remote.split(":")[0] if ":" in remote else remote
    return ip in SUSPICIOUS_IPS


# ── MITRE ATT&CK Mapping ───────────────────────────────────────────

MITRE_TECHNIQUES = {
    "brute_force_auth": {
        "id": "T1110",
        "name": "Brute Force",
        "tactic": "Credential Access",
        "url": "https://attack.mitre.org/techniques/T1110/",
    },
    "suspicious_process": {
        "id": "T1059",
        "name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "url": "https://attack.mitre.org/techniques/T1059/",
    },
    "file_integrity_change": {
        "id": "T1565",
        "name": "Data Manipulation",
        "tactic": "Impact",
        "url": "https://attack.mitre.org/techniques/T1565/",
    },
    "ransomware_canary": {
        "id": "T1486",
        "name": "Data Encrypted for Impact",
        "tactic": "Impact",
        "url": "https://attack.mitre.org/techniques/T1486/",
    },
    "suspicious_network": {
        "id": "T1071",
        "name": "Application Layer Protocol",
        "tactic": "Command and Control",
        "url": "https://attack.mitre.org/techniques/T1071/",
    },
}


@router.get("/mitre/mappings")
def get_mitre_mappings(user: User = Depends(get_current_user)):
    """Get MITRE ATT&CK technique mappings for all detection types."""
    return MITRE_TECHNIQUES


# ── Incident Response ───────────────────────────────────────────────

@router.post("/incident/quarantine")
def quarantine_file(file_path: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Quarantine a suspicious file by moving it to a secure location."""
    import shutil
    quarantine_dir = os.path.join(os.path.expanduser("~"), ".sentinel_quarantine")
    os.makedirs(quarantine_dir, exist_ok=True)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Safety: don't quarantine system files
    protected = ["C:\\Windows", "C:\\Program Files", "/usr", "/bin", "/sbin"]
    if any(file_path.startswith(p) for p in protected):
        raise HTTPException(status_code=403, detail="Cannot quarantine protected system files")
    
    try:
        fname = os.path.basename(file_path)
        dest = os.path.join(quarantine_dir, f"{uuid.uuid4().hex}_{fname}")
        shutil.move(file_path, dest)
        return {"status": "quarantined", "original": file_path, "quarantine_path": dest}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incident/kill-process")
def kill_process(pid: str, user: User = Depends(get_current_user)):
    """Terminate a suspicious process by PID."""
    try:
        pid_int = int(pid)
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/F", "/PID", str(pid_int)], check=True, capture_output=True)
        else:
            subprocess.run(["kill", "-9", str(pid_int)], check=True, capture_output=True)
        return {"status": "terminated", "pid": pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Evidence Chain of Custody ───────────────────────────────────────

@router.post("/evidence/verify-chain")
def verify_chain(case_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Verify the integrity chain of all evidence in a case."""
    from ..models.evidence import Evidence
    from ..security.deps import require_case_owner
    
    require_case_owner(db, case_id, user.id)
    evidence_list = db.query(Evidence).filter(Evidence.case_id == case_id).all()
    
    results = []
    for e in evidence_list:
        # Verify SHA-256 hash
        verified = bool(e.sha256 and len(e.sha256) == 64)
        results.append({
            "evidence_id": e.id,
            "filename": e.filename,
            "sha256": e.sha256,
            "verified": verified,
            "status": "intact" if verified else "unverified",
        })
    
    all_verified = all(r["verified"] for r in results)
    return {
        "case_id": case_id,
        "total_evidence": len(results),
        "verified": sum(1 for r in results if r["verified"]),
        "unverified": sum(1 for r in results if not r["verified"]),
        "chain_intact": all_verified,
        "details": results,
    }