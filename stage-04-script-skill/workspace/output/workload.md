# Báo cáo chất lượng dữ liệu: `data/workload.csv`

Công cụ: `skills/csv-quality/scripts/check_csv.py` | exit code: 0 | Ngưỡng giờ tối đa: 8.0

## Tổng quan chất lượng dữ liệu

| Chỉ số | Giá trị |
|---|---|
| Tổng dòng dữ liệu (không tính header) | 6 |
| Dòng thiếu owner | 1 |
| Dòng hours không hợp lệ | 1 |
| Số task_id bị lặp (distinct) | 1 (['T02']) |

## Chi tiết vấn đề chất lượng

| Line | Cột | Loại lỗi | task_id | Mô tả |
|---|---|---|---|---|
| 5 | hours | invalid_hours | T04 | hours 'abc' không phải số hữu hạn không âm. |
| 6 | task_id | duplicate_id | T02 | task_id T02 đã xuất hiện ở line 3. |
| 7 | owner | missing_owner | T05 | owner trống. |

## Tổng hợp giờ làm việc và phân tích quá tải

- **Ngưỡng quá tải áp dụng:** 8.0 giờ

### Tổng giờ theo người phụ trách (chỉ tính dòng hợp lệ)
| Người phụ trách (Owner) | Tổng giờ ghi nhận | Trạng thái |
|---|---|---|
| Lan | 9.0 | Quá tải |
| Minh | 3.0 | Bình thường |

### Danh sách người vượt ngưỡng (8.0 giờ)
| Người phụ trách | Tổng giờ | Vượt quá |
|---|---|---|
| Lan | 9.0 | 1.0 giờ |

## Các dòng bị loại khỏi tính giờ (excluded_rows)

| Dòng (Line) | task_id | Danh sách mã lý do loại |
|---|---|---|
| 5 | T04 | ['invalid_hours'] |
| 6 | T02 | ['duplicate_id'] |
| 7 | T05 | ['missing_owner'] |

## Khuyến nghị

- **Dòng 5 (T04):** Bổ sung giá trị số giờ làm việc hợp lệ cho Minh thay cho chuỗi 'abc'.
- **Dòng 6 (T02):** Kiểm tra trùng lặp mã công việc `T02`. Nếu là công việc khác cần gán ID mới; nếu là công việc trùng thì giữ nguyên việc loại trừ.
- **Dòng 7 (T05):** Bổ sung người phụ trách (owner) cho mã công việc `T05`.
- **Điều phối nhân sự:** Lan đang có tổng 9.0 giờ làm việc (vượt 1.0 giờ so với ngưỡng 8.0 giờ). Khuyến nghị chuyển bớt 1.0 giờ công việc sang cho Minh (hiện mới phụ trách 3.0 giờ) để cân bằng khối lượng công việc trong đội ngũ.
