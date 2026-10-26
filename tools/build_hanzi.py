#!/usr/bin/env python3
"""Tạo hanzi.json: phân tích bộ thủ + âm Hán Việt + mẹo nhớ cho các chữ trong 16 bài.

Cấu tạo chữ lấy từ Make Me a Hanzi (github.com/skishore/makemeahanzi, dictionary.txt);
âm Hán Việt, nghĩa bộ thủ và mẹo nhớ tiếng Việt soạn tay ở dưới.

Chạy: python3 tools/build_hanzi.py words.json
  (words.json: danh sách từ của app — ALLW [{u, w:[hanzi, pinyin, nghĩa]}] hoặc [[hanzi, pinyin, nghĩa], ...];
   bỏ trống thì lấy từ video/words.json)
"""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MMAH_URL = "https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt"

# chữ|Hán Việt|nghĩa ngắn  (chữ trong bài và các thành phần ghép chữ)
HV = """
一|nhất|một
三|tam|ba
上|thượng|trên
不|bất|không
专|chuyên|chuyên
业|nghiệp|nghề, sự nghiệp
丢|đâu|đánh mất
主|chủ|chủ
书|thư|sách, viết
争|tranh|tranh giành
事|sự|việc
交|giao|giao, trao
产|sản|sinh ra
人|nhân|người
仓|thương|kho
付|phó|trả, giao
代|đại|thay, đời
件|kiện|món, kiện
价|giá|giá
任|nhiệm|gánh vác
企|xí|kiễng chân, mong
优|ưu|ưu tú
会|hội|họp, biết
位|vị|chỗ, vị trí
低|đê|thấp
作|tác|làm
保|bảo|giữ
信|tín|tin, thư
修|tu|sửa
假|giả|giả, nghỉ
做|tố|làm
偿|thường|đền bù
入|nhập|vào
全|toàn|trọn vẹn
公|công|chung
关|quan|cửa ải, liên quan
写|tả|viết
决|quyết|quyết
准|chuẩn|chuẩn
出|xuất|ra
分|phân|chia
划|hoạch|vạch
判|phán|phán đoán
利|lợi|lợi
到|đáo|đến
制|chế|chế tạo
前|tiền|trước
力|lực|sức
功|công|công lao
加|gia|thêm
务|vụ|việc
动|động|động
劳|lao|nhọc
势|thế|thế
包|bao|bọc
化|hóa|biến đổi
协|hiệp|hợp sức
单|đơn|đơn
占|chiếm|chiếm
厂|xưởng|nhà xưởng
历|lịch|trải qua
原|nguyên|gốc
参|tham|tham gia
双|song|đôi
反|phản|ngược
发|phát|phát ra
取|thủ|lấy
受|thụ|nhận
口|khẩu|miệng
司|ty|coi sóc
各|các|mỗi
合|hợp|hợp
同|đồng|cùng
名|danh|tên
后|hậu|sau
告|cáo|báo
员|viên|người làm
品|phẩm|phẩm, hàng
唛|mạch|nhãn hiệu (mark)
售|thụ|bán
商|thương|buôn bán
器|khí|đồ dùng
回|hồi|về
因|nhân|nguyên nhân
地|địa|đất
场|trường|bãi, nơi
坏|hoại|hỏng
培|bồi|vun đắp
填|điền|lấp, điền
处|xử|xử lý, nơi
备|bị|chuẩn bị
失|thất|mất
头|đầu|đầu
子|tử|con
字|tự|chữ
守|thủ|giữ
安|an|yên
完|hoàn|xong
定|định|định
客|khách|khách
家|gia|nhà
寸|thốn|tấc, bàn tay
少|thiểu|ít
尺|xích|thước
展|triển|mở rộng
岗|cương|trạm gác, vị trí
岸|ngạn|bờ
工|công|thợ, việc
币|tệ|tiền
市|thị|chợ
帽|mạo|mũ
广|quảng|rộng, mái nhà
序|tự|thứ tự
库|khố|kho
应|ứng|ứng, nên
度|độ|mức độ
延|diên|kéo dài
建|kiến|xây
开|khai|mở
式|thức|kiểu
录|lục|ghi chép
形|hình|hình
待|đãi|đợi, đối đãi
律|luật|luật
心|tâm|tim, lòng
快|khoái|nhanh
态|thái|thái độ
性|tính|tính
怨|oán|oán trách
总|tổng|tổng
惠|huệ|ơn, ưu đãi
意|ý|ý
成|thành|thành
截|tiệt|cắt
户|hộ|cửa, hộ
手|thủ|tay
扣|khấu|khấu trừ
技|kỹ|kỹ năng
投|đầu|ném
折|chiết|bẻ gãy
护|hộ|che chở
报|báo|báo
抱|bão|ôm
抽|trừu|rút
拒|cự|chống lại
招|chiêu|vẫy gọi
括|quát|bao gồm
持|trì|cầm giữ
损|tổn|tổn hại
换|hoán|đổi
据|cứ|căn cứ
排|bài|xếp
接|tiếp|đón, nối
控|khống|khống chế
推|thôi|đẩy
提|đề|nhấc, nêu
支|chi|chống đỡ
改|cải|sửa
效|hiệu|hiệu quả
教|giáo|dạy
数|số|số
文|văn|văn
料|liệu|vật liệu
方|phương|phương
日|nhật|mặt trời
时|thời|thời gian
明|minh|sáng
有|hữu|có
服|phục|áo, phục vụ
期|kỳ|kỳ hạn
本|bản|gốc
术|thuật|thuật
机|cơ|máy
材|tài|vật liệu
条|điều|cành, điều
查|tra|tra xét
标|tiêu|mốc, chuẩn
样|dạng|mẫu
格|cách|ô, cách
案|án|phương án
检|kiểm|kiểm tra
模|mô|khuôn
次|thứ|lần
款|khoản|khoản tiền
歉|khiểm|áy náy
止|chỉ|dừng
步|bộ|bước
比|tỷ|so sánh
毕|tất|xong
民|dân|dân
求|cầu|cầu xin
法|pháp|phép, luật
海|hải|biển
消|tiêu|tan biến
润|nhuận|ướt, lợi
涨|trướng|dâng lên
清|thanh|trong
港|cảng|cảng
满|mãn|đầy
火|hỏa|lửa
点|điểm|chấm, điểm
照|chiếu|chiếu
片|phiến|tấm
牌|bài|tấm biển
物|vật|vật
特|đặc|đặc biệt
率|suất|tỷ lệ
现|hiện|hiện
班|ban|ca, lớp
理|lý|lý
生|sinh|sinh
用|dụng|dùng
申|thân|trình bày
益|ích|ích
盒|hạp|hộp
盖|cái|nắp, che
盘|bàn|mâm
目|mục|mắt
知|tri|biết
短|đoản|ngắn
码|mã|mã số
确|xác|chắc chắn
礼|lễ|lễ
票|phiếu|phiếu
离|ly|rời
秘|bí|bí mật
积|tích|tích lũy
程|trình|trình tự
税|thuế|thuế
稿|cảo|bản thảo
空|không|trống
立|lập|đứng
站|trạm|trạm
竞|cạnh|tranh đua
章|chương|chương, con dấu
签|thiêm|ký
简|giản|đơn giản
管|quản|ống, quản lý
箱|tương|hòm, thùng
系|hệ|hệ, buộc
索|sách|dây, đòi
纠|củ|rối, sửa
约|ước|hẹn
纷|phân|rối ren
纸|chỉ|giấy
线|tuyến|sợi, tuyến
经|kinh|trải qua
结|kết|thắt, kết
绝|tuyệt|dứt
统|thống|thống nhất
续|tục|nối tiếp
维|duy|giữ gìn
缺|khuyết|thiếu
考|khảo|xét, thi
耽|đam|chậm trễ
职|chức|chức
联|liên|liên kết
聘|sính|mời, tuyển
能|năng|có thể
自|tự|tự mình
航|hàng|đi thuyền
舱|khoang|khoang
船|thuyền|thuyền
色|sắc|màu
营|doanh|doanh trại, kinh doanh
薪|tân|củi, lương
虑|lự|lo
表|biểu|bên ngoài, bảng
装|trang|lắp, đóng
裹|khỏa|bọc
见|kiến|thấy
观|quan|xem
规|quy|quy tắc
解|giải|cởi, giải
言|ngôn|lời nói
计|kế|tính
订|đính|đặt
认|nhận|nhận biết
讨|thảo|bàn, đòi
让|nhượng|nhường
训|huấn|dạy
议|nghị|bàn
记|ký|ghi
论|luận|bàn luận
设|thiết|đặt ra
访|phỏng|thăm hỏi
证|chứng|chứng
诉|tố|kể, kiện
试|thí|thử
询|tuân|hỏi
误|ngộ|lầm
请|thỉnh|mời
调|điều|điều chỉnh
谅|lượng|thông cảm
谈|đàm|nói chuyện
负|phụ|gánh
财|tài|của cải
责|trách|trách nhiệm
货|hóa|hàng
质|chất|chất
购|cấu|mua
贴|thiếp|dán, phụ cấp
费|phí|phí
资|tư|vốn
赔|bồi|đền
赖|lại|dựa vào
起|khởi|dậy
跟|cân|gót, theo
路|lộ|đường
踪|tung|dấu vết
车|xa|xe
轮|luân|bánh xe
达|đạt|đạt tới
运|vận|chở
还|hoàn|trả, còn
进|tiến|tiến
违|vi|trái
迟|trì|muộn
退|thoái|lui
适|thích|vừa
递|đệ|chuyển
途|đồ|đường
通|thông|thông
遇|ngộ|gặp
道|đạo|đường
遵|tuân|theo
部|bộ|bộ phận
量|lượng|lượng
金|kim|vàng, kim loại
销|tiêu|bán ra
长|trường|dài
门|môn|cửa
问|vấn|hỏi
间|gian|khoảng
陆|lục|đất liền
降|giáng|hạ xuống
限|hạn|giới hạn
险|hiểm|hiểm
集|tập|tụ lại
面|diện|mặt
顾|cố|ngoảnh nhìn, chăm sóc
预|dự|trước
题|đề|đề
颜|nhan|mặt, màu
风|phong|gió
馈|quỹ|biếu tặng
验|nghiệm|kiểm nghiệm
高|cao|cao
⺀|chấm|hai chấm
⺈|đao (dạng 𠂊)|người cúi, tay
⺊|bốc|bói
⺍|tiểu|nhỏ
⺮|trúc|tre
⺼|nhục|thịt
㔾|tiết|người quỳ
㢟|dẫn|bước đi
丁|đinh|cái đinh, người
丂|khảo|hơi thở
七|thất|bảy
丄|thượng|trên
与|dữ|và, cho
两|lưỡng|hai
丨|cổn|nét sổ
丩|củ|quấn
丶|chủ|chấm
丷|bát|tách ra
丿|phiệt|nét phẩy
乂|nghệ|bắt chéo
义|nghĩa|nghĩa
乍|sạ|chợt, mới
乚|ất|nét móc
也|dã|cũng
亅|quyết|nét móc
了|liễu|xong
予|dư|cho
二|nhị|hai
云|vân|mây, nói
井|tỉnh|giếng
亠|đầu|nắp, mái
亢|kháng|cao
京|kinh|kinh đô
亻|nhân đứng|người
亼|tập|gom lại
介|giới|ở giữa
仑|luân|thứ tự
余|dư|thừa
佥|thiêm|đều, cùng
儿|nhân đi|người, chân
元|nguyên|đầu, đầu tiên
兄|huynh|anh
充|sung|đầy
兑|đoái|đổi
八|bát|tám, chia
六|lục|sáu
其|kỳ|ấy
兼|kiêm|gồm
冂|quynh|khung, vùng biên
冈|cương|sườn núi
冋|quynh|khung
冏|quýnh|cửa sổ sáng
冒|mạo|đội, liều
冖|mịch|trùm, che
冘|dâm|đi chậm
冫|băng|nước đá
几|kỷ|cái bàn nhỏ
凡|phàm|mọi
凵|khảm|hố, đồ đựng
凶|hung|dữ
击|kích|đánh
刀|đao|dao
刂|đao đứng|dao
刖|ngoạt|chặt
剌|lạt|trái ngược
办|biện|làm
勹|bao|bọc
勺|chước|cái muôi
勾|câu|móc
勿|vật|chớ
匕|chủy|cái thìa
十|thập|mười
半|bán|nửa
卑|ti|thấp
卖|mại|bán
卜|bốc|bói
卩|tiết|người quỳ
厄|ách|khó khăn
厶|tư|riêng tư
去|khứ|đi
又|hựu|bàn tay, lại
叚|giả|mượn
只|chỉ|chỉ
召|triệu|gọi
吉|cát|tốt lành
吕|lữ|xương sống, phòng nối nhau
吴|ngô|nước Ngô
呆|ngốc|ngây
呈|trình|dâng
周|chu|vòng, chu đáo
咅|phẫu|(gợi âm)
囗|vi|vây quanh
土|thổ|đất
士|sĩ|kẻ sĩ
壬|nhâm|gánh
壮|tráng|khỏe
夂|tri|bước chậm
夅|giáng|bước xuống
夕|tịch|chiều tối
夗|uyển|nằm cuộn
大|đại|to, người dang tay
天|thiên|trời
太|thái|rất
夫|phu|đàn ông
夬|quái|quyết, dứt
奂|hoán|lộng lẫy
女|nữ|phụ nữ
妾|thiếp|nàng hầu
娄|lâu|(gợi âm)
孝|hiếu|hiếu thảo
宀|miên|mái nhà
宗|tông|tổ tiên
官|quan|quan
寺|tự|chùa, sân triều
尊|tôn|tôn kính
小|tiểu|nhỏ
尝|thường|nếm
尤|vưu|càng
尸|thi|thân người
居|cư|ở
屮|triệt|mầm cây
山|sơn|núi
川|xuyên|sông
巨|cự|lớn
己|kỷ|bản thân
巳|tị|thai nhi
巴|ba|mong
巷|hạng|ngõ
巾|cân|khăn
干|can|khô, cái khiên
幺|yêu|sợi tơ nhỏ
廴|dẫn|bước dài
廾|củng|hai tay chắp
廿|nhập|hai mươi
弋|dặc|cọc, tên buộc dây
弗|phất|không
弟|đệ|em trai
张|trương|giương
彐|kệ|bàn tay
彡|sam|lông, tia sáng
彦|ngạn|người tài
彳|xích|bước chân
忄|tâm đứng|lòng
必|tất|tất phải
戈|qua|giáo mác
戋|tiên|nhỏ
扌|thủ|tay
才|tài|tài
执|chấp|cầm
攵|phộc|tay cầm roi
攸|du|(gợi âm)
故|cố|cũ, vì thế
斗|đấu|cái đấu
斤|cân|cái rìu
斥|xích|mắng
新|tân|mới
旦|đán|buổi sáng
旬|tuần|mười ngày
昭|chiêu|sáng tỏ
是|thị|là, đúng
月|nguyệt|trăng, thịt
木|mộc|cây
果|quả|quả
欠|khiếm|há miệng, thiếu
正|chính|ngay thẳng
殳|thù|cây gậy
每|mỗi|mỗi
毛|mao|lông
氏|thị|họ
氐|đê|gốc
水|thủy|nước
氵|thủy|nước
氺|thủy|nước
泉|tuyền|suối
灬|hỏa|lửa
炎|viêm|nóng
爫|trảo|móng, bàn tay
牛|ngưu|trâu bò
犬|khuyển|chó
玉|ngọc|ngọc
王|vương|vua, ngọc
甬|dũng|lối đi
田|điền|ruộng
由|do|do
甹|sính|(gợi âm)
疋|sơ|bàn chân
皿|mãnh|bát đĩa
相|tương|nhau, xem
真|chân|thật
矢|thỉ|mũi tên
石|thạch|đá
示|thị|bàn thờ, chỉ cho thấy
礻|thị|thần, lễ
禸|nhựu|vết chân thú
禺|ngu|(gợi âm)
禾|hòa|lúa
穴|huyệt|hang
米|mễ|gạo
糸|mịch|sợi tơ
纟|mịch|sợi tơ
缶|phẫu|đồ gốm
羊|dương|dê
耂|lão|già
耳|nhĩ|tai
聿|duật|cây bút
肖|tiếu|giống
至|chí|đến
舌|thiệt|lưỡi
舟|chu|thuyền
艮|cấn|cứng, dừng
艹|thảo|cỏ
莫|mạc|chớ
虍|hô|vằn hổ
衣|y|áo
覀|á|che, đậy
角|giác|sừng
讠|ngôn|lời nói
豆|đậu|hạt đậu
豕|thỉ|lợn
贝|bối|vỏ sò, tiền
贵|quý|đắt, quý
走|tẩu|chạy
足|túc|chân
辶|sước|đi
里|lý|làng, dặm
钅|kim|kim loại
闰|nhuận|nhuận
阝|phụ|gò đất
隹|chuy|chim
青|thanh|xanh
非|phi|không phải
韦|vi|da thuộc
音|âm|âm thanh
页|hiệt|đầu
饣|thực|ăn
首|thủ|đầu
马|mã|ngựa
麦|mạch|lúa mạch
龶|sinh|(biến thể của 生)
厤|lịch|lịch
昜|dương|mặt trời lên
票|phiếu|phiếu
㒼|man|(gợi âm)
般|ban|loại, kiểu
章|chương|chương
叀|chuyên|(gợi âm)
东|đông|phía đông
中|trung|giữa
值|trị|giá trị
停|đình|dừng
具|cụ|đồ dùng
别|biệt|khác, riêng
匙|thi|cái thìa
区|khu|khu vực
升|thăng|lên cao
卡|tạp|thẻ
向|hướng|hướng
型|hình|khuôn, kiểu
墅|thự|nhà ở ngoại ô
契|khế|khế ước
套|sáo|bộ, căn
寓|ngụ|nơi ở
层|tầng|tầng
师|sư|thầy
房|phòng|nhà, phòng
押|áp|cầm cố, đặt cọc
施|thi|thi hành
朝|triều|hướng về
权|quyền|quyền
楼|lâu|tòa nhà, lầu
段|đoạn|đoạn
电|điện|điện
看|khán|xem
砍|khảm|chặt
禁|cấm|cấm
租|tô|thuê
行|hành|đi; hàng (ngân hàng)
贷|thải|cho vay
过|quá|qua
配|phối|phối, kèm
钥|thược|chìa khóa
银|ngân|bạc
项|hạng|hạng mục
㐌|dã|(biến thể của 也)
且|thả|vả lại, đều đặn
丰|phong|vạch khắc
亍|xúc|bước chân phải
亭|đình|cái đình
刑|hình|hình phạt
匸|hễ|che chắn
另|lánh|khác
帀|táp|vòng quanh
曰|viết|nói
林|lâm|rừng
甲|giáp|áo giáp
直|trực|thẳng
酉|dậu|bình rượu
野|dã|đồng nội
镸|trường|dài
龺|triêu|mặt trời mọc giữa cỏ
雚|quán|(gợi âm)
咼|oa|(gợi âm)
"""

