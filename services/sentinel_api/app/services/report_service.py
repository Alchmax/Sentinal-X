from datetime import UTC, datetime


def generate_html_report(
    case, evidence_list, findings, events, timeline, notes, audit
) -> str:
    def esc(s):
        return (
            (str(s) if s is not None else "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    lines = []
    lines.append(
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Sentinel X Report</title>"
    )
    lines.append(
        "<style>body{font-family:Arial,sans-serif;margin:24px;color:#222;}h1,h2{color:#0b6;}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ccc;padding:6px;font-size:12px;} .muted{color:#666;font-size:11px;}</style>"
    )
    lines.append("</head><body>")
    lines.append("<h1>SENTINEL X Investigation Report</h1>")
    lines.append(
        f"<p class='muted'>Generated (UTC): {datetime.now(UTC).isoformat()}</p>"
    )
    lines.append(
        f"<h2>Case</h2><p><b>ID:</b> {esc(case.id)}<br><b>Title:</b> {esc(case.title)}<br><b>Status:</b> {esc(case.status)}<br><b>Priority:</b> {esc(case.priority)}<br><b>Description:</b> {esc(case.description)}</p>"
    )
    lines.append(
        f"<h2>Evidence Inventory ({len(evidence_list)})</h2><table><tr><th>Filename</th><th>SHA-256</th><th>Size</th><th>Signature</th></tr>"
    )
    for e in evidence_list:
        lines.append(
            f"<tr><td>{esc(e.filename)}</td><td>{esc(e.sha256)}</td><td>{e.size_bytes}</td><td>{esc(e.detected_signature)}</td></tr>"
        )
    lines.append("</table>")
    lines.append(f"<h2>Findings ({len(findings)})</h2>")
    for f in findings:
        lines.append(
            f"<p><b>[{esc(f.kind)}]</b> {esc(f.title)}<br>{esc(f.description)}<br><span class='muted'>refs: {esc(f.evidence_refs)}</span></p>"
        )
    lines.append(
        f"<h2>Detections / Events ({len(events)})</h2><table><tr><th>Time</th><th>Actor</th><th>Type</th><th>Message</th></tr>"
    )
    for ev in events[:500]:
        lines.append(
            f"<tr><td>{esc(ev.timestamp)}</td><td>{esc(ev.actor)}</td><td>{esc(ev.event_type)}</td><td>{esc(ev.message)}</td></tr>"
        )
    lines.append("</table>")
    lines.append(f"<h2>Timeline ({len(timeline)})</h2>")
    for t in timeline:
        lines.append(
            f"<p><b>{esc(t.timestamp)}</b> [{esc(t.entry_type)}] {esc(t.title)} - {esc(t.description)}</p>"
        )
    lines.append(f"<h2>Analyst Notes ({len(notes)})</h2>")
    for n in notes:
        lines.append(
            f"<p>{esc(n.content)} <span class='muted'>({esc(n.created_at)})</span></p>"
        )
    lines.append(
        "<h2>Known Limitations</h2><ul><li>Automated detections are heuristic and require analyst review.</li><li>AI not used unless explicitly enabled.</li><li>Chain of custody claims limited to recorded audit events.</li></ul>"
    )
    lines.append(
        "<p class='muted'>Detection rules version: 0.1.0 | App version: 0.1.0</p>"
    )
    lines.append("</body></html>")
    return "\n".join(lines)


def generate_pdf_report(case, evidence_list, findings, events, timeline, notes) -> bytes:
    try:
        from io import BytesIO

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        return b""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 720, "SENTINEL X Investigation Report")
    c.setFont("Helvetica", 10)
    y = 700
    c.drawString(72, y, f"Case: {case.title} ({case.id})"); y -= 14
    c.drawString(72, y, f"Status: {case.status} Priority: {case.priority}"); y -= 14
    c.drawString(72, y, f"Evidence items: {len(evidence_list)}"); y -= 14
    c.drawString(72, y, f"Findings: {len(findings)}  Events: {len(events)}  Timeline: {len(timeline)}"); y -= 20
    c.drawString(72, y, "Evidence:"); y -= 14
    for e in evidence_list[:40]:
        c.drawString(80, y, f"- {e.filename} {e.sha256}"); y -= 12
        if y < 72:
            c.showPage(); y = 720
    c.drawString(72, y, "Findings:"); y -= 14
    for f in findings[:40]:
        c.drawString(80, y, f"- [{f.kind}] {f.title}"); y -= 12
        if y < 72:
            c.showPage(); y = 720
    c.save()
    return buf.getvalue()
