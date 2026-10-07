---
name: csv-quality
description: Kiểm tra chất lượng file CSV công việc (cột task_id, owner, hours), tính tổng giờ theo người, phát hiện quá tải theo ngưỡng giờ và ghi báo cáo Markdown dưới output/. Dùng khi người dùng yêu cầu kiểm tra dữ liệu, rà soát trùng lặp hoặc đánh giá quá tải công việc.
---

# CSV quality

Kiểm tra chất lượng CSV công việc và phân tích quá tải bằng script, không tự phỏng đoán số liệu.

## Quy tắc xử lý ngưỡng giờ (--max-hours)

- Khi người dùng có yêu cầu kiểm tra quá tải hoặc phân tích giờ làm:
  - Nếu yêu cầu **chưa có ngưỡng giờ**: Phải hỏi lại người dùng để lấy ngưỡng cụ thể trước khi thực hiện.
  - Tuyệt đối **không tự ý lấy ngưỡng từ các cuộc trò chuyện cũ** hoặc tự đặt giá trị ngầm định.
  - Khi người dùng đã cung cấp ngưỡng: Truyền đúng giá trị đó vào tham số `--max-hours`. Ngưỡng phải là số hữu hạn không âm (ví dụ: `8`, `40`).

## Chạy script

Dùng tool `bash` (cwd là workspace). Lệnh mẫu:

```bash
python skills/csv-quality/scripts/check_csv.py --input <đường dẫn CSV> --max-hours <ngưỡng giờ>
```

Ví dụ: `python skills/csv-quality/scripts/check_csv.py --input data/workload.csv --max-hours 8`

Không cần đọc source script để chạy. Chỉ đọc `scripts/check_csv.py` khi cần hiểu một hành vi mà phần dưới không mô tả.

## Kiểm tra kết quả

- `exit_code` 0: phân tích thành công. `stdout` là JSON gồm `row_count`, `missing_owner_count`, `invalid_hours_count`, `duplicate_id_count`, `duplicate_ids`, `issues`, `max_hours`, `hours_by_owner`, `overloaded_owners`, `excluded_rows`. Dữ liệu có lỗi chất lượng hoặc có người quá tải vẫn là exit 0.
- `exit_code` 1: **lỗi thực thi** (file không tồn tại, thiếu cột bắt buộc, lỗi parse, thiếu hoặc sai `--max-hours`). Đọc `stderr`, báo lỗi cho người dùng. Không bịa thống kê, không ghi báo cáo như thể đã phân tích.
- `timed_out` true hoặc `ok` false: lệnh không chạy xong; báo lỗi, không suy đoán kết quả.
- Phân biệt rõ **lỗi dữ liệu** (nằm trong `issues`, script vẫn chạy thành công) với **lỗi thực thi** (exit khác 0).

## Viết báo cáo

1. Đọc template `references/report-template.md` trong thư mục skill này, tức `skills/csv-quality/references/report-template.md`.
2. Lấy mọi con số từ JSON của script. Điền đầy đủ các phần: tổng quan chất lượng, chi tiết lỗi, tổng hợp giờ làm & phân tích quá tải, danh sách người vượt ngưỡng, và các dòng bị loại khỏi tính giờ (`excluded_rows`).
3. Không sửa file CSV khi người dùng chỉ yêu cầu kiểm tra. Có thể đề xuất cách sửa trong mục khuyến nghị.
4. Ghi báo cáo bằng `write_file` vào đường dẫn người dùng yêu cầu (ví dụ `output/workload.md` hoặc `output/csv-quality.md`), rồi trả lời đường dẫn và tóm tắt ngắn.