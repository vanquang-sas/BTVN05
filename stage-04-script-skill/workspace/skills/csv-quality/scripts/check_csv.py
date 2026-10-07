#!/usr/bin/env python3
"""Kiểm tra chất lượng CSV công việc (task_id, owner, hours) và in JSON ra stdout.

Cách chạy (cwd là workspace):
    python skills/csv-quality/scripts/check_csv.py --input data/tasks.csv --max-hours 8

Exit 0: phân tích thành công, kể cả khi dữ liệu có lỗi hoặc người quá tải.
Exit 1: file không tồn tại/không đọc được, thiếu cột bắt buộc hoặc lỗi parse CSV;
        thiếu hoặc sai tham số --max-hours; thông báo ra stderr.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

REQUIRED_COLUMNS = ("task_id", "owner", "hours")
REASON_ORDER = [
    "wrong_field_count",
    "missing_task_id",
    "duplicate_id",
    "missing_owner",
    "invalid_hours",
]


class InputError(Exception):
    pass


def parse_hours(raw: str | None) -> float | None:
    """Số hữu hạn, không âm. Trả None nếu không hợp lệ."""
    if raw is None or not raw.strip():
        return None
    try:
        value = float(raw.strip())
    except ValueError:
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return value


def analyze(path: str, max_hours: float) -> dict:
    try:
        handle = open(path, encoding="utf-8-sig", newline="")
    except OSError as exc:
        raise InputError(f"Không đọc được file {path}: {exc.strerror or exc}") from exc

    with handle:
        reader = csv.reader(handle, strict=True)
        try:
            header = next(reader, None)
            if header is None:
                raise InputError(f"File {path} rỗng, không có header.")
            columns = [c.strip() for c in header]
            missing = [c for c in REQUIRED_COLUMNS if c not in columns]
            if missing:
                raise InputError(f"Thiếu cột bắt buộc: {', '.join(missing)}. Header hiện có: {', '.join(columns)}")
            index = {name: columns.index(name) for name in REQUIRED_COLUMNS}

            row_count = 0
            missing_owner = 0
            invalid_hours = 0
            first_seen: dict[str, int] = {}
            duplicate_ids: list[str] = []
            issues: list[dict] = []

            # Lưu trữ phục vụ tính tải và loại trừ dòng
            hours_by_owner: dict[str, float] = {}
            excluded_rows: list[dict] = []

            for row in reader:
                line = reader.line_num
                if not any(cell.strip() for cell in row):
                    continue  # bỏ qua dòng trống hoàn toàn

                row_count += 1

                def cell(name: str) -> str:
                    position = index[name]
                    return row[position].strip() if position < len(row) else ""

                task_id, owner, hours = cell("task_id"), cell("owner"), cell("hours")

                reasons_set: set[str] = set()

                # 1. Kiểm tra số trường
                if len(row) != len(columns):
                    issues.append({
                        "line": line,
                        "column": None,
                        "type": "wrong_field_count",
                        "task_id": task_id or None,
                        "message": f"Có {len(row)} trường, header có {len(columns)} cột.",
                    })
                    reasons_set.add("wrong_field_count")

                # 2. Kiểm tra task_id
                if not task_id:
                    issues.append({
                        "line": line,
                        "column": "task_id",
                        "type": "missing_task_id",
                        "task_id": None,
                        "message": "task_id trống.",
                    })
                    reasons_set.add("missing_task_id")
                elif task_id in first_seen:
                    if task_id not in duplicate_ids:
                        duplicate_ids.append(task_id)
                    issues.append({
                        "line": line,
                        "column": "task_id",
                        "type": "duplicate_id",
                        "task_id": task_id,
                        "message": f"task_id {task_id} đã xuất hiện ở line {first_seen[task_id]}.",
                    })
                    reasons_set.add("duplicate_id")
                else:
                    first_seen[task_id] = line

                # 3. Kiểm tra owner
                if not owner:
                    missing_owner += 1
                    issues.append({
                        "line": line,
                        "column": "owner",
                        "type": "missing_owner",
                        "task_id": task_id or None,
                        "message": "owner trống.",
                    })
                    reasons_set.add("missing_owner")

                # 4. Kiểm tra hours
                parsed_h = parse_hours(hours)
                if parsed_h is None:
                    invalid_hours += 1
                    issues.append({
                        "line": line,
                        "column": "hours",
                        "type": "invalid_hours",
                        "task_id": task_id or None,
                        "value": hours,
                        "message": f"hours '{hours}' không phải số hữu hạn không âm.",
                    })
                    reasons_set.add("invalid_hours")

                # Xác định cộng giờ hay loại bỏ dòng
                if reasons_set:
                    sorted_reasons = [r for r in REASON_ORDER if r in reasons_set]
                    excluded_rows.append({
                        "line": line,
                        "task_id": task_id if task_id else None,
                        "reasons": sorted_reasons,
                    })
                else:
                    # Dòng hợp lệ: cộng vào tổng giờ của owner
                    hours_by_owner[owner] = hours_by_owner.get(owner, 0.0) + parsed_h

        except csv.Error as exc:
            raise InputError(f"Lỗi parse CSV ở line {reader.line_num}: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise InputError(f"File {path} không phải UTF-8: {exc}") from exc

    # Xác định danh sách người vượt ngưỡng, sắp xếp theo tên
    overloaded_owners = [
        {"owner": o, "total_hours": total}
        for o, total in hours_by_owner.items()
        if total > max_hours
    ]
    overloaded_owners.sort(key=lambda item: item["owner"])

    return {
        "input": path,
        "row_count": row_count,
        "missing_owner_count": missing_owner,
        "invalid_hours_count": invalid_hours,
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_ids": duplicate_ids,
        "issues": sorted(issues, key=lambda item: item["line"]),
        "max_hours": max_hours,
        "hours_by_owner": hours_by_owner,
        "overloaded_owners": overloaded_owners,
        "excluded_rows": excluded_rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kiểm tra chất lượng CSV công việc (task_id, owner, hours).")
    parser.add_argument("--input", required=True, help="Đường dẫn CSV, ví dụ data/tasks.csv")
    parser.add_argument("--max-hours", dest="max_hours", required=False, default=None,
                        help="Ngưỡng giờ tối đa cho mỗi owner (số hữu hạn không âm)")

    args = parser.parse_args(argv)

    if args.max_hours is None:
        print("ERROR: Thiếu tham số bắt buộc --max-hours.", file=sys.stderr)
        return 1

    try:
        max_h = float(args.max_hours.strip())
        if not math.isfinite(max_h) or max_h < 0:
            raise ValueError()
    except (ValueError, AttributeError):
        print(f"ERROR: Giá trị --max-hours '{args.max_hours}' không hợp lệ (phải là số hữu hạn không âm).", file=sys.stderr)
        return 1

    try:
        result = analyze(args.input, max_h)
    except InputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())