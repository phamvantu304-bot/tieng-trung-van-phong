# Ảnh nhân vật cho video hội thoại

Đặt ảnh vào thư mục này rồi chạy `python3 video/make_video.py` để làm lại `video/unit1.mp4 … unit16.mp4`.
Khi một người nói, video sẽ cắt sang ảnh của người đó, giống như trong phim.

- Ảnh **ngang 16:9** (ví dụ 1280×720). Định dạng .jpg, .png hoặc .webp. Ảnh sẽ được tự cắt vào giữa.
- Tên file phân biệt chữ hoa/thường và dấu tiếng Việt, cần đặt đúng như bảng dưới.

## Ảnh dùng chung (một ảnh cho mọi unit có nhân vật đó)

| Tên file | Nhân vật | Xuất hiện ở unit |
|---|---|---|
| `A_Vương.jpg` | Vương (vai A) | 1, 3, 5, 10 |
| `B_Minh.jpg` | Minh (vai B) | 1, 2, 3 |
| `A_Lý.jpg` | Lý (vai A) | 2 |
| `A_Lâm.jpg` | Lâm (vai A) | 4 |
| `B_Trần.jpg` | Trần (vai B) | 4, 10 |
| `B_Lý.jpg` | Lý (vai B) | 5 |
| `A_Vương Lan.jpg` | Vương Lan (vai A) | 6, 7, 8, 9, 11, 12, 13, 14, 15, 16 |
| `B_Trương.jpg` | Trương (vai B) | 6, 7, 8, 9, 11, 12, 13, 14, 15, 16 |

## Ảnh riêng từng unit (ưu tiên hơn ảnh dùng chung)

- `u6_A.jpg`, `u6_B.jpg`: người A / B trong unit 6
- `u6.jpg`: ảnh cảnh chung của unit 6, dùng khi không có ảnh người nói

Nếu không có ảnh nào, video dùng khung cảnh vẽ đơn giản với chữ họ của nhân vật.
