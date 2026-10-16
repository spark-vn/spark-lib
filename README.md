# Spark Library

Thư viện tài liệu Lark dành cho doanh nghiệp Việt Nam, do Spark Technology (đối tác Platinum của Lark) tổng hợp và biên soạn.

## Cập nhật nội dung

Toàn bộ nội dung nằm trong `content.json`:

- `groups`: các chuyên mục. Mỗi nhóm có `id`, `name`, `nav` (tên ngắn trên menu), `lead`, `template` (`split` | `grid` | `dark`) và `docs` hoặc `subgroups` (tạo tab lọc).
- Mỗi tài liệu có `title`, `desc`, `kind` (`wiki` | `docx` | `base` | `file` | `slides` | `pdf` | `web`), `level`, `lang`, `minutes`, `topics`, `created` (YYYY-MM-DD) và `token` hoặc `url`.
- `keep_order: true` giữ đúng thứ tự trong file; nếu không, tài liệu được xếp mới nhất lên trước.
- `topics`: các nút lọc chủ đề ở đầu trang.

Sau khi sửa, chạy lại build:

```
python build.py
```

Script đọc `content.json` và ghi đè `index.html`.

## Cấu trúc

| File | Vai trò |
|------|---------|
| `index.html` | Trang tĩnh, GitHub Pages phục vụ file này |
| `content.json` | Toàn bộ nội dung: chuyên mục, tài liệu, chủ đề |
| `build.py` | Generator sinh `index.html` |
| `assets/` | Logo Spark, logo Lark Partner, icon Lark chính thức (được nhúng thẳng vào `index.html`) |

Trang là một file HTML duy nhất; chỉ font Be Vietnam Pro tải từ Google Fonts (mất mạng thì dùng font hệ thống).