# Mẹo nhớ cho chữ hội ý / tượng hình (chữ hình thanh có mẹo tự sinh: bộ chỉ nghĩa + phần gợi âm)
STORY = """
一|Một nét ngang = số một.
三|Ba nét ngang = số ba.
上|Nét ngắn nằm TRÊN nét ngang dài → ở trên.
不|Con chim bay vút lên trời 一 mà không tới được → không.
专|Ống chỉ quay đều một chiều → chuyên tâm một việc.
业|Giá treo chuông khánh vững chắc → nghề nghiệp, sự nghiệp.
丢|Viên ngọc 王 của riêng mình 厶 bị rơi → đánh mất.
主|Ngọn lửa 丶 trên cây đèn 王, người giữ đèn là chủ nhà → chủ.
书|Nét bút vạch lên trang giấy → viết, sách.
争|Hai bàn tay ⺈ 彐 giằng co một cây gậy 亅 → tranh giành.
事|Bàn tay 彐 cầm thẻ tre 亅 ghi chép công việc → việc.
交|Người bắt chéo chân 乂 → giao nhau, trao đổi.
产|Dưới mái 亠 nhà xưởng 厂 sinh ra hàng hóa → sản xuất (đọc gần 厂 chǎng).
人|Hình người đang bước, hai chân dang ra.
仓|Người 人 cất lương thực vào chỗ kín 㔾 → kho.
付|Người 亻 dùng tay 寸 trao vật → trả, giao.
代|Người 亻 bị buộc vào cọc thời gian 弋, đời này thay đời khác → thay thế, thời đại.
件|Người 亻 xẻ con bò 牛 thành từng phần → từng món, từng kiện.
企|Người 人 kiễng chân 止 nhìn xa → mong mỏi (xí nghiệp phải nhìn xa).
会|Mọi người 人 tụ lại nói chuyện 云 → họp, hội.
位|Chỗ người 亻 đứng 立 → vị trí.
作|Người 亻 bắt đầu 乍 làm ra thứ gì → làm (tác).
信|Người 亻 nói lời 言 thì phải giữ → tin, uy tín.
假|Người 亻 mượn 叚 danh người khác → giả.
做|Người 亻 làm cho việc xảy ra 故 → làm.
入|Mũi tên chỉ vào trong → vào.
全|Ngọc 玉 được cất vào 入 cẩn thận → nguyên vẹn, toàn bộ.
公|Chia 八 cái riêng 厶 ra cho mọi người → chung, công.
关|Then cài ngang qua cánh cửa → đóng, cửa ải, liên quan (khép vào nhau).
写|Dưới mái che 冖 viết thư cho 与 người khác → viết.
决|Băng 冫 vỡ, nước phá 夬 bờ → quyết, dứt khoát.
出|Mầm 屮 mọc ra khỏi chậu 凵 → ra.
分|Dao 刀 cắt vật tách 八 làm đôi → chia.
划|Cầm giáo 戈 và dao 刂 vạch đường → vạch ra, kế hoạch.
利|Dao 刂 gặt lúa 禾 → có lợi.
前|Cắt 刖 bụi rậm mở lối đi phía trước → trước.
力|Hình lưỡi cày đâm xuống đất → sức lực.
功|Làm việc 工 bằng sức 力 → công lao.
加|Dùng sức 力 và lời nói 口 cổ vũ → thêm vào.
务|Bước đi 夂 dùng sức 力 làm việc → nhiệm vụ.
动|Dùng sức 力 đẩy như mây 云 trôi → chuyển động.
劳|Dùng sức 力 gánh bó cỏ 艹 dưới mái 冖 → lao động, vất vả.
包|Bọc 勹 em bé 巳 trong tã → gói, bao.
化|Người đứng 亻 rồi người ngã 匕 → biến đổi.
单|Cây ná một chạc → đơn, một.
占|Nói 口 điều xem bói 卜 → chiêm; chiếm chỗ.
厂|Mái che dựa vách núi → nhà xưởng.
参|Người 大 đội ba vì sao 厶 lấp lánh 彡 (chòm sao Sâm) → tham gia.
双|Hai bàn tay 又 又 → một đôi.
反|Bàn tay 又 đẩy vào vách núi 厂 → ngược lại, phản.
发|Bàn tay 又 giương cung bắn → phát ra.
取|Tay 又 cắt lấy tai 耳 (chiến lợi phẩm xưa) → lấy.
受|Tay trên 爫 trao, tay dưới 又 nhận vật 冖 → nhận.
口|Hình cái miệng mở.
司|Người giơ tay ra lệnh bằng miệng 口 → coi sóc, quản lý (công ty).
各|Bước đi 夂 + miệng 口: mỗi người đi một ngả → các, mỗi.
合|Nắp 亼 đậy khít miệng 口 → hợp.
同|Mọi người 凡 nói cùng một miệng 口 → cùng, giống nhau.
名|Trời tối 夕 không thấy mặt, phải gọi tên 口 → tên.
后|Người đứng sau ra lệnh bằng miệng 口 → sau.
告|Con bò 牛 rống to bằng miệng 口 → báo cho biết.
员|Miệng 口 ăn nhờ tiền 贝 lương → nhân viên.
品|Ba cái miệng 口 bàn tán → hàng hóa, phẩm chất.
售|Người bán rao như chim 隹 hót bằng miệng 口 → bán.
器|Bốn đồ đựng 口 có chó 犬 canh giữ → đồ dùng, máy móc.
回|Vòng trong vòng ngoài xoáy lại → quay về.
因|Người 大 nằm trên chiếu 囗 → dựa vào, nguyên nhân.
处|Đi 夂 tới rồi cắm cờ 卜 → nơi chốn, xử lý.
备|Đi 夂 ra ruộng 田 chuẩn bị mùa vụ → chuẩn bị.
失|Vật rơi 丿 khỏi tay 夫 → mất.
头|Người 大 với chỏm tóc ⺀ → đầu.
子|Em bé quấn tã, dang hai tay.
字|Con 子 dưới mái nhà 宀 học chữ → chữ.
守|Bàn tay 寸 giữ đồ dưới mái nhà 宀 → giữ, canh.
安|Người phụ nữ 女 ở trong nhà 宀 → yên ổn.
定|Bàn chân 疋 dừng lại dưới mái nhà 宀 → ổn định, quyết định.
客|Mỗi người 各 đến dưới mái nhà 宀 → khách.
寸|Bàn tay với chấm chỉ chỗ bắt mạch → tấc.
少|Nhỏ 小 lại bớt đi một nét 丿 → ít.
尺|Người 尸 dang bước chân 乚 đo đất → thước.
展|Trải áo 衣 ra bày 尸 → mở rộng, triển lãm.
岸|Vách đá 厂 cạnh núi 山, 干 gợi âm → bờ.
工|Hình cây thước thợ → thợ, công việc.
币|Tiền xưa làm bằng lụa 巾 → tiền tệ.
市|Nơi treo khăn 巾 làm biển hàng → chợ.
广|Mái nhà 厂 có nóc 丶 → nhà rộng.
库|Nhà 广 để xe 车 → kho.
应|Dưới mái 广 có người đáp ⺍ lời → ứng đáp, nên làm.
度|Hai mươi 廿 người giơ tay 又 bàn bạc trong nhà 广 → mức độ.
延|Bước chân 㢟 bị kéo dài thêm 丿 → kéo dài, hoãn.
开|Hai tay 廾 nhấc then cửa 一 → mở.
式|Thợ dùng cọc 弋 và thước 工 → kiểu mẫu, cách thức.
录|Cây bút 彐 chấm nước 氺 ghi chép → ghi lại.
形|Tia sáng 彡 qua khung cửa 开 tạo hình → hình dáng.
待|Bước 彳 đến sân triều 寺 chờ đợi → đợi, đối đãi.
律|Bước 彳 theo điều viết bằng bút 聿 → luật.
心|Hình trái tim.
快|Lòng 忄 quyết 夬 → nhanh, vui.
总|Nhiều miệng 口 cùng một lòng 心 → tổng.
成|Cầm giáo 戈 dựng nghiệp 丁 → thành.
截|Giáo 戈 chặn đứng con chim 隹 → cắt đứt.
户|Hình một cánh cửa → cửa, hộ.
手|Hình bàn tay xòe ngón.
折|Tay 扌 cầm rìu 斤 chặt → bẻ gãy, chiết khấu.
护|Tay 扌 che chở cửa nhà 户 → bảo vệ.
报|Tay 扌 bắt kẻ phạm tội 卩 又 → báo (báo án).
抱|Tay 扌 bao 包 lấy → ôm.
招|Tay 扌 vẫy gọi 召 → chiêu mộ, tuyển.
支|Tay 又 cầm cành cây 十 chống → chống đỡ, chi trả.
改|Cầm roi 攵 dạy đứa trẻ 己 sửa lỗi → sửa đổi.
文|Hình hoa văn xăm trên ngực → văn.
料|Dùng đấu 斗 đong gạo 米 → nguyên liệu.
方|Hình lá cờ chỉ hướng → phương.
日|Hình mặt trời.
时|Mặt trời 日 + tấc 寸: đo từng tấc bóng nắng → thời gian.
明|Mặt trời 日 + mặt trăng 月 → sáng.
有|Tay cầm miếng thịt 月 → có.
服|Người 卩 dùng tay 又 khoác áo 月 → quần áo, phục.
本|Cây 木 có nét đánh dấu ở gốc → gốc.
术|Cây 木 thêm chấm 丶: nghề trồng cây → kỹ thuật.
机|Cái bàn 几 bằng gỗ 木 → máy (cơ).
条|Bước 夂 theo cành cây 木 dài → cành, điều khoản.
查|Cây 木 + buổi sáng 旦: sáng nào cũng đi xem từng cây → tra xét.
次|Người há miệng 欠 ngáp thêm lần nữa 冫 → lần, thứ.
款|Lễ vật 士 示 dâng lên khi còn thiếu 欠 → khoản tiền.
止|Hình bàn chân → dừng.
步|Bàn chân 止 nối bàn chân → bước.
比|Hai cái thìa 匕 đặt cạnh nhau → so sánh.
民|Mắt bị giáo 戈 đâm (dấu nô lệ xưa) → dân thường.
求|Áo lông 氺 ai cũng muốn có → cầu xin.
法|Nước 氵 chảy 去 phẳng như nhau → phép, luật.
火|Hình ngọn lửa.
片|Nửa thân cây bổ đôi → tấm, mảnh.
率|Sợi dây 幺 rung trong nhạc cụ đều nhịp → tỷ lệ, suất.
现|Ngọc 王 lộ ra cho thấy 见 → hiện.
班|Dao 刂 chia ngọc 王 làm hai → ca, lớp.
生|Mầm cây mọc từ đất 土 → sinh.
用|Hình cái thùng gỗ dùng hằng ngày → dùng.
申|Hình tia chớp duỗi ra → trình bày.
益|Nước 水 tràn đầy chén 皿 → có ích.
盖|Cái đĩa 皿 có nắp đậy 羊 → nắp, che.
目|Hình con mắt dựng đứng.
票|Lửa 覀 trên bàn thờ 示 đốt tờ giấy → phiếu, vé.
离|Con thú 禸 bỏ chạy, chỉ còn vết chân → rời xa.
税|Lúa 禾 nộp đổi 兑 cho nhà nước → thuế.
立|Người đứng trên mặt đất 一 → đứng.
竞|Đứng 立 đối đầu người anh 兄 → tranh đua.
章|Mười 十 đoạn nhạc 音 → chương.
系|Nét 丿 buộc vào sợi tơ 糸 → buộc, hệ thống.
索|Sợi dây 糸 treo dưới mái 冖 → dây, đòi hỏi.
纠|Quấn 丩 các sợi tơ 纟 → rối; gỡ rối, sửa sai.
约|Sợi dây 纟 buộc cái muôi 勺 → ràng buộc, hẹn ước.
能|Đầu 厶, thân 月, móng vuốt 匕 匕 của con gấu khỏe → có năng lực.
自|Hình cái mũi (người Trung Quốc chỉ vào mũi khi nói "tôi") → tự mình.
舱|Cái kho 仓 trên thuyền 舟 → khoang.
船|Thuyền 舟 chở người 几 và hàng 口 → thuyền.
色|Người ⺈ ngắm 巴 → sắc, màu.
营|Mái 冖 phủ cỏ 艹 với các phòng nối nhau 吕 → doanh trại, kinh doanh.
薪|Cỏ cây 艹 mới 新 chặt → củi; tiền công.
虑|Hổ 虍 khiến lòng 心 lo → lo lắng.
表|Áo 衣 lông 毛 mặc bên ngoài → bên ngoài, biểu hiện.
见|Người 儿 với con mắt to → thấy.
观|Lại 又 nhìn 见 → xem, quan sát.
解|Dao 刀 cắt sừng 角 con trâu 牛 → cởi, giải.
言|Lưỡi thè ra khỏi miệng 口 → lời nói.
讨|Lời 讠 xin một chút 寸 → bàn, đòi.
记|Lời 讠 của chính mình 己 → ghi nhớ.
论|Lời 讠 có thứ tự 仑 → bàn luận.
证|Lời 讠 ngay thẳng 正 → chứng cứ.
诉|Lời 讠 trách mắng 斥 → kể tội, khiếu nại.
负|Người ⺈ cõng tiền 贝 → gánh (nợ).
责|Tiền 贝 phải trả → trách nhiệm.
车|Hình chiếc xe nhìn từ trên xuống.
还|Không 不 đi 辶 nữa mà quay lại → trả lại, vẫn còn.
遵|Đi 辶 theo người được tôn kính 尊 → tuân theo.
金|Hình cái chuông đúc → vàng, kim loại.
长|Cụ già tóc dài chống gậy → dài.
门|Hình hai cánh cửa → cửa.
间|Mặt trời 日 chiếu qua khe cửa 门 → khoảng giữa.
集|Chim 隹 đậu trên cây 木 → tụ lại.
面|Hình khuôn mặt → mặt.
风|Gió 几 cuốn qua 乂 → gió.
馈|Món ăn 饣 quý 贵 đem biếu → tặng, phản hồi.
高|Hình tòa lầu cao.
价|Người 亻 đứng giữa 介 hai bên mua bán → giá cả (介 jiè gợi âm).
低|Người 亻 cúi xuống tận gốc 氐 → thấp (氐 dī gợi âm).
历|Dùng sức 力 vượt qua bao sườn núi 厂 → trải qua (lịch sử, lý lịch).
商|Dưới mái 亠 cửa hàng sáng sủa 冏 người ta mặc cả 丷 → buôn bán.
场|Khoảng đất 土 rộng có nắng chiếu 勿 → bãi, nơi (trường).
惠|Tấm lòng 心 tốt với người khác → ơn huệ, ưu đãi.
标|Cây 木 cắm làm mốc chỉ cho thấy 示 → mốc, tiêu chuẩn.
满|Nước 氵 dâng ngập cả hai 两 bờ cỏ 艹 → đầy.
盘|Cái mâm 皿 to như con thuyền 舟 → mâm; kiểm kê hàng.
东|Mặt trời 日 mọc sau gốc cây 木 (chữ phồn thể 東) → phía đông.
中|Một nét 丨 xuyên qua giữa khung 口 → ở giữa.
具|Hai tay 八 nâng cái mâm 目 → đồ dùng, dụng cụ.
别|Dao 刂 tách cái khác 另 ra → phân biệt, khác.
区|Vùng che chắn 匸 có dấu chéo 乂 đánh dấu → khu vực.
升|Cái đấu đong 十 nhấc lên → lên cao, tăng (thăng chức).
卡|Vật kẹt giữa trên 上 và dưới 卜 → thẻ, mắc kẹt.
向|Cửa sổ 口 dưới mái nhà mở về một phía → hướng.
契|Dao 刀 khắc vạch 丰 lên gỗ 大 để làm tin → khế ước, hợp đồng.
套|Người 大 quấn tấm vải dài 镸 → bọc, bộ; lượng từ "căn" (一套房).
层|Thân nhà 尸 xếp chồng như mây 云 → tầng.
师|Người cầm dao 刂 lành nghề đi khắp nơi 帀 → thầy, chuyên gia (律师 luật sư).
施|Lá cờ 方 phấp phới 㐌 → thi hành, thiết lập (设施 cơ sở vật chất).
段|Tay cầm đục 殳 chia đá thành từng khúc → đoạn, khúc (地段 khu vực).
电|Tia chớp 曰 giật xuống 乚 → điện.
看|Bàn tay 手 che trên mắt 目 nhìn xa → xem, nhìn.
租|Lúa 禾 nộp đều đặn 且 → tiền thuê.
行|Bước chân trái 彳 + chân phải 亍 → đi; hàng lối (银行 ngân hàng).
权|Cầm cán cân gỗ 木 trong tay 又 → quyền.
过|Bước đi 辶 qua từng tấc 寸 đường → qua.
二|Hai nét ngang = số hai.
介|Người 人 đứng chen vào giữa 八 hai bên → ở giữa, giới thiệu (中介 môi giới).
小|Một nét ở giữa tách hai chấm nhỏ ra → nhỏ.
水|Hình dòng nước chảy ở giữa, bọt nước hai bên → nước.
首|Hình cái đầu có tóc ở trên → đầu, đầu tiên (首付 trả trước lần đầu).
"""

