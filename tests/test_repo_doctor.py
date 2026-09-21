from pathlib import Path

from repo_doctor import human_size, scan_repository


def test_human_size():
    assert human_size(1024) == "1.0 KB"
    assert human_size(5 * 1024 * 1024) == "5.0 MB"


def test_scan_repository(tmp_path: Path):
    (tmp_path / "README.md").write_text("# demo\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("# TODO: improve\nprint('hi')\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()

    report = scan_repository(tmp_path)

    assert report["file_count"] == 3
    assert report["checks"]["README"] is True
    assert report["checks"]["tests"] is True
    assert report["checks"]["LICENSE"] is False
    assert report["languages"]["Python"] == 2
    assert report["todos"] == 1
