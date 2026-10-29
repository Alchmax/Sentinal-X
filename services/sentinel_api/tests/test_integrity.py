import os
import tempfile

from app.services.integrity import build_baseline, compare_baseline


def test_integrity_baseline_and_compare():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "a.txt")
    with open(p, "w") as f:
        f.write("hello")
    base = build_baseline(d)
    assert len(base) == 1
    # modify
    with open(p, "w") as f:
        f.write("changed")
    diff = compare_baseline(base, d)
    assert len(diff["modified"]) == 1
    # add new file
    with open(os.path.join(d, "b.txt"), "w") as f:
        f.write("new")
    diff2 = compare_baseline(base, d)
    assert len(diff2["added"]) == 1
    # delete
    os.remove(p)
    diff3 = compare_baseline(base, d)
    assert len(diff3["deleted"]) == 1
    import shutil

    shutil.rmtree(d)
