# Báo cáo chất lượng dữ liệu: `{đường dẫn CSV}`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: {exit_code} | Ngưỡng giờ tối đa: {max_hours}

## Tổng quan chất lượng dữ liệu

| Chỉ số | Giá trị |
|---|---|
| Tổng dòng dữ liệu (không tính header) | {row_count} |
| Dòng thiếu owner | {missing_owner_count} |
| Dòng hours không hợp lệ | {invalid_hours_count} |
| Số task_id bị lặp (distinct) | {duplicate_id_count} ({duplicate_ids}) |

## Chi tiết vấn đề chất lượng

| Line | Cột | Loại lỗi | task_id | Mô tả |
|---|---|---|---|---|
| {line} | {column} | {type} | {task_id} | {message} |

*(Nếu không có vấn đề nào, ghi: "Không phát hiện lỗi dữ liệu.")*

## Tổng hợp giờ làm việc và phân tích quá tải

- **Ngưỡng quá tải áp dụng:** {max_hours} giờ

### Tổng giờ theo người phụ trách (chỉ tính dòng hợp lệ)
| Người phụ trách (Owner) | Tổng giờ ghi nhận | Trạng thái |
|---|---|---|
| {owner} | {total_hours} | {Bình thường / Quá tải} |

*(Nếu không có owner nào có dòng hợp lệ, ghi: "Không có dữ liệu giờ hợp lệ.")*

### Danh sách người vượt ngưỡng ({max_hours} giờ)
| Người phụ trách | Tổng giờ | Vượt quá |
|---|---|---|
| {owner} | {total_hours} | {total_hours - max_hours} giờ |

*(Nếu không có ai vượt ngưỡng, ghi: "Không có ai bị quá tải.")*

## Các dòng bị loại khỏi tính giờ (excluded_rows)

| Dòng (Line) | task_id | Danh sách mã lý do loại |
|---|---|---|
| {line} | {task_id} | {reasons} |

*(Nếu không có dòng nào bị loại, ghi: "Không có dòng nào bị loại.")*

## Khuyến nghị

- {Cách sửa chi tiết cho từng dòng bị loại hoặc lỗi dữ liệu; tuyệt đối không tự ý sửa file nguồn}
- {Khuyến nghị điều phối lại khối lượng công việc cho các cá nhân bị quá tải}