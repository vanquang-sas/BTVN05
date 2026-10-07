"""csv-quality script: thống kê fixture, lỗi input/schema/parse exit 1, lỗi dữ liệu exit 0, tính quá tải theo max-hours."""

import json
import subprocess
import sys

import pytest

import paths

SCRIPT = paths.FIXTURES_DIR / "skills" / "csv-quality" / "scripts" / "check_csv.py"


def run(path, max_hours: str | None = "8"):
    args = [sys.executable, str(SCRIPT), "--input", str(path)]
    if max_hours is not None:
        args.extend(["--max-hours", str(max_hours)])
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)


def write_csv(tmp_path, text):
    path = tmp_path / "t.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_fixture_statistics():
    result = run(paths.FIXTURES_DIR / "data" / "tasks.csv", max_hours="8")
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["row_count"] == 6
    assert data["missing_owner_count"] == 1
    assert data["invalid_hours_count"] == 1
    assert data["duplicate_id_count"] == 1
    assert data["duplicate_ids"] == ["T02"]
    assert [(i["line"], i["column"], i["type"]) for i in data["issues"]] == [
        (4, "owner", "missing_owner"),
        (5, "hours", "invalid_hours"),
        (6, "task_id", "duplicate_id"),
    ]
    assert data["max_hours"] == 8.0
    assert "hours_by_owner" in data
    assert "overloaded_owners" in data
    assert "excluded_rows" in data


@pytest.mark.parametrize("hours", ["NaN", "nan", "Infinity", "-inf", "-1", ""])
def test_non_finite_negative_or_empty_hours_rejected(tmp_path, hours):
    data = json.loads(run(write_csv(tmp_path, f"task_id,owner,hours\nT01,Lan,{hours}\n"), max_hours="8").stdout)
    assert data["invalid_hours_count"] == 1
    assert data["issues"][0]["line"] == 2


def test_clean_data_exit_0_without_issues(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner,hours\nT01,Lan,4\nT02,Minh,2.5\n"), max_hours="8")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["issues"] == []
    assert data["hours_by_owner"] == {"Lan": 4.0, "Minh": 2.5}
    assert data["overloaded_owners"] == []


def test_missing_file_exit_1(tmp_path):
    result = run(tmp_path / "khong-co.csv", max_hours="8")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "Không đọc được file" in result.stderr


def test_missing_column_exit_1(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner\nT01,Lan\n"), max_hours="8")
    assert result.returncode == 1
    assert "Thiếu cột bắt buộc: hours" in result.stderr


def test_parse_error_exit_1(tmp_path):
    result = run(write_csv(tmp_path, 'task_id,owner,hours\nT01,"La"n,4\n'), max_hours="8")
    assert result.returncode == 1
    assert "Lỗi parse CSV" in result.stderr


def test_script_does_not_modify_input():
    source = paths.FIXTURES_DIR / "data" / "tasks.csv"
    before = source.read_bytes()
    run(source, max_hours="8")
    assert source.read_bytes() == before


def test_missing_max_hours_exit_1(tmp_path):
    result = run(write_csv(tmp_path, "task_id,owner,hours\nT01,Lan,4\n"), max_hours=None)
    assert result.returncode == 1
    assert "Thiếu tham số bắt buộc --max-hours" in result.stderr


@pytest.mark.parametrize("invalid_max", ["-1", "abc", "NaN", "inf", ""])
def test_invalid_max_hours_exit_1(tmp_path, invalid_max):
    result = run(write_csv(tmp_path, "task_id,owner,hours\nT01,Lan,4\n"), max_hours=invalid_max)
    assert result.returncode == 1
    assert "không hợp lệ" in result.stderr


def test_edge_case_first_occurrence_invalid_hours_rejects_duplicate(tmp_path):
    csv_text = "task_id,owner,hours\nE01,Lan,abc\nE01,Lan,5\nE02,Minh,0\n"
    result = run(write_csv(tmp_path, csv_text), max_hours="0")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["row_count"] == 3
    assert data["duplicate_ids"] == ["E01"]
    assert "Lan" not in data["hours_by_owner"]
    assert data["hours_by_owner"] == {"Minh": 0.0}
    assert data["overloaded_owners"] == []
    assert len(data["excluded_rows"]) == 2
    assert data["excluded_rows"][0] == {"line": 2, "task_id": "E01", "reasons": ["invalid_hours"]}
    assert data["excluded_rows"][1] == {"line": 3, "task_id": "E01", "reasons": ["duplicate_id"]}
