# FocusStudy design system

Ngày 28/10/2026. Nguồn: 4 ảnh docs/design-references; UI UX Pro Max query education productivity calm dashboard (Flat Design phù hợp app; marketing Product Demo pattern không áp dụng); stack React focus/forms.

## Tokens và quyết định
- Ivory #faf8f4 nền; ink #101d2c; teal #075658 primary, white trên teal; mint #e2f1eb; terracotta #cf744e; vàng nhạt #fff0cd.
- Font hệ thống Segoe UI/Arial, có tiếng Việt, không phụ thuộc CDN. Heading 32–58px tùy viewport, body 16px, phụ 13px trở lên.
- Spacing 4/8/12/16/24/32/40, card radius 18px; control >=44px, viền #c5d1d3.
- Shell sidebar 240px desktop, nav cuộn ngang mobile. 375/768/1024/1440, grid minmax(0,1fr), không khóa zoom.
- Dashboard: hero mint + tài liệu teal + weekly/recent API + card vàng; ribbon CSS độc lập, aria-hidden. Không bìa mẫu giả, không thành tích minh họa.
- Button/Field/Pill/Modal ở components.jsx; loading/empty/error/status dùng ngữ nghĩa và chữ. Modal Escape, trap Tab và return focus. Toast không lấy focus.
- Focus-visible 3px teal, offset 3px. Reduced motion OS và localStorage, không tự mở camera.
- Modal/table/PDF co giãn, tên dài wrap, PDF có đường mở tab riêng.

## Kiểm tra
Build và test thực tế ghi docs/KET_QUA_KIEM_TRA.md. Chỉ đánh dấu browser viewport khi có bằng chứng; không dùng CSS review làm bằng chứng trình duyệt.
