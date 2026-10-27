"""Render explanatory report figures. All coordinates are illustrative, not study data."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/evidence'
INK, TEAL, MINT, PAPER = '#243b32', '#176569', '#e2f1eb', '#faf8f4'

def font(size=30, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf', size)

def canvas(title, subtitle, height=1000):
    im = Image.new('RGB', (1600, height), PAPER)
    d = ImageDraw.Draw(im)
    d.text((60, 35), title, font=font(40, True), fill=TEAL)
    d.text((60, 96), subtitle, font=font(27), fill=INK)
    return im, d

def box(d, xy, title, lines):
    d.rounded_rectangle(xy, radius=20, fill=MINT, outline='#9bbcb2', width=2)
    x, y = xy[:2]
    d.text((x+25, y+18), title, font=font(32, True), fill=TEAL)
    for i, line in enumerate(lines):
        d.text((x+25, y+66+i*40), line, font=font(28), fill=INK)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im, d = canvas('Từ tín hiệu tới hỗ trợ: phân biệt các lớp', 'Sơ đồ khái niệm theo code; không phải kết quả đánh giá.', 1100)
    box(d, (60,160,1540,310), '1. Tín hiệu model', ['Head / gaze ước lượng + validity + thời điểm; không phải nhãn hành vi.'])
    box(d, (60,350,1540,500), '2. Sự kiện detector', ['Chuỗi tín hiệu + calibration + ngưỡng / thời gian → dấu hiệu.'])
    box(d, (60,540,1540,690), '3. Policy và lời nhắc', ['Ngữ cảnh, A/B, cooldown và ACK quyết định lời nhắc được hiển thị.'])
    box(d, (60,730,1540,880), '4. Phản hồi của người dùng', ['Notes / snooze / outside cung cấp ngữ cảnh; không tự train model.'])
    for y in (310,500,690):
        d.line((800,y+5,800,y+30), fill=TEAL, width=5)
    d.text((65,925), 'Nhãn tham chiếu: thu độc lập theo kịch bản / quan sát,', font=font(31, True), fill='#9a523c')
    d.text((65,975), 'dùng để đối chiếu detector; không suy ra từ chính ngưỡng đang đánh giá.', font=font(29), fill=INK)
    im.save(OUT/'guide-label-layers.png')

    im, d = canvas('Ba kiểu chuyển động đầu', 'Chỉ minh họa chuyển động; chưa xác nhận dấu dương / âm của pipeline.', 700)
    for i, (name, desc, hint) in enumerate([
        ('YAW', 'Quay trái / phải', 'Đầu quay quanh trục đứng'),
        ('PITCH', 'Cúi / ngẩng', 'Đầu quay quanh trục ngang'),
        ('ROLL', 'Nghiêng trái / phải', 'Đầu nghiêng về phía vai')]):
        x=60+i*510
        box(d,(x,175,x+480,620),name,[desc])
        cx=x+240
        if i==2:
            d.ellipse((cx-80,310,cx+55,475),outline=TEAL,width=6)
            d.line((cx-35,335,cx+20,450),fill=TEAL,width=5)
        else:
            d.ellipse((cx-70,310,cx+70,475),outline=TEAL,width=6)
            if i==0:
                d.line((cx-125,395,cx+125,395),fill='#9a523c',width=5)
                d.text((cx-130,390),'←',font=font(40),fill='#9a523c')
                d.text((cx+95,390),'→',font=font(40),fill='#9a523c')
            else:
                d.line((cx,290,cx,490),fill='#9a523c',width=5)
                d.text((cx+20,350),'↑  ↓',font=font(40),fill='#9a523c')
        d.text((x+22,550),hint,font=font(26),fill=INK)
    im.save(OUT/'guide-head-motion.png')

    im,d=canvas('Gaze: vùng góc tham chiếu minh họa', 'Ví dụ giả định; không phải pixel màn hình, dữ liệu thu hoặc độ chính xác.', 1000)
    def point(x,y): return (700+x*20,560-y*20)
    for x in range(-20,36,5):
        px,_=point(x,0);d.line((px,220,px,860),fill='#d8dfd8',width=1)
    for y in range(-15,16,5):
        _,py=point(0,y);d.line((300,py,1400,py),fill='#d8dfd8',width=1)
    a=point(-12,10);b=point(14,-8)
    d.rectangle((*a,*b),fill=MINT,outline=TEAL,width=5)
    d.line((300,560,1450,560),fill=INK,width=3);d.line((700,200,700,880),fill=INK,width=3)
    for x,y,label,col in [(0,0,'(0, 0): trong vùng',TEAL),(24,2,'(24, 2): ngoài vùng','#a34b37')]:
        px,py=point(x,y);d.ellipse((px-9,py-9,px+9,py+9),fill=col)
        d.text((px+15,py+14),label,font=font(27,True),fill=col)
    d.text((300,165),'pitch (độ, field code)',font=font(29),fill=INK)
    d.text((1100,900),'yaw (độ, field code)',font=font(29),fill=INK)
    d.text((350,330),'yaw trong [-12, 14]',font=font(30,True),fill=TEAL)
    d.text((350,375),'pitch trong [-8, 10]',font=font(30,True),fill=TEAL)
    d.text((65,945),'Chưa gán phía vật lý cho dấu trục; cần kiểm mapping và điểm nhìn độc lập.',font=font(28),fill=INK)
    im.save(OUT/'guide-gaze-region.png')

    im,d=canvas('Lộ trình của nhóm: qua từng cổng kiểm chứng', 'Kế hoạch đề xuất. Các cổng sau chưa được coi là đã nghiệm thu.', 1460)
    stages=[('G0 · Chạy lại được','Setup, hợp đồng dữ liệu, version và bằng chứng nền.'),
            ('G1 · Hiểu đúng tín hiệu','Xác minh head / gaze: tensor, trục, dấu và đơn vị.'),
            ('G2 · Hiệu chỉnh có kiểm độc lập','Điểm mới, tư thế mới; ghi cả lần thất bại.'),
            ('G3 · Luật và phục hồi đáng tin','Fusion / policy / offline / timer có replay và test lỗi.'),
            ('G4 · Pilot rồi đóng băng cấu hình','Chọn tham số có căn cứ; tách người / dữ liệu đánh giá.'),
            ('G5 · Đánh giá và bàn giao','Đối chiếu nhãn độc lập, UX, giới hạn và báo cáo đầy đủ.')]
    for i,(title,detail) in enumerate(stages):
        y=170+i*205;box(d,(60,y,1540,y+160),title,[detail])
        if i<5:d.line((800,y+163,800,y+196),fill=TEAL,width=5)
    im.save(OUT/'guide-team-roadmap.png')
    print('4 explanatory figures generated; no measured data or model execution.')

if __name__=='__main__':
    main()