# Tên khi chữ đứng làm bộ thủ bên trong chữ khác (khác với khi đứng riêng)
AS_PART = {"厂": ["hán", "sườn núi, mái che"], "广": ["nghiễm", "mái nhà"], "王": ["ngọc", "ngọc"],
           "人": ["nhân", "người"], "口": ["khẩu", "miệng, đồ đựng"]}

# Nhóm nghĩa của bộ thủ chỉ nghĩa (giúp đoán nghĩa chữ mới)
FAMILY = {
    "扌": "hành động bằng tay", "手": "hành động bằng tay", "又": "hành động bằng tay",
    "氵": "nước, chất lỏng", "冫": "băng, lạnh", "讠": "lời nói", "言": "lời nói", "口": "miệng, nói, ăn",
    "贝": "tiền bạc, của cải", "纟": "sợi, dây, sự nối kết", "糸": "sợi, dây, sự nối kết",
    "木": "cây, đồ gỗ", "辶": "đi lại, di chuyển", "亻": "con người", "人": "con người",
    "忄": "tâm trạng, suy nghĩ", "心": "tâm trạng, suy nghĩ", "土": "đất, nơi chốn", "禾": "lúa, thu hoạch",
    "⺮": "đồ làm bằng tre (thẻ, ống, hộp)", "宀": "nhà cửa", "页": "đầu, mặt", "足": "chân, đi",
    "耳": "tai, nghe", "阝": "đồi, vùng đất", "钅": "kim loại", "舟": "thuyền", "车": "xe",
    "石": "đá", "日": "mặt trời, thời gian", "月": "trăng, thời gian hoặc cơ thể", "攵": "hành động (đánh, dạy)",
    "刂": "dao, cắt", "力": "sức lực", "皿": "bát đĩa, đồ đựng", "衣": "quần áo", "巾": "vải vóc",
    "灬": "lửa, nhiệt", "牛": "trâu bò, vật", "王": "ngọc quý", "立": "đứng", "穴": "hang, chỗ trống",
    "欠": "há miệng, thiếu", "缶": "đồ gốm", "山": "núi", "广": "nhà cửa", "廴": "đi xa", "彳": "đi lại",
    "片": "tấm ván", "矢": "mũi tên", "石": "đá", "礻": "thần, lễ nghi", "饣": "ăn uống", "马": "ngựa",
    "至": "đến", "走": "chạy, đi", "见": "nhìn thấy", "隹": "chim", "彡": "lông, hoa văn",
}


