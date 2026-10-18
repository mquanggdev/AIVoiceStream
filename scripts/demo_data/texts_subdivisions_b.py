"""Nội dung DEMO cho 6 phân khu: London, Paris, Palma, Masteri Waterfront, Masteri Lakeside, Senique.

Mỗi phân khu có 7 chủ đề: overview, location, amenities, design, handover, legal, community.
Không chứa giá hoặc mã căn — các thông tin đó nằm trong units.csv.
"""

DOCS_B: dict[str, dict[str, tuple[str, str]]] = {
    "the-london": {
        "overview": (
            "Tổng quan phân khu The London",
            "The London là phân khu căn hộ thuộc cụm The Metropolitan, được mở bán sau The Beverly. Căn hộ The London được thiết "
            "kế theo phong cách cổ điển Anh quốc, với kiến trúc mặt đứng trang nhã, sảnh đón sang trọng và hệ tiện ích trong "
            "nhà phong phú.\n\n"
            "Phân khu gồm ba tòa LD1, LD2 và LD3. Tòa LD1 cao 29 tầng, LD2 cao 26 tầng và LD3 cao 30 tầng, mỗi tầng 16 căn. "
            "The London vừa bàn giao vào quý 3 năm 2026.\n\n"
            "Sản phẩm gồm studio, một phòng ngủ, hai phòng ngủ, hai phòng ngủ cộng một và ba phòng ngủ, bàn giao theo tiêu chuẩn "
            "căn hộ cao cấp với sàn gỗ, trần thạch cao, điều hòa và thiết bị bếp.\n\n"
            "The London phù hợp với cư dân ưa sự thanh lịch, gia đình trung lưu và khách hàng muốn sản phẩm mới bàn giao có nhiều "
            "tiện ích trong nhà, phù hợp cả những ngày mưa hoặc nắng nóng.",
        ),
        "location": (
            "Vị trí phân khu The London",
            "The London sở hữu vị trí ba mặt đường gồm đường Lý Thánh Tông, đường Hải Đăng 8 và đường Hải Đăng 5, thuận tiện cho "
            "việc ra vào và kết nối với các khu vực khác.\n\n"
            "Từ phân khu, cư dân có thể nhanh chóng ra cao tốc Hà Nội – Hải Phòng và Quốc lộ 5. Bên trong đại đô thị, cư dân đi xe "
            "buýt điện khoảng năm đến mười phút tới hồ Ngọc Trai, biển hồ nhân tạo và Vincom Mega Mall. Trường liên cấp Vinschool "
            "nằm gần phân khu.\n\n"
            "Nhờ vị trí mặt đường, The London thuận tiện cho người đi làm và kinh doanh nhỏ ở tầng đế. Các căn hướng vào nội khu "
            "yên tĩnh hơn các căn hướng ra mặt đường Lý Thánh Tông.\n\n"
            "Một số căn tầng cao có thể nhìn về hướng hồ Ngọc Trai, phần lớn các căn còn lại nhìn ra nội khu hoặc thành phố.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The London",
            "The London nổi bật với hệ tiện ích trong nhà: phòng tập gym, phòng giải trí, phòng karaoke, phòng dance, phòng trẻ em, "
            "sảnh lễ tân và sảnh thang máy sang trọng ở tầng một.\n\n"
            "Ngoài trời có bể bơi Santa Monica rộng khoảng 700 mét vuông, gym ngoài trời, hệ thống sân thể thao, quảng trường, "
            "công viên cây xanh và sân chơi trẻ em. An ninh được bố trí tại tầng một mỗi tòa với kiểm soát ra vào bằng thẻ.\n\n"
            "Ngoại khu, cư dân The London sử dụng chung hồ Ngọc Trai, biển hồ nhân tạo, trường liên cấp Vinschool, Vinmec, VinUni, "
            "Vincom Mega Mall và hệ thống xe buýt điện.\n\n"
            "Tiện ích trong nhà là điểm khác biệt so với nhiều phân khu khác vốn tập trung vào tiện ích ngoài trời.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The London",
            "Kiến trúc The London theo phong cách cổ điển Anh: mặt đứng đối xứng, chi tiết phào chỉ, màu sắc trầm ấm, sảnh và hành "
            "lang được trang trí theo phong cách khách sạn.\n\n"
            "Mỗi tầng có 16 căn hộ. Căn studio diện tích thông thủy khoảng 27 đến 36 mét vuông. Căn một phòng ngủ khoảng 37 đến 44 "
            "mét vuông. Căn hai phòng ngủ khoảng 56 đến 65 mét vuông, căn hai phòng ngủ cộng một khoảng 63 đến 72 mét vuông. Căn ba "
            "phòng ngủ khoảng 81 đến 99 mét vuông.\n\n"
            "Căn hộ có phòng khách liền bếp, ban công kính, phòng ngủ chính có vệ sinh riêng ở các căn từ hai phòng ngủ.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc; căn góc có hai mặt thoáng.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tình trạng The London",
            "The London bàn giao vào quý 3 năm 2026. Căn hộ được bàn giao theo tiêu chuẩn cao cấp gồm sàn gỗ, trần thạch cao, điều "
            "hòa, tủ bếp và thiết bị bếp, thiết bị vệ sinh và nhà tắm, thiết bị chiếu sáng, hệ thống cửa, ổ cắm công tắc.\n\n"
            "Vì vừa bàn giao, nhiều căn đang được chủ nhà hoàn thiện nội thất. Căn hộ vẫn trong thời gian bảo hành của chủ đầu tư.\n\n"
            "Người mua lại nên kiểm tra biên bản bàn giao, thời hạn bảo hành và tình trạng thanh toán với chủ đầu tư.\n\n"
            "Các tiện ích trong nhà và bể bơi đã đi vào hoạt động.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The London",
            "Căn hộ The London là căn hộ chung cư thương mại, sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Căn hộ vừa bàn giao nên chưa được cấp sổ hồng. Giao dịch thứ cấp thực hiện bằng chuyển nhượng hợp đồng mua bán có xác "
            "nhận của chủ đầu tư; căn còn trong quỹ hàng ký hợp đồng trực tiếp với chủ đầu tư.\n\n"
            "Người mua cần kiểm tra hợp đồng gốc, các khoản đã thanh toán và khoản vay ngân hàng nếu có.\n\n"
            "Thời điểm cấp sổ cụ thể cần được Sales cập nhật.",
        ),
        "community": (
            "Cộng đồng và đối tượng phù hợp với The London",
            "The London phù hợp với cư dân ưa phong cách thanh lịch, gia đình trung lưu và người làm việc văn phòng muốn có tiện ích "
            "giải trí trong nhà.\n\n"
            "Phân khu thích hợp với gia đình có trẻ nhỏ nhờ phòng trẻ em, sân chơi và trường Vinschool gần kề, cũng như người trẻ "
            "thích hoạt động như dance, karaoke, gym.\n\n"
            "So với The Beverly, The London có quy mô nhỏ hơn, cộng đồng gọn hơn và tiện ích trong nhà phong phú hơn. So với The "
            "Paris, The London đã bàn giao nên có thể vào ở ngay.\n\n"
            "Điểm cần cân nhắc là các căn hướng mặt đường Lý Thánh Tông có thể ồn hơn và giai đoạn đầu sau bàn giao còn thi công "
            "nội thất.",
        ),
    },
    "the-paris": {
        "overview": (
            "Tổng quan phân khu The Paris",
            "The Paris là khu căn hộ cuối cùng thuộc phân khu The Metropolitan được mở bán tại Vinhomes Ocean Park. Là một trong "
            "những mảnh ghép hoàn thiện Thành phố biển, The Paris mang phong cách cổ điển Pháp với biểu tượng quảng trường tháp "
            "Eiffel thu nhỏ.\n\n"
            "Phân khu gồm ba tòa PR1, PR3 và PR5, mỗi tòa cao khoảng 30 tầng, mỗi tầng 16 căn. The Paris đang hoàn thiện, dự kiến "
            "bàn giao vào quý 1 năm 2027.\n\n"
            "Sản phẩm đa dạng gồm studio, một phòng ngủ, một phòng ngủ cộng một, hai phòng ngủ, hai phòng ngủ cộng một và ba phòng "
            "ngủ. Căn hộ được chủ đầu tư phân phối theo bảng giá niêm yết với chính sách thanh toán theo tiến độ.\n\n"
            "The Paris phù hợp với khách hàng yêu thích phong cách Pháp lãng mạn, muốn mua sơ cấp từ chủ đầu tư với thời gian chờ "
            "nhà ngắn.",
        ),
        "location": (
            "Vị trí phân khu The Paris",
            "The Paris nằm trong cụm The Metropolitan, gần trục đường Lý Thánh Tông, kết nối thuận tiện với Quốc lộ 5 và cao tốc "
            "Hà Nội – Hải Phòng.\n\n"
            "Từ The Paris, cư dân đi xe buýt điện khoảng năm đến mười phút tới hồ Ngọc Trai, biển hồ nhân tạo và Vincom Mega Mall. "
            "Phòng khám đa khoa Vinmec, trường học Vinschool và trường liên cấp Deway nằm trong bán kính ngắn.\n\n"
            "Tuyến đường sắt đô thị số 8 theo quy hoạch dự kiến đi qua khu vực lân cận, đây là yếu tố tiềm năng dài hạn.\n\n"
            "Các căn hướng về quảng trường Eiffel và vườn nội khu có tầm nhìn đẹp hơn, các căn ở mặt còn lại nhìn ra thành phố.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Paris",
            "Tiện ích nổi bật của The Paris là quảng trường tháp Eiffel, chòi nghỉ hoàng gia, sân chơi trẻ em phong cách vườn xích "
            "đu cổ tích, tiểu cảnh và đường dạo bộ phong cách Pháp.\n\n"
            "Phân khu có bể bơi ngoài trời, phòng gym, phòng yoga, phòng pilates, phòng bi-a và game, phòng làm việc chung, phòng trà "
            "lounge âm nhạc, phòng sinh hoạt cộng đồng, kid corner, sân thể thao, gym ngoài trời và khu BBQ.\n\n"
            "Ngoại khu, cư dân sử dụng chung hồ Ngọc Trai, biển hồ nhân tạo, Vincom Mega Mall, phòng khám Vinmec, trường Vinschool, "
            "Deway và hệ thống xe buýt điện.\n\n"
            "Vì phân khu chưa bàn giao, một số tiện ích sẽ được đưa vào sử dụng cùng thời điểm bàn giao.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Paris",
            "Kiến trúc The Paris theo phong cách cổ điển Pháp: mặt đứng màu kem, mái và phào chỉ tinh xảo, sảnh và hành lang trang "
            "trí sang trọng.\n\n"
            "Mỗi tầng có 16 căn hộ. Căn studio có diện tích thông thủy khoảng 27 đến 31 mét vuông. Căn một phòng ngủ khoảng 42 đến "
            "44 mét vuông, căn một phòng ngủ cộng một khoảng 46 đến 50 mét vuông. Căn hai phòng ngủ khoảng 61 đến 70 mét vuông, căn "
            "hai phòng ngủ cộng một khoảng 66 đến 75 mét vuông. Căn ba phòng ngủ khoảng 84 đến 97 mét vuông.\n\n"
            "Căn hộ có sảnh căn hộ riêng ở một số tầng, hành lang rộng, ban công kính, bếp mở.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tiến độ The Paris",
            "The Paris đang hoàn thiện, dự kiến bàn giao quý 1 năm 2027. Tiến độ thực tế sẽ được chủ đầu tư thông báo.\n\n"
            "Căn hộ dự kiến bàn giao theo tiêu chuẩn nội thất liền tường cao cấp: sàn gỗ, trần thạch cao, điều hòa, tủ bếp kèm bếp "
            "từ, hút mùi và lò, thiết bị vệ sinh cao cấp, bình nóng lạnh, hệ thống chiếu sáng, khóa cửa điện tử.\n\n"
            "Khách hàng thanh toán theo tiến độ trong chính sách bán hàng, phần lớn giá trị thanh toán khi nhận bàn giao.\n\n"
            "Đây là sản phẩm hình thành trong tương lai, khách hàng xem nhà mẫu và tài liệu thiết kế thay vì căn thực tế.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Paris",
            "Căn hộ The Paris là nhà ở hình thành trong tương lai, sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Khách hàng ký hợp đồng mua bán với chủ đầu tư, có bảo lãnh ngân hàng theo quy định. Sổ hồng được cấp sau khi bàn giao "
            "và hoàn thành thủ tục.\n\n"
            "Mọi điều khoản pháp lý chi tiết cần đối chiếu với hợp đồng mẫu và văn bản chính thức của chủ đầu tư.\n\n"
            "Thời điểm cấp sổ cụ thể chưa xác định.",
        ),
        "community": (
            "Đối tượng phù hợp với The Paris",
            "The Paris phù hợp với khách hàng yêu thích phong cách Pháp, gia đình muốn mua sơ cấp từ chủ đầu tư với chính sách thanh "
            "toán giãn tiến độ và thời gian chờ nhà ngắn, khoảng vài tháng.\n\n"
            "Hệ tiện ích trong nhà phong phú như phòng làm việc chung, phòng yoga, lounge âm nhạc phù hợp với người làm việc linh hoạt "
            "và gia đình trẻ.\n\n"
            "So với các phân khu đã bàn giao trong cụm The Metropolitan, The Paris có lợi thế mua giá niêm yết từ chủ đầu tư kèm "
            "chính sách ưu đãi, nhưng phải chờ bàn giao.\n\n"
            "Điểm cần cân nhắc là rủi ro tiến độ và môi trường hoàn thiện công trình trong giai đoạn đầu.",
        ),
    },
    "the-palma": {
        "overview": (
            "Tổng quan phân khu The Palma",
            "The Palma là phân khu căn hộ hạng sang được Masterise Homes ra mắt đầu tiên tại dự án Lumiere Orient Pearl, nằm trong "
            "đại đô thị Vinhomes Ocean Park. Lấy cảm hứng từ những giá trị chắt lọc, riêng tư và yên bình, The Palma hướng tới "
            "nhóm khách hàng có yêu cầu cao về chất lượng sống.\n\n"
            "Phân khu gồm hai tòa PA1 và PA2, mỗi tòa cao khoảng 32 tầng, mỗi tầng chỉ 10 căn. Mật độ thấp giúp không gian sống riêng "
            "tư và thang máy ít phải chờ.\n\n"
            "Sản phẩm gồm studio, một phòng ngủ, một phòng ngủ cộng một, hai phòng ngủ, hai phòng ngủ cộng một và ba phòng ngủ, trong "
            "đó căn ba phòng ngủ ở góc tòa có thang máy riêng. Dự kiến bàn giao từ quý 3 năm 2027.\n\n"
            "The Palma có mức giá thuộc nhóm cao nhất trong đại đô thị, phù hợp với khách hàng tìm kiếm sản phẩm hạng sang và nhà "
            "đầu tư dài hạn.",
        ),
        "location": (
            "Vị trí phân khu The Palma",
            "The Palma sở hữu vị trí khoáng đạt với cả bốn mặt các tòa căn hộ đều có tầm nhìn rộng mở ra Thành phố biển Ocean Park. "
            "Phân khu có ba mặt tiền đường là Biển Hồ 1, Biển Hồ 2 và trục giao thông Lý Thánh Tông.\n\n"
            "Từ The Palma, cư dân đi bộ vài phút tới biển hồ Crystal Lagoon và khoảng năm phút tới hồ Ngọc Trai. Vincom Mega Mall, "
            "Vinmec và trường Vinschool đều nằm trong bán kính di chuyển ngắn.\n\n"
            "Nhiều căn ở tầng trung và tầng cao nhìn trực diện biển hồ hoặc hồ Ngọc Trai, là lợi thế cảnh quan hiếm có.\n\n"
            "Do nằm cạnh các trục đường chính, một số căn mặt đường Lý Thánh Tông có thể chịu tiếng ồn giao thông, các căn hướng biển "
            "hồ yên tĩnh hơn.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Palma",
            "The Palma được thiết kế với hệ tiện ích hạng sang theo tiêu chuẩn của Masterise Homes: sảnh đón phong cách khách sạn, "
            "lounge cư dân, bể bơi tràn bờ, spa, phòng gym và yoga, phòng sinh hoạt cộng đồng, vườn trên cao và khu vui chơi trẻ em.\n\n"
            "Căn ba phòng ngủ ở góc tòa có thang máy riêng, đảm bảo sự riêng tư tối đa cho chủ nhà.\n\n"
            "Ngoại khu, The Palma tiếp giáp biển hồ Crystal Lagoon, gần hồ Ngọc Trai và công viên trung tâm, sử dụng chung Vincom Mega "
            "Mall, Vinmec, VinUni, Vinschool và xe buýt điện của đại đô thị.\n\n"
            "Vì dự án chưa bàn giao, danh mục tiện ích cuối cùng theo tài liệu chính thức của chủ đầu tư.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Palma",
            "Kiến trúc The Palma theo phong cách Modern Luxury: tối giản, sang trọng, sử dụng vật liệu cao cấp ở mặt ngoài và sảnh.\n\n"
            "Mỗi tầng có 10 căn hộ. Căn studio có diện tích thông thủy khoảng 28 đến 32 mét vuông. Căn một phòng ngủ khoảng 39 đến 42 "
            "mét vuông, căn một phòng ngủ cộng một khoảng 46 đến 48 mét vuông. Căn hai phòng ngủ khoảng 58 đến 64 mét vuông, căn hai "
            "phòng ngủ cộng một khoảng 66 đến 72 mét vuông. Căn ba phòng ngủ khoảng 90 đến 110 mét vuông.\n\n"
            "Căn hộ có trần cao, cửa kính từ sàn tới trần, ban công rộng, bếp mở kết hợp đảo bếp ở căn lớn.\n\n"
            "Các căn hướng Đông nhìn ra biển hồ được định giá cao nhất.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tiến độ The Palma",
            "The Palma dự kiến bàn giao từ quý 3 năm 2027. Căn hộ được bàn giao theo tiêu chuẩn hoàn thiện liền tường cao cấp với "
            "trang thiết bị nhập khẩu từ các thương hiệu hàng đầu thế giới.\n\n"
            "Danh mục bàn giao gồm sàn gỗ kỹ thuật, đá ốp lát cao cấp, điều hòa, hệ thống bếp nhập khẩu kèm thiết bị âm tủ, thiết bị "
            "vệ sinh cao cấp, hệ thống chiếu sáng và khóa thông minh.\n\n"
            "Khách hàng thanh toán theo tiến độ trong chính sách bán hàng của Masterise Homes.\n\n"
            "Đây là sản phẩm hình thành trong tương lai, khách hàng tham quan nhà mẫu và xem tài liệu thiết kế.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Palma",
            "Căn hộ The Palma là nhà ở hình thành trong tương lai do Masterise Homes phát triển, sở hữu lâu dài đối với người Việt "
            "Nam.\n\n"
            "Khách hàng ký thỏa thuận và hợp đồng mua bán với chủ đầu tư, có bảo lãnh ngân hàng theo quy định. Sổ hồng được cấp sau "
            "bàn giao.\n\n"
            "Người nước ngoài có thể sở hữu theo hạn mức và thời hạn của pháp luật về nhà ở.\n\n"
            "Các điều khoản chi tiết cần đối chiếu với hợp đồng mẫu của chủ đầu tư.",
        ),
        "community": (
            "Đối tượng phù hợp với The Palma",
            "The Palma phù hợp với khách hàng thu nhập cao, doanh nhân, chuyên gia và gia đình muốn không gian sống riêng tư, tầm nhìn "
            "biển hồ và tiêu chuẩn hạng sang.\n\n"
            "Nhà đầu tư dài hạn quan tâm The Palma nhờ vị trí hiếm và thương hiệu Masterise Homes, tuy nhiên mọi khoản đầu tư đều có "
            "rủi ro, không thể cam kết lợi nhuận.\n\n"
            "So với Masteri Lakeside, The Palma có mật độ thấp hơn, tầm nhìn biển hồ tốt hơn và giá cao hơn. So với The Senique Hanoi, "
            "The Palma gần biển hồ hơn, còn Senique theo mô hình compound khép kín.\n\n"
            "Điểm cần cân nhắc là mức giá cao và thời gian chờ bàn giao đến năm 2027.",
        ),
    },
    "masteri-waterfront": {
        "overview": (
            "Tổng quan Masteri Waterfront",
            "Masteri Waterfront là dự án căn hộ hạng sang nằm trong quần thể đại đô thị Vinhomes Ocean Park, được phát triển bởi "
            "Masterise Homes, một trong những nhà phát triển bất động sản cao cấp hàng đầu Việt Nam.\n\n"
            "Dự án sở hữu vị trí trung tâm của khu đô thị với tầm nhìn toàn cảnh hồ Ngọc Trai. Trong bộ dữ liệu này, Masteri Waterfront "
            "gồm ba tòa H1, H2 và H3, mỗi tòa cao khoảng 33 tầng, mỗi tầng 14 căn. Dự án đã bàn giao trong giai đoạn từ quý 3 năm "
            "2023 đến quý 4 năm 2024.\n\n"
            "Sản phẩm gồm studio, một phòng ngủ, hai phòng ngủ, hai phòng ngủ cộng một và ba phòng ngủ, bàn giao nội thất liền tường "
            "cao cấp. Giao dịch hiện nay chủ yếu là mua lại từ chủ nhà.\n\n"
            "Masteri Waterfront phù hợp với khách hàng muốn sản phẩm cao cấp đã hoàn thiện, view hồ Ngọc Trai và dịch vụ quản lý "
            "chuyên nghiệp.",
        ),
        "location": (
            "Vị trí Masteri Waterfront",
            "Masteri Waterfront nằm ở vị trí trái tim của khu đô thị, tiếp giáp hồ Ngọc Trai rộng 24,5 héc ta và gần biển hồ Crystal "
            "Lagoon rộng 6,1 héc ta.\n\n"
            "Từ dự án, cư dân đi bộ vài phút ra hồ Ngọc Trai, khoảng năm phút tới biển hồ nhân tạo, Vincom Mega Mall và trường Vinschool. "
            "Bệnh viện Vinmec, Đại học VinUni và trường liên cấp Deway nằm trong bán kính di chuyển ngắn.\n\n"
            "Ra bên ngoài, cư dân sử dụng đường Lý Thánh Tông để kết nối với Quốc lộ 5 và cao tốc Hà Nội – Hải Phòng.\n\n"
            "Nhiều căn ở các tòa H1 và H2 có tầm nhìn trực diện hồ Ngọc Trai, các căn ở mặt còn lại nhìn ra nội khu hoặc thành phố.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu Masteri Waterfront",
            "Masteri Waterfront có hệ thống công viên tiện ích nội khu với bể bơi ngoài trời, bể bơi bốn mùa trong nhà, gym trong nhà "
            "và ngoài trời, spa, sân chơi trẻ em, sân thể thao và sảnh lounge phong cách khách sạn năm sao.\n\n"
            "Các tòa có vườn thượng uyển, khu sinh hoạt cộng đồng và ban công kính cường lực. Dịch vụ quản lý vận hành theo tiêu chuẩn "
            "của Masterise Homes.\n\n"
            "Ngoại khu, cư dân hưởng trọn hồ Ngọc Trai, biển hồ Crystal Lagoon, bệnh viện Vinmec, trường Vinschool, Deway, Vincom Mega "
            "Mall và hệ thống công viên của đại đô thị.\n\n"
            "Khu thương mại tầng đế có nhà hàng, cà phê, cửa hàng tiện lợi và dịch vụ cao cấp.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ Masteri Waterfront",
            "Kiến trúc Masteri Waterfront theo phong cách Modern Luxury, mặt đứng nhiều mảng kính, ban công kính cường lực thời thượng.\n\n"
            "Mỗi tầng có 14 căn hộ. Căn studio diện tích thông thủy khoảng 25 đến 34 mét vuông. Căn một phòng ngủ khoảng 42 đến 48 mét "
            "vuông. Căn hai phòng ngủ khoảng 54 đến 63 mét vuông, căn hai phòng ngủ cộng một khoảng 62 đến 70 mét vuông. Căn ba phòng "
            "ngủ khoảng 74 đến 82 mét vuông.\n\n"
            "Căn hộ được thiết kế tối ưu, phòng khách liền bếp, cửa kính lớn đón ánh sáng và gió từ hồ.\n\n"
            "Các căn hướng hồ Ngọc Trai có giá cao hơn đáng kể so với căn hướng nội khu.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tình trạng Masteri Waterfront",
            "Masteri Waterfront đã bàn giao trong giai đoạn từ quý 3 năm 2023 đến quý 4 năm 2024. Toàn bộ tiện ích đã đi vào hoạt động.\n\n"
            "Căn hộ bàn giao nội thất liền tường cao cấp: sàn gỗ, trần thạch cao, điều hòa, tủ bếp kèm thiết bị bếp nhập khẩu, thiết bị "
            "vệ sinh cao cấp, bình nóng lạnh, hệ thống chiếu sáng, khóa cửa điện tử.\n\n"
            "Một phần căn hộ đã được chủ nhà bổ sung nội thất đầy đủ để cho thuê.\n\n"
            "Người mua lại nên kiểm tra hiện trạng căn hộ và thời hạn bảo hành còn lại.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại Masteri Waterfront",
            "Căn hộ Masteri Waterfront là căn hộ chung cư thương mại, sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Một phần căn hộ đã được cấp sổ hồng, phần còn lại đang được chủ đầu tư làm thủ tục. Giao dịch thứ cấp thực hiện bằng hợp "
            "đồng công chứng nếu có sổ hoặc chuyển nhượng hợp đồng mua bán nếu chưa có sổ.\n\n"
            "Người nước ngoài có thể sở hữu theo quy định, Sales cần kiểm tra hạn mức còn lại.\n\n"
            "Tình trạng pháp lý từng căn cần được xác minh bằng giấy tờ gốc.",
        ),
        "community": (
            "Cộng đồng và đối tượng phù hợp với Masteri Waterfront",
            "Cư dân Masteri Waterfront gồm gia đình khá giả, chuyên gia nước ngoài và người làm việc trong lĩnh vực giáo dục, y tế tại "
            "VinUni và Vinmec.\n\n"
            "Dự án phù hợp với khách hàng muốn căn hộ cao cấp đã hoàn thiện, view hồ Ngọc Trai, dịch vụ quản lý chuyên nghiệp, và nhà "
            "đầu tư cho thuê hướng tới khách chuyên gia.\n\n"
            "So với các phân khu Vinhomes đã bàn giao, Masteri Waterfront có tiêu chuẩn và dịch vụ cao hơn, giá cũng cao hơn. So với "
            "Masteri Lakeside, Waterfront đã có thể vào ở ngay.\n\n"
            "Điểm cần cân nhắc là phí quản lý cao hơn mặt bằng chung và nguồn hàng view hồ không nhiều.",
        ),
    },
    "masteri-lakeside": {
        "overview": (
            "Tổng quan Masteri Lakeside",
            "Masteri Lakeside là dự án cuối cùng thuộc bộ sưu tập căn hộ Masteri Collection tại Vinhomes Ocean Park, là một trong những "
            "mảnh ghép hoàn thiện Thành phố biển. Dự án do Masterise Homes phát triển với thiết kế hiện đại và nội thất sang trọng.\n\n"
            "Trong bộ dữ liệu này, Masteri Lakeside gồm hai tòa ML1 và ML2, mỗi tòa cao khoảng 30 tầng, mỗi tầng 14 căn. Dự án đang xây "
            "dựng, dự kiến bàn giao quý 4 năm 2026.\n\n"
            "Sản phẩm gồm studio, một phòng ngủ cộng một, hai phòng ngủ, hai phòng ngủ cộng một và ba phòng ngủ. Căn hộ được phân phối "
            "theo bảng giá niêm yết của chủ đầu tư kèm chính sách thanh toán chi tiết theo từng đợt.\n\n"
            "Masteri Lakeside phù hợp với khách hàng muốn mua sơ cấp sản phẩm cao cấp, thời gian chờ bàn giao ngắn.",
        ),
        "location": (
            "Vị trí Masteri Lakeside",
            "Masteri Lakeside tọa lạc tại giao điểm của đường Lý Thánh Tông và đường Đại Tây Dương. Từ dự án, cư dân dễ dàng kết nối các "
            "đại tiện ích của toàn khu đô thị, trung tâm thủ đô và các vùng kinh tế trọng điểm phía Bắc.\n\n"
            "Phía Tây Nam dự án tiếp giáp đường Biển Hồ, gần trường học và khu phố thương mại. Cư dân đi bộ vài phút tới hồ cảnh quan, "
            "khoảng năm phút đi xe tới hồ Ngọc Trai, biển hồ nhân tạo và Vincom Mega Mall.\n\n"
            "Tuyến metro số 8 theo quy hoạch dự kiến đi qua khu vực, là yếu tố tiềm năng dài hạn.\n\n"
            "Các căn hướng hồ cảnh quan có tầm nhìn đẹp hơn các căn hướng đường.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu Masteri Lakeside",
            "Masteri Lakeside được thiết kế với bể bơi ngoài trời, bể bơi bốn mùa, phòng gym, spa, khu vui chơi trẻ em, vườn thư giãn, "
            "lounge cư dân và hồ điều hòa cảnh quan.\n\n"
            "Ngoại khu, cư dân sử dụng chung hồ Ngọc Trai, biển hồ nhân tạo, công viên, Vincom Mega Mall, Vinmec, trường học và khu phố "
            "thương mại Biển Hồ.\n\n"
            "Vì dự án chưa bàn giao, tiện ích sẽ đi vào hoạt động cùng thời điểm bàn giao theo kế hoạch của chủ đầu tư.\n\n"
            "Danh mục tiện ích cuối cùng theo tài liệu chính thức của Masterise Homes.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ Masteri Lakeside",
            "Masteri Lakeside theo phong cách Modern Luxury, thiết kế hiện đại, nội thất sang trọng, tối ưu ánh sáng và tầm nhìn.\n\n"
            "Mỗi tầng có 14 căn hộ. Căn studio diện tích thông thủy khoảng 25 đến 27 mét vuông. Căn một phòng ngủ cộng một khoảng 45 đến "
            "47 mét vuông. Căn hai phòng ngủ khoảng 61 đến 64 mét vuông, căn hai phòng ngủ cộng một khoảng 64 đến 67 mét vuông. Căn ba "
            "phòng ngủ khoảng 82 đến 96 mét vuông.\n\n"
            "Căn hộ có bếp mở, ban công kính, phòng ngủ chính có vệ sinh riêng.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tiến độ Masteri Lakeside",
            "Masteri Lakeside dự kiến bàn giao quý 4 năm 2026. Căn hộ bàn giao nội thất liền tường cao cấp theo tiêu chuẩn Masterise "
            "Homes: sàn gỗ, trần thạch cao, điều hòa, bếp và thiết bị bếp nhập khẩu, thiết bị vệ sinh cao cấp, hệ thống chiếu sáng, "
            "khóa thông minh.\n\n"
            "Khách hàng thanh toán theo các đợt trong chính sách bán hàng, gồm đặt cọc, ký văn bản thỏa thuận, ký hợp đồng mua bán và "
            "các đợt theo tiến độ, đợt cuối khi nhận bàn giao.\n\n"
            "Vì sắp bàn giao, thời gian chờ nhà ngắn, phù hợp khách muốn mua sơ cấp nhưng không muốn chờ lâu.\n\n"
            "Tiến độ thực tế theo thông báo của chủ đầu tư.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại Masteri Lakeside",
            "Căn hộ Masteri Lakeside là nhà ở hình thành trong tương lai, sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Khách hàng ký xác nhận đăng ký, văn bản thỏa thuận và hợp đồng mua bán với chủ đầu tư; hợp đồng có bảo lãnh ngân hàng theo "
            "quy định.\n\n"
            "Sổ hồng được cấp sau bàn giao và hoàn tất thủ tục với cơ quan nhà nước.\n\n"
            "Điều khoản chi tiết cần đối chiếu với hợp đồng mẫu của chủ đầu tư.",
        ),
        "community": (
            "Đối tượng phù hợp với Masteri Lakeside",
            "Masteri Lakeside phù hợp với gia đình trẻ, người trẻ thành đạt và nhà đầu tư muốn sản phẩm cao cấp mua trực tiếp từ chủ đầu "
            "tư với chính sách thanh toán linh hoạt.\n\n"
            "So với Masteri Waterfront, Lakeside mới hơn và đang có chính sách sơ cấp, nhưng chưa thể vào ở ngay. So với The Palma, "
            "Lakeside có giá mềm hơn và bàn giao sớm hơn.\n\n"
            "Nhà đầu tư cần lưu ý mọi khoản đầu tư đều có rủi ro, không thể cam kết lợi nhuận.\n\n"
            "Điểm cần cân nhắc là quy mô dự án nhỏ và căn studio diện tích nhỏ hơn các dự án khác.",
        ),
    },
    "the-senique-hanoi": {
        "overview": (
            "Tổng quan The Senique Hanoi",
            "The Senique Hanoi là khu căn hộ cao cấp do CapitaLand Development phát triển, tọa lạc tại vị trí trái tim của khu đô thị "
            "Vinhomes Ocean Park. Đây là dự án được quản lý theo mô hình compound khép kín, an ninh nhiều lớp và tiện ích dành riêng cho "
            "cư dân.\n\n"
            "Trong bộ dữ liệu này, The Senique Hanoi gồm hai tòa SQ1 cao 37 tầng và SQ2 cao 36 tầng, mỗi tầng 12 căn. Dự án dự kiến bàn "
            "giao quý 2 năm 2027.\n\n"
            "Sản phẩm gồm căn một phòng ngủ, hai phòng ngủ, ba phòng ngủ và bốn phòng ngủ diện tích lớn, phù hợp với gia đình đa thế hệ. "
            "Một phần quỹ căn chưa được mở bán và chưa công bố giá.\n\n"
            "The Senique Hanoi phù hợp với khách hàng tìm kiếm sự riêng tư, chuẩn mực quản lý quốc tế và không gian sống xanh.",
        ),
        "location": (
            "Vị trí The Senique Hanoi",
            "The Senique Hanoi nằm ở trung tâm đại đô thị, hòa quyện với cảnh quan xanh và hồ nước rộng mở, gần đường Lý Thánh Tông.\n\n"
            "Từ dự án, cư dân đi bộ vài phút tới hồ cảnh quan, khoảng năm phút đi xe tới hồ Ngọc Trai, biển hồ nhân tạo và Vincom Mega "
            "Mall. Trường học và phòng khám trong khu đô thị nằm trong bán kính ngắn.\n\n"
            "Ra bên ngoài, cư dân kết nối Quốc lộ 5 và cao tốc Hà Nội – Hải Phòng. Khi tuyến metro số 8 hoàn thành và đưa vào sử dụng, "
            "khả năng kết nối sẽ thuận tiện hơn, tuy nhiên đây là yếu tố dài hạn.\n\n"
            "Các căn tầng cao có tầm nhìn rộng ra hồ và toàn cảnh khu đô thị.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Senique Hanoi",
            "The Senique Hanoi có bể bơi ngoài trời dài 50 mét, phòng gym và xông hơi, spa, khu vui chơi trẻ em, vườn cảnh quan, sảnh "
            "lounge và khu sinh hoạt cộng đồng. Tiện ích được dành riêng cho cư dân trong compound.\n\n"
            "Hệ thống an ninh nhiều lớp với kiểm soát ra vào, hầm đỗ xe thông minh và dịch vụ quản lý theo tiêu chuẩn quốc tế của "
            "CapitaLand.\n\n"
            "Ngoại khu, cư dân sử dụng chung hồ Ngọc Trai, biển hồ nhân tạo, trường học, Vinmec, Vincom Mega Mall và hệ thống xe buýt điện "
            "của đại đô thị.\n\n"
            "Vì dự án chưa bàn giao, tiện ích sẽ đi vào hoạt động theo kế hoạch của chủ đầu tư.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Senique Hanoi",
            "The Senique Hanoi theo phong cách Modern Luxury Compound, kiến trúc hiện đại, mật độ xây dựng thấp, nhiều không gian xanh.\n\n"
            "Mỗi tầng có 12 căn hộ. Căn một phòng ngủ có diện tích thông thủy khoảng 42 đến 46 mét vuông. Căn hai phòng ngủ khoảng 54 đến "
            "81 mét vuông. Căn ba phòng ngủ khoảng 83 đến 108 mét vuông. Căn bốn phòng ngủ khoảng 120 đến 135 mét vuông, nằm ở góc tòa.\n\n"
            "Căn hộ thiết kế không gian mở, trần cao, cửa kính lớn, ban công rộng. Căn lớn có phòng giúp việc và kho.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tiến độ The Senique Hanoi",
            "The Senique Hanoi dự kiến bàn giao quý 2 năm 2027. Căn hộ bàn giao hoàn thiện liền tường cao cấp theo tiêu chuẩn CapitaLand: "
            "sàn gỗ, đá ốp lát, điều hòa, hệ thống bếp và thiết bị nhập khẩu, thiết bị vệ sinh cao cấp, hệ thống chiếu sáng, khóa thông "
            "minh.\n\n"
            "Khách hàng thanh toán theo các đợt: booking, ký thỏa thuận ký quỹ, ký hợp đồng mua bán và các đợt theo tiến độ.\n\n"
            "Một phần quỹ căn chưa mở bán, giá sẽ được công bố theo từng đợt.\n\n"
            "Tiến độ thực tế theo thông báo của chủ đầu tư.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Senique Hanoi",
            "Căn hộ The Senique Hanoi là nhà ở hình thành trong tương lai do CapitaLand Development phát triển, sở hữu lâu dài đối với "
            "người Việt Nam.\n\n"
            "Khách hàng ký thỏa thuận ký quỹ và hợp đồng mua bán với chủ đầu tư, có bảo lãnh ngân hàng theo quy định. Sổ hồng được cấp sau "
            "bàn giao.\n\n"
            "Người nước ngoài có thể sở hữu theo hạn mức pháp luật cho phép.\n\n"
            "Điều khoản chi tiết cần đối chiếu với hợp đồng mẫu của chủ đầu tư.",
        ),
        "community": (
            "Đối tượng phù hợp với The Senique Hanoi",
            "The Senique Hanoi phù hợp với gia đình đa thế hệ cần căn ba hoặc bốn phòng ngủ, khách hàng đề cao sự riêng tư của mô hình "
            "compound và chuyên gia nước ngoài quen với chuẩn quản lý quốc tế.\n\n"
            "So với các dự án của Masterise Homes, Senique có căn diện tích lớn hơn và mô hình khép kín. So với các phân khu của Vinhomes, "
            "Senique có mật độ thấp hơn và dịch vụ riêng biệt.\n\n"
            "Nhà đầu tư cần lưu ý một phần quỹ căn chưa công bố giá và mọi khoản đầu tư đều có rủi ro.\n\n"
            "Điểm cần cân nhắc là thời gian chờ bàn giao đến năm 2027 và mức giá cao.",
        ),
    },
}