def parse(block):
    out = {}
    for line in block.strip().splitlines():
        parts = line.split("|")
        out[parts[0]] = parts[1:]
    return out


def main():
    hv, story = parse(HV), {k: v[0] for k, v in parse(STORY).items()}
    src = os.path.join(ROOT, "tools", "mmah-dictionary.txt")
    if not os.path.exists(src):
        urllib.request.urlretrieve(MMAH_URL, src)
    D = {}
    for l in open(src, encoding="utf-8"):
        j = json.loads(l)
        D[j["character"]] = j
    wf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "video", "words.json")
    words = json.load(open(wf, encoding="utf-8"))
    if isinstance(words, dict):  # video/words.json: {unit: [[[hz,py,mn],...], ...]}
        words = [w for v in words.values() for line in v for w in line]
    words = [w["w"] if isinstance(w, dict) else w for w in words]  # ALLW của app: [{u, w}, ...]
    chars = sorted({c for w in words for c in w[0] if "一" <= c <= "鿿"})
    out, missing = {}, []
    for c in chars:
        j = D[c]
        e = j.get("etymology") or {}
        parts = [p for p in j["decomposition"] if not ("⿰" <= p <= "⿿") and p != "？"]
        if c not in hv:
            missing.append(c)
        comps = []
        for p in parts:
            name = AS_PART.get(p) if p != c else None
            name = name or hv.get(p)
            if not name:
                missing.append(p)
                name = ["", ""]
            comps.append([p, name[0], name[1]])
        py = (j.get("pinyin") or [""])[0]
        note = story.get(c)
        role = {}
        if not note and e.get("type") == "pictophonetic" and e.get("semantic") and e.get("phonetic"):
            s, p = e["semantic"], e["phonetic"]
            sn, pn = hv.get(s, ["", ""]), hv.get(p, ["", ""])
            ppy = (D.get(p, {}).get("pinyin") or [""])[0]
            sn = AS_PART.get(s, sn)
            note = f"Bộ {s} ({sn[0]} – {sn[1]}) cho nghĩa, phần {p} ({pn[0]}, đọc {ppy}) cho âm → {c} đọc {py}."
            if s in FAMILY:
                note += f" Gặp bộ {s} thường là chữ liên quan đến {FAMILY[s]}."
            role = {"s": s, "p": p}
        if not note:
            missing.append("story:" + c)
        out[c] = {"hv": hv[c][0], "m": hv[c][1], "py": py, "parts": comps, "note": note or "", **role}
    if missing:
        sys.exit("Thiếu dữ liệu: " + " ".join(sorted(set(missing))))
    dst = os.path.join(ROOT, "hanzi.json")
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print(f"{len(out)} chữ -> {dst}")


if __name__ == "__main__":
    main()
