"""Nội dung DEMO cho 6 phân khu: Sapphire, Zenpark, Pavilion, Bayfront, Zurich, Beverly.

Mỗi phân khu có 7 chủ đề: overview, location, amenities, design, handover, legal, community.
Không chứa giá hoặc mã căn — các thông tin đó nằm trong units.csv.
"""

DOCS_A: dict[str, dict[str, tuple[str, str]]] = {
    "the-sapphire": {
        "overview": (
            "Tổng quan phân khu The Sapphire",
            "The Sapphire là phân khu căn hộ đầu tiên được mở bán và bàn giao tại Vinhomes Ocean Park, gồm các cụm "
            "Sapphire 1 và Sapphire 2. Những căn hộ đầu tiên được bàn giao từ tháng 4 năm 2020, vì vậy đây là khu có "
            "cộng đồng cư dân lâu năm và đông đúc nhất trong đại đô thị.\n\n"
            "Điểm mạnh nổi bật của The Sapphire là mức giá dễ tiếp cận nhất trong các phân khu của Vinhomes tại Ocean "
            "Park, phù hợp với người mua nhà lần đầu, gia đình trẻ và nhà đầu tư cho thuê với ngân sách vừa phải. Cơ cấu "
            "sản phẩm đa dạng từ căn studio, một phòng ngủ, một phòng ngủ cộng một, hai phòng ngủ cho đến ba phòng ngủ.\n\n"
            "Trong bộ dữ liệu này, The Sapphire gồm các tòa S1.03, S1.05, S2.12 và S2.18. Các tòa cao khoảng 29 đến 30 "
            "tầng, mỗi tầng 14 căn. Vì đã bàn giao từ lâu nên giao dịch tại đây hiện chủ yếu là mua bán lại, giá do chủ "
            "nhà rao bán và có thể thương lượng.\n\n"
            "Khách hàng chọn The Sapphire thường quan tâm đến chi phí hợp lý, tiện ích hoàn thiện sẵn và khả năng vào ở "
            "ngay. Điểm cần cân nhắc là tiêu chuẩn bàn giao cơ bản, các căn hộ đã qua sử dụng nên cần kiểm tra hiện trạng "
            "nội thất và thiết bị trước khi quyết định.",
        ),
        "location": (
            "Vị trí phân khu The Sapphire",
            "The Sapphire nằm ở khu vực cửa ngõ phía Bắc của đại đô thị, gần trục đường Lý Thánh Tông, thuận tiện ra "
            "Quốc lộ 5 để đi vào nội thành Hà Nội. Đây là khu vực được xây dựng sớm nhất nên hạ tầng đường nội khu, vỉa hè "
            "và cây xanh đã hoàn thiện và trưởng thành.\n\n"
            "Từ The Sapphire, cư dân đi bộ khoảng năm đến mười phút tới hồ Ngọc Trai, khoảng mười phút tới cụm trường "
            "Vinschool và khoảng mười lăm phút đi xe buýt điện tới Vincom Mega Mall Ocean Park. Bệnh viện Vinmec và Đại học "
            "VinUni nằm trong bán kính vài kilomet, di chuyển bằng xe buýt nội khu rất thuận tiện.\n\n"
            "Do nằm gần cổng vào đại đô thị, The Sapphire có lợi thế về thời gian di chuyển ra các trục đường lớn, phù hợp "
            "với người đi làm hằng ngày vào nội thành hoặc sang khu Long Biên. Mặt trái là một số tòa gần trục đường chính "
            "có thể chịu tiếng ồn giao thông vào giờ cao điểm, các căn hướng vào nội khu thường yên tĩnh hơn.\n\n"
            "Một số căn ở tầng cao của tòa S2.18 có thể nhìn được về phía hồ Ngọc Trai, còn đa số căn nhìn ra công viên "
            "nội khu hoặc hướng thành phố.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Sapphire",
            "Tiện ích nội khu của The Sapphire gồm bể bơi ngoài trời, bể bơi trong nhà, phòng tập gym, khu vườn Nhật nhỏ "
            "với hồ cá koi, chòi nghỉ và ghế nghỉ dọc đường dạo. Mỗi cụm tòa có sân chơi trẻ em, sân thể thao đa năng và "
            "khu BBQ ngoài trời cho cư dân đăng ký sử dụng vào cuối tuần.\n\n"
            "Tầng đế của các tòa là dãy shophouse với cửa hàng tiện lợi, siêu thị mini, quán cà phê, nhà hàng, tiệm thuốc, "
            "tiệm giặt là và các dịch vụ hằng ngày. Nhờ cộng đồng cư dân đông, khu thương mại tại Sapphire là một trong "
            "những khu sầm uất nhất Ocean Park.\n\n"
            "Về tiện ích ngoại khu, cư dân Sapphire sử dụng chung các đại tiện ích của khu đô thị như hồ Ngọc Trai, biển "
            "hồ Crystal Lagoon, công viên trung tâm, trường liên cấp Vinschool, Đại học VinUni, phòng khám Vinmec và trung "
            "tâm thương mại Vincom Mega Mall. Tuyến xe buýt điện có điểm dừng ngay trong phân khu.\n\n"
            "Vì là phân khu đầu tiên, một số tiện ích nội khu đã sử dụng nhiều năm, chất lượng duy trì tùy thuộc vào ban "
            "quản lý từng cụm tòa.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Sapphire",
            "The Sapphire được thiết kế theo phong cách hiện đại, tối giản, ưu tiên công năng và tối ưu diện tích để giữ "
            "mức giá hợp lý. Mỗi tầng có 14 căn hộ bố trí quanh lõi thang máy, hai mặt tòa nhìn về hai hướng chính.\n\n"
            "Căn studio có diện tích thông thủy khoảng 26 đến 33 mét vuông, phù hợp cho một người ở hoặc cho thuê. Căn một "
            "phòng ngủ khoảng 38 đến 45 mét vuông. Căn một phòng ngủ cộng một có thêm một góc nhỏ có thể làm phòng làm việc "
            "hoặc phòng ngủ cho trẻ nhỏ. Căn hai phòng ngủ khoảng 55 đến 70 mét vuông, phổ biến nhất trong phân khu. Căn ba "
            "phòng ngủ khoảng 76 đến 92 mét vuông, thường nằm ở các góc tòa và có hai mặt thoáng.\n\n"
            "Các căn đều có ban công hoặc lô gia, phòng khách liền bếp, cửa sổ kính lớn để lấy sáng. Căn góc được đánh giá "
            "cao hơn vì thông thoáng và nhiều ánh sáng tự nhiên.\n\n"
            "Hướng ban công trong phân khu chủ yếu là Đông Nam và Tây Bắc. Người mua quan tâm phong thủy hoặc tránh nắng "
            "chiều thường ưu tiên căn ban công hướng Đông Nam.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tình trạng The Sapphire",
            "The Sapphire đã bàn giao từ quý 2 năm 2020. Căn hộ được bàn giao theo tiêu chuẩn cơ bản của Vinhomes, gồm sàn "
            "gỗ công nghiệp ở phòng ngủ và phòng khách, sàn gạch ở khu vệ sinh và ban công, tủ bếp trên dưới, bếp từ, máy hút "
            "mùi, thiết bị vệ sinh cơ bản, hệ thống đèn chiếu sáng, cửa chính và cửa sổ hoàn thiện.\n\n"
            "Tiêu chuẩn cơ bản thường chưa bao gồm điều hòa, rèm cửa, tủ quần áo và đồ rời. Vì phần lớn căn hộ đã có người ở "
            "nhiều năm, nội thất thực tế khi mua lại phụ thuộc vào từng chủ nhà: có căn để trống, có căn đã được làm nội thất "
            "đầy đủ.\n\n"
            "Khi mua lại căn hộ tại Sapphire, người mua nên kiểm tra kỹ hiện trạng chống thấm khu vệ sinh, tình trạng thiết bị "
            "bếp, hệ thống điện nước và các khoản phí quản lý còn nợ trước khi ký hợp đồng.\n\n"
            "Ưu điểm của việc mua căn đã bàn giao là xem được căn thực tế, đánh giá được ánh sáng, tiếng ồn và cộng đồng "
            "cư dân trước khi quyết định.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Sapphire",
            "Căn hộ tại The Sapphire là căn hộ chung cư thương mại, hình thức sở hữu lâu dài đối với người Việt Nam. Phần lớn "
            "căn hộ đã được chủ đầu tư làm thủ tục cấp giấy chứng nhận quyền sở hữu, thường gọi là sổ hồng.\n\n"
            "Với căn đã có sổ, giao dịch được thực hiện bằng hợp đồng mua bán công chứng và làm thủ tục sang tên tại văn phòng "
            "đăng ký đất đai. Với số ít căn chưa có sổ, giao dịch thực hiện qua chuyển nhượng hợp đồng mua bán có xác nhận của "
            "chủ đầu tư.\n\n"
            "Người mua cần kiểm tra căn hộ có đang thế chấp ngân hàng hay không. Nếu đang thế chấp, hai bên cần thỏa thuận "
            "phương án tất toán khoản vay trước hoặc trong quá trình công chứng.\n\n"
            "Tình trạng sổ của từng căn cụ thể cần được Sales xác minh với chủ nhà và giấy tờ gốc, hệ thống chỉ cung cấp thông "
            "tin chung của phân khu.",
        ),
        "community": (
            "Cộng đồng và đối tượng phù hợp với The Sapphire",
            "The Sapphire có cộng đồng cư dân đông nhất Ocean Park, đa dạng từ gia đình trẻ, người đi làm, người lớn tuổi đến "
            "chuyên gia nước ngoài thuê nhà. Không khí sinh hoạt sôi động, đặc biệt vào buổi tối và cuối tuần quanh khu "
            "shophouse và sân chơi.\n\n"
            "Phân khu phù hợp nhất với người mua nhà lần đầu cần mức giá dễ tiếp cận, gia đình trẻ muốn vào ở ngay gần trường "
            "học và công viên, và nhà đầu tư cho thuê căn studio hoặc một phòng ngủ nhờ nhu cầu thuê ổn định.\n\n"
            "Điểm cần cân nhắc là mật độ cư dân cao nên giờ cao điểm thang máy có thể phải chờ, tiêu chuẩn bàn giao cơ bản "
            "và các tiện ích nội khu đã qua nhiều năm sử dụng. Khách ưu tiên sự yên tĩnh và sản phẩm mới có thể cân nhắc "
            "thêm The Zenpark, The Pavilion hoặc các phân khu thuộc The Metropolitan.\n\n"
            "Với nhà đầu tư, tỷ lệ cho thuê tại Sapphire thường tốt nhờ giá thuê vừa phải, tuy nhiên nguồn cung cho thuê "
            "cũng lớn nên cạnh tranh về giá và nội thất.",
        ),
    },
    "the-zenpark": {
        "overview": (
            "Tổng quan phân khu The Zenpark",
            "The Zenpark là phân khu căn hộ cao cấp phong cách Nhật Bản, thuộc cụm The Ocean View của Vinhomes Ocean Park. "
            "Phân khu gồm bốn tòa R1.01, R1.02, R1.03 và R1.05, đã hoàn thiện và bàn giao từ quý 2 năm 2021.\n\n"
            "The Zenpark được định vị ở phân khúc Ruby, cao hơn The Sapphire, với tiêu chuẩn bàn giao nội thất liền tường và "
            "chất lượng dịch vụ quản lý vận hành tương đương các khu căn hộ cao cấp khác của Vinhomes tại Hà Nội.\n\n"
            "Điểm nhận diện của phân khu là công viên Nhật Bản rộng khoảng một héc ta nằm giữa các tòa, với vườn thiền, hồ cá "
            "koi, cổng torii, cầu gỗ và những hàng hoa anh đào. Không gian được thiết kế theo triết lý sống chậm, cân bằng và "
            "gần gũi thiên nhiên.\n\n"
            "Mỗi tòa cao khoảng 30 tầng, mỗi tầng 16 căn với các loại từ studio tới ba phòng ngủ. Vì đã bàn giao, giao dịch "
            "hiện tại chủ yếu là mua lại từ chủ nhà. The Zenpark phù hợp với khách hàng muốn một không gian sống yên tĩnh, "
            "thẩm mỹ, có tiện ích hoàn thiện và vào ở ngay.",
        ),
        "location": (
            "Vị trí phân khu The Zenpark",
            "The Zenpark nằm ở vị trí trung tâm của đại đô thị, kế cận đường Lý Thánh Tông rộng khoảng 40 mét, trục giao "
            "thông chính kết nối với Quốc lộ 5, cao tốc Hà Nội – Hải Phòng và đường 379 đi Ecopark.\n\n"
            "Từ The Zenpark, cư dân đi bộ vài phút là tới hồ Ngọc Trai, khoảng năm phút tới trường liên cấp Vinschool và "
            "khoảng mười phút đi xe tới biển hồ Crystal Lagoon và Vincom Mega Mall Ocean Park. Phòng khám Vinmec và Đại học "
            "VinUni cũng nằm trong bán kính di chuyển ngắn bằng xe buýt điện.\n\n"
            "Nhờ nằm giữa khu đô thị, The Zenpark vừa thuận tiện ra trục đường lớn vừa giữ được sự yên tĩnh bên trong nhờ "
            "công viên Nhật Bản ngăn cách các tòa với đường giao thông. Nhiều căn ở tầng trung và tầng cao có hướng nhìn về "
            "phía hồ Ngọc Trai hoặc nhìn thẳng xuống vườn Nhật.\n\n"
            "Tuyến đường sắt đô thị số 8 theo quy hoạch dự kiến đi qua khu vực lân cận, tuy nhiên đây là yếu tố tiềm năng dài "
            "hạn, chưa nên coi là tiện ích hiện hữu.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Zenpark",
            "Tiện ích nổi bật nhất của The Zenpark là công viên Nhật Bản với vườn thiền, hồ cá koi, cổng torii, chòi nghỉ lục "
            "giác, cầu gỗ và đường dạo bộ rợp bóng cây. Đây là nơi cư dân thường tản bộ, tập dưỡng sinh buổi sáng và chụp ảnh "
            "mùa hoa.\n\n"
            "Phân khu có bể bơi bốn mùa trong nhà, bể bơi ngoài trời, phòng gym trong nhà, gym ngoài trời, nhà đa năng tổ chức "
            "sự kiện cộng đồng, sân chơi trẻ em theo chủ đề Nhật Bản và khu BBQ. Sảnh các tòa được thiết kế sang trọng, có "
            "lễ tân và khu chờ.\n\n"
            "Tầng đế là dãy thương mại với nhà hàng Nhật, quán cà phê, cửa hàng tiện lợi, spa và các dịch vụ thiết yếu.\n\n"
            "Ngoại khu, cư dân sử dụng chung hồ Ngọc Trai, biển hồ nhân tạo, công viên trung tâm, trường Vinschool, Vinmec, "
            "Vincom Mega Mall và hệ thống xe buýt điện của đại đô thị. Khoảng cách gần tới hồ Ngọc Trai là một lợi thế rõ rệt "
            "so với nhiều phân khu khác.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Zenpark",
            "Kiến trúc The Zenpark lấy cảm hứng từ Nhật Bản: đường nét tối giản, màu sắc trung tính, vật liệu gỗ và đá tự "
            "nhiên trong sảnh, cảnh quan đặt trọng tâm vào sự hài hòa giữa con người và thiên nhiên.\n\n"
            "Mỗi tầng có 16 căn hộ. Căn studio có diện tích thông thủy khoảng 27 đến 31 mét vuông. Căn một phòng ngủ khoảng "
            "41 đến 46 mét vuông, căn một phòng ngủ cộng một khoảng 45 đến 50 mét vuông. Căn hai phòng ngủ khoảng 59 đến 70 "
            "mét vuông, căn hai phòng ngủ cộng một khoảng 63 đến 72 mét vuông. Căn ba phòng ngủ khoảng 76 đến 86 mét vuông, "
            "thường ở góc tòa với hai mặt thoáng.\n\n"
            "Các căn được thiết kế phòng khách liền bếp, ban công rộng, cửa kính lớn. Căn hai phòng ngủ trở lên thường có hai "
            "phòng vệ sinh. Các căn nhìn xuống vườn Nhật hoặc hướng hồ Ngọc Trai được ưa chuộng hơn.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc; căn góc có thêm mặt thoáng hướng Đông Bắc hoặc Tây Nam.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tình trạng The Zenpark",
            "The Zenpark đã bàn giao từ quý 2 năm 2021, toàn bộ bốn tòa đã có cư dân sinh sống.\n\n"
            "Căn hộ được bàn giao theo tiêu chuẩn nội thất liền tường: sàn gỗ cao cấp, trần thạch cao, điều hòa âm trần hoặc "
            "treo tường, tủ bếp trên dưới kèm bếp từ, máy hút mùi, lò vi sóng hoặc lò nướng tùy loại căn, thiết bị vệ sinh "
            "thương hiệu cao cấp, bình nóng lạnh, hệ thống chiếu sáng và khóa cửa điện tử.\n\n"
            "Tiêu chuẩn này chưa gồm đồ rời như sofa, giường, tủ quần áo và rèm cửa. Với căn mua lại, nội thất thực tế phụ "
            "thuộc vào chủ nhà, nhiều căn đã được bổ sung nội thất đầy đủ để cho thuê.\n\n"
            "Do bàn giao chưa quá lâu, hệ thống kỹ thuật và tiện ích nội khu của The Zenpark vẫn trong tình trạng tốt. Người "
            "mua vẫn nên kiểm tra hiện trạng thiết bị, chống thấm và lịch sử bảo trì trước khi giao dịch.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Zenpark",
            "Căn hộ The Zenpark là căn hộ chung cư thương mại, sở hữu lâu dài đối với người Việt Nam. Phần lớn căn hộ đã được "
            "cấp giấy chứng nhận quyền sở hữu.\n\n"
            "Giao dịch thứ cấp thực hiện bằng hợp đồng mua bán công chứng nếu đã có sổ, hoặc chuyển nhượng hợp đồng mua bán có "
            "xác nhận của chủ đầu tư nếu chưa có sổ. Người bán thường chịu thuế thu nhập cá nhân 2%, người mua chịu lệ phí "
            "trước bạ 0,5%, trừ khi hai bên thỏa thuận khác.\n\n"
            "Người nước ngoài có thể sở hữu căn hộ trong giới hạn và thời hạn theo quy định pháp luật về nhà ở, cần Sales "
            "kiểm tra hạn mức còn lại của từng tòa.\n\n"
            "Thông tin pháp lý của từng căn cụ thể phải được xác minh bằng giấy tờ gốc trước khi đặt cọc.",
        ),
        "community": (
            "Cộng đồng và đối tượng phù hợp với The Zenpark",
            "Cư dân The Zenpark chủ yếu là gia đình trung lưu và khá giả, người làm việc văn phòng, chuyên gia trong và ngoài "
            "nước. Cộng đồng có nhiều người Nhật và Hàn Quốc thuê ở nhờ phong cách thiết kế và các nhà hàng, cửa hàng Nhật trong "
            "phân khu.\n\n"
            "Phân khu phù hợp với gia đình muốn không gian yên tĩnh, thẩm mỹ, gần hồ Ngọc Trai và trường Vinschool, với người "
            "yêu thích phong cách Nhật Bản, và với nhà đầu tư cho thuê hướng tới khách chuyên gia có mức chi trả cao.\n\n"
            "So với The Sapphire, The Zenpark có giá cao hơn nhưng tiêu chuẩn bàn giao và cảnh quan tốt hơn rõ rệt. So với các "
            "phân khu mới của The Metropolitan, Zenpark có lợi thế đã hoàn thiện, cây xanh trưởng thành và cộng đồng ổn định.\n\n"
            "Điểm cần cân nhắc là nguồn hàng thứ cấp không nhiều ở các căn view vườn Nhật hoặc view hồ, giá các căn này thường "
            "cao hơn mặt bằng chung của phân khu.",
        ),
    },
    "the-pavilion": {
        "overview": (
            "Tổng quan phân khu The Pavilion",
            "The Pavilion là phân khu căn hộ thuộc cụm The Ocean View, nằm ở khu vực trung tâm của Vinhomes Ocean Park. Phân "
            "khu gồm hai tòa P1 và P2, được bàn giao từ quý 1 năm 2024.\n\n"
            "The Pavilion mang phong cách nghỉ dưỡng nhiệt đới, lấy cảm hứng từ các khu resort ven biển với nhiều cây xanh, "
            "mặt nước và không gian mở. Tiêu chuẩn bàn giao được nâng cấp so với The Sapphire, thường được gọi là tiêu chuẩn "
            "Sapphire cộng.\n\n"
            "Mỗi tòa cao khoảng 30 tầng, mỗi tầng 15 căn với các loại từ studio, một phòng ngủ, hai phòng ngủ đến ba phòng "
            "ngủ. Do mới bàn giao khoảng hai năm, hệ thống thang máy, sảnh và tiện ích còn mới, cộng đồng cư dân đang dần ổn "
            "định.\n\n"
            "The Pavilion là lựa chọn cân bằng giữa giá và chất lượng: mức giá thuộc nhóm dễ tiếp cận của Vinhomes, nhưng "
            "sản phẩm mới hơn và cảnh quan nghỉ dưỡng hơn so với các phân khu bàn giao sớm.",
        ),
        "location": (
            "Vị trí phân khu The Pavilion",
            "The Pavilion nằm trong cụm The Ocean View, ở khu vực trung tâm đại đô thị, gần trục đường Lý Thánh Tông. Từ phân "
            "khu có thể đi bộ tới hồ Ngọc Trai trong khoảng năm đến bảy phút.\n\n"
            "Cư dân The Pavilion đi xe buýt điện khoảng năm phút tới Vincom Mega Mall Ocean Park, khoảng mười phút tới biển hồ "
            "Crystal Lagoon. Trường liên cấp Vinschool và phòng khám Vinmec nằm trong bán kính dưới hai kilomet.\n\n"
            "Ra bên ngoài, The Pavilion kết nối thuận tiện với Quốc lộ 5 và cao tốc Hà Nội – Hải Phòng qua đường Lý Thánh Tông. "
            "Thời gian di chuyển ô tô vào khu vực trung tâm Hà Nội khoảng ba mươi phút ngoài giờ cao điểm.\n\n"
            "Các căn hướng ra phía hồ hoặc đảo yoga trong nội khu có tầm nhìn thoáng hơn, các căn hướng ra đường có thể nhìn về "
            "phía thành phố.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Pavilion",
            "The Pavilion có hệ thống tiện ích theo phong cách resort nhiệt đới: bể bơi ngoài trời dáng tự do bao quanh bởi "
            "hàng cọ, đảo yoga giữa hồ cảnh quan, quảng trường trung tâm, vườn nhiệt đới và đường dạo bộ ven hồ.\n\n"
            "Ngoài ra phân khu có phòng gym, spa, sân chơi trẻ em, khu BBQ, ghế nghỉ dọc lối đi và hầm để xe rộng rãi. Một số "
            "căn được trang bị hệ thống nhà thông minh cơ bản như khóa cửa điện tử và điều khiển chiếu sáng.\n\n"
            "Tầng đế là khu thương mại với cửa hàng tiện lợi, quán cà phê, nhà hàng và các dịch vụ hằng ngày, tuy chưa sầm uất "
            "bằng khu Sapphire.\n\n"
            "Về ngoại khu, cư dân sử dụng chung hồ Ngọc Trai, biển hồ nhân tạo, công viên trung tâm, trường Vinschool, Đại học "
            "VinUni, Vinmec và Vincom Mega Mall của đại đô thị.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Pavilion",
            "Kiến trúc The Pavilion theo phong cách Tropical Resort: mặt ngoài sáng màu, nhiều mảng kính, ban công rộng và cảnh "
            "quan cây xanh phủ kín không gian chung.\n\n"
            "Mỗi tầng có 15 căn hộ. Căn studio diện tích thông thủy khoảng 27 đến 34 mét vuông. Căn một phòng ngủ khoảng 36 đến "
            "46 mét vuông. Căn hai phòng ngủ khoảng 55 đến 72 mét vuông, là loại căn chiếm tỷ lệ lớn nhất. Căn ba phòng ngủ khoảng "
            "78 đến 96 mét vuông, nằm ở các góc tòa.\n\n"
            "Thiết kế căn hộ ưu tiên ánh sáng tự nhiên, phòng khách liền bếp, ban công đủ rộng để đặt bàn ghế nhỏ. Căn hai phòng "
            "ngủ diện tích lớn và căn ba phòng ngủ có hai phòng vệ sinh.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc; căn hướng Đông Nam nhìn ra đảo yoga và hồ cảnh quan được ưa chuộng "
            "hơn.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tình trạng The Pavilion",
            "The Pavilion bàn giao từ quý 1 năm 2024. Tiêu chuẩn bàn giao là Sapphire cộng, nâng cấp so với tiêu chuẩn cơ bản "
            "của The Sapphire.\n\n"
            "Căn hộ được bàn giao với sàn gỗ công nghiệp, sàn gạch khu vệ sinh và ban công, tủ bếp trên dưới, bếp từ, máy hút mùi, "
            "thiết bị vệ sinh, bình nóng lạnh, đèn chiếu sáng, khóa cửa điện tử và một số thiết bị nhà thông minh cơ bản. Tiêu "
            "chuẩn này thường chưa gồm điều hòa và đồ rời.\n\n"
            "Do mới bàn giao, phần lớn căn hộ còn mới, một số chủ nhà mua đầu tư vẫn để căn trống hoặc mới hoàn thiện nội thất "
            "để cho thuê. Người mua lại nên kiểm tra thời hạn bảo hành còn lại của căn hộ và thiết bị.\n\n"
            "Các hạng mục tiện ích của phân khu đã hoàn thiện và đưa vào sử dụng.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Pavilion",
            "Căn hộ The Pavilion là căn hộ chung cư thương mại, sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Vì bàn giao năm 2024, một phần căn hộ đã được cấp sổ hồng, một phần đang trong quá trình chủ đầu tư làm thủ tục cấp "
            "sổ. Giao dịch với căn chưa có sổ được thực hiện bằng chuyển nhượng hợp đồng mua bán có xác nhận của chủ đầu tư.\n\n"
            "Người mua cần kiểm tra tiến độ thanh toán của chủ nhà với chủ đầu tư, khoản vay ngân hàng nếu có và các khoản phí "
            "còn phải đóng như kinh phí bảo trì.\n\n"
            "Tình trạng sổ của từng căn cần được Sales xác minh cụ thể.",
        ),
        "community": (
            "Cộng đồng và đối tượng phù hợp với The Pavilion",
            "Cư dân The Pavilion phần lớn là gia đình trẻ và người mua để ở mới chuyển về trong hai năm gần đây, cùng một tỷ lệ "
            "nhà đầu tư cho thuê.\n\n"
            "Phân khu phù hợp với người muốn sản phẩm mới, tiện ích resort, nhưng ngân sách chưa đủ cho các phân khu thuộc "
            "The Metropolitan hay các dự án hạng sang. Đây cũng là lựa chọn tốt cho gia đình muốn vào ở ngay mà không phải chờ "
            "xây dựng.\n\n"
            "So với The Sapphire, The Pavilion mới hơn, ít cư dân hơn nên yên tĩnh hơn, tiêu chuẩn bàn giao tốt hơn. So với "
            "The Zenpark, The Pavilion có giá mềm hơn nhưng cảnh quan chưa đặc trưng bằng vườn Nhật.\n\n"
            "Điểm cần cân nhắc là khu thương mại tầng đế chưa sầm uất và cộng đồng đang trong giai đoạn hình thành.",
        ),
    },
    "the-bayfront": {
        "overview": (
            "Tổng quan phân khu The Bayfront",
            "The Bayfront là phân khu căn hộ cao tầng do Vinhomes phát triển, mang phong cách Dubai Tropical, kết hợp nét sang "
            "trọng của kiến trúc Trung Đông với không gian nhiệt đới nhiều cây xanh và mặt nước. Phân khu đang trong giai "
            "đoạn xây dựng, dự kiến bàn giao vào quý 4 năm 2027.\n\n"
            "Trong bộ dữ liệu này, The Bayfront gồm ba tòa BF1, BF2 và BF3, mỗi tòa cao khoảng 35 tầng, mỗi tầng 12 căn. Mật độ "
            "căn hộ mỗi tầng thấp hơn các phân khu bàn giao sớm, giúp không gian hành lang và thang máy thoải mái hơn.\n\n"
            "Sản phẩm gồm căn một phòng ngủ cộng một, hai phòng ngủ, hai phòng ngủ cộng một và ba phòng ngủ, hướng tới khách "
            "hàng mua để ở lâu dài và nhà đầu tư trung hạn. Căn hộ được chủ đầu tư phân phối theo bảng giá niêm yết, kèm chính "
            "sách thanh toán theo tiến độ.\n\n"
            "The Bayfront phù hợp với khách hàng có thể chờ nhà và muốn sở hữu sản phẩm mới nhất, tiêu chuẩn bàn giao liền tường, "
            "vị trí gần khu biển hồ.",
        ),
        "location": (
            "Vị trí phân khu The Bayfront",
            "The Bayfront nằm ở phía Đông của đại đô thị, gần khu vực biển hồ Crystal Lagoon. Đây là khu vực đang được hoàn "
            "thiện hạ tầng, với các tuyến đường nội khu mới và hệ thống công viên ven biển hồ.\n\n"
            "Từ The Bayfront, cư dân có thể đi bộ khoảng năm đến mười phút ra bãi cát của biển hồ, khoảng mười phút đi xe buýt "
            "điện tới hồ Ngọc Trai và Vincom Mega Mall. Trường học và phòng khám trong khu đô thị đều nằm trong bán kính vài "
            "kilomet.\n\n"
            "Nhiều căn ở tầng trung và tầng cao có hướng nhìn ra biển hồ, đây là lợi thế cảnh quan nổi bật của phân khu. Các căn "
            "ở mặt còn lại nhìn vào nội khu hoặc hướng thành phố.\n\n"
            "Vì phân khu đang xây dựng, môi trường xung quanh trong giai đoạn hiện tại vẫn còn công trường, tiếng ồn và bụi sẽ "
            "giảm dần khi các hạng mục hoàn thiện.",
        ),
        "amenities": (
            "Tiện ích dự kiến của The Bayfront",
            "Theo thiết kế, The Bayfront có bể bơi bốn mùa, bể bơi ngoài trời phong cách beach club, vườn nhiệt đới, khu thể "
            "thao, phòng gym, spa, sân chơi trẻ em và sảnh đón phong cách khách sạn. Các tiện ích này sẽ được đưa vào sử dụng "
            "cùng thời điểm bàn giao.\n\n"
            "Ngoại khu, The Bayfront hưởng lợi trực tiếp từ biển hồ Crystal Lagoon với bãi cát trắng, các môn thể thao dưới nước "
            "và các sự kiện lễ hội mùa hè. Cư dân cũng sử dụng chung hồ Ngọc Trai, trường Vinschool, Đại học VinUni, Vinmec và "
            "Vincom Mega Mall của đại đô thị.\n\n"
            "Vì phân khu chưa bàn giao, danh mục tiện ích có thể được chủ đầu tư điều chỉnh. Khách hàng nên đối chiếu với tài "
            "liệu bán hàng chính thức tại thời điểm ký hợp đồng.\n\n"
            "Đây là điểm khác biệt quan trọng so với các phân khu đã bàn giao: tiện ích của The Bayfront là tiện ích theo thiết "
            "kế, chưa phải tiện ích hiện hữu.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Bayfront",
            "Kiến trúc The Bayfront kết hợp đường cong mềm mại, các khối kiến trúc màu sáng và hệ thống ban công rộng, gợi cảm "
            "giác nghỉ dưỡng ven biển kiểu Dubai.\n\n"
            "Mỗi tầng có 12 căn hộ, ít hơn các phân khu khác. Căn một phòng ngủ cộng một có diện tích thông thủy khoảng 45 đến 50 "
            "mét vuông. Căn hai phòng ngủ khoảng 60 đến 70 mét vuông, căn hai phòng ngủ cộng một khoảng 68 đến 76 mét vuông. Căn "
            "ba phòng ngủ khoảng 85 đến 100 mét vuông, nằm ở các góc tòa, nhiều căn có hai mặt nhìn ra biển hồ.\n\n"
            "Căn hộ được thiết kế trần cao, cửa kính lớn, phòng khách và bếp mở. Căn từ hai phòng ngủ trở lên có hai phòng vệ "
            "sinh.\n\n"
            "Hướng ban công chủ yếu là Đông và Tây; các căn ban công hướng Đông nhìn ra biển hồ được định giá cao hơn.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tiến độ The Bayfront",
            "The Bayfront đang trong quá trình xây dựng, dự kiến bàn giao vào quý 4 năm 2027. Tiến độ thực tế có thể thay đổi "
            "theo công trường và sẽ được chủ đầu tư thông báo.\n\n"
            "Căn hộ dự kiến bàn giao theo tiêu chuẩn nội thất liền tường: sàn gỗ, trần thạch cao, điều hòa, tủ bếp và thiết bị "
            "bếp, thiết bị vệ sinh, bình nóng lạnh, hệ thống chiếu sáng, khóa cửa điện tử. Danh mục vật liệu chi tiết được ghi "
            "trong phụ lục hợp đồng mua bán.\n\n"
            "Khách hàng mua căn hộ đang xây dựng thanh toán theo tiến độ, chỉ phải thanh toán phần lớn giá trị khi nhận bàn giao. "
            "Đây là lợi thế về dòng tiền so với mua căn đã hoàn thiện.\n\n"
            "Khi tư vấn, cần nói rõ đây là sản phẩm hình thành trong tương lai, không có căn thực tế để xem, chỉ có nhà mẫu và "
            "tài liệu thiết kế.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Bayfront",
            "Căn hộ The Bayfront là nhà ở hình thành trong tương lai, được chủ đầu tư bán theo quy định về kinh doanh bất động "
            "sản. Hình thức sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Khách hàng ký văn bản thỏa thuận và hợp đồng mua bán với chủ đầu tư, thanh toán theo tiến độ trong chính sách bán "
            "hàng. Hợp đồng mua bán nhà ở hình thành trong tương lai cần có bảo lãnh của ngân hàng theo quy định.\n\n"
            "Sổ hồng được cấp sau khi bàn giao và chủ đầu tư hoàn thành các thủ tục với cơ quan nhà nước. Thời gian cấp sổ cụ "
            "thể chưa xác định.\n\n"
            "Mọi thông tin pháp lý chi tiết cần được Sales cung cấp bằng văn bản chính thức của chủ đầu tư.",
        ),
        "community": (
            "Đối tượng phù hợp với The Bayfront",
            "The Bayfront phù hợp với khách hàng muốn sở hữu căn hộ mới nhất trong đại đô thị, ưu tiên cảnh quan biển hồ và có "
            "thể chờ đến cuối năm 2027 để nhận nhà.\n\n"
            "Phân khu cũng hấp dẫn nhà đầu tư trung hạn nhờ thanh toán theo tiến độ, giá niêm yết từ chủ đầu tư và vị trí gần biển "
            "hồ, nơi có nhu cầu thuê nghỉ dưỡng ngắn ngày vào mùa hè. Tuy nhiên mọi khoản đầu tư đều có rủi ro, không thể cam kết "
            "mức tăng giá hay lợi nhuận.\n\n"
            "Gia đình cần nhà ở ngay nên cân nhắc các phân khu đã bàn giao. Khách có ngân sách hạn chế có thể tham khảo The "
            "Sapphire hoặc The Pavilion.\n\n"
            "Điểm cần cân nhắc là thời gian chờ bàn giao, rủi ro chậm tiến độ và môi trường công trường trong giai đoạn xây dựng.",
        ),
    },
    "the-zurich": {
        "overview": (
            "Tổng quan phân khu The Zurich",
            "The Zurich là tiểu khu căn hộ đầu tiên thuộc phân khu The Metropolitan của Vinhomes Ocean Park. Phân khu được quy "
            "hoạch theo phong cách kiến trúc Thụy Sỹ với cảm hứng từ “giá trị vô giá của thời gian”, biểu tượng là tháp đồng hồ "
            "và quảng trường Thụy Sỹ ở trung tâm.\n\n"
            "Trong bộ dữ liệu này, The Zurich gồm ba tòa ZR1, ZR2 và ZR3, mỗi tòa cao khoảng 29 tầng, mỗi tầng 16 căn. Phân khu "
            "đã bàn giao từ tháng 8 năm 2025.\n\n"
            "Khi mở bán, quỹ căn sơ cấp của The Zurich đã được bán hết từ chủ đầu tư. Hiện tại giao dịch tại đây là mua bán lại "
            "từ chủ nhà, giá rao bán tham khảo thay đổi theo từng căn.\n\n"
            "The Zurich phù hợp với khách hàng muốn sản phẩm mới bàn giao, phong cách châu Âu thanh lịch, gần trường quốc tế "
            "Brighton College và trung tâm của The Metropolitan.",
        ),
        "location": (
            "Vị trí phân khu The Zurich",
            "The Zurich nằm trong cụm The Metropolitan, được xem là “quận trung tâm” của đại đô thị, gần trục đường Lý Thánh Tông "
            "và các tuyến đường nội khu chính.\n\n"
            "Phân khu được bao quanh bởi hệ thống giáo dục chất lượng cao: trường quốc tế Brighton College, trường liên cấp "
            "Vinschool và các trường mầm non. Từ The Zurich, cư dân đi bộ khoảng năm phút tới khu trường học, khoảng mười phút đi "
            "xe buýt điện tới hồ Ngọc Trai và Vincom Mega Mall.\n\n"
            "Hệ thống xe buýt điện VinBus có điểm dừng gần phân khu, kết nối tới các khu vực khác trong đại đô thị và vào nội "
            "thành. Ra bên ngoài, cư dân dùng đường Lý Thánh Tông để ra Quốc lộ 5 và cao tốc Hà Nội – Hải Phòng.\n\n"
            "Các căn ở mặt hướng về quảng trường Thụy Sỹ và hồ cảnh quan Geneva có tầm nhìn đẹp hơn các căn hướng ra đường.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Zurich",
            "Biểu tượng của The Zurich là tháp đồng hồ và quảng trường Thụy Sỹ, nơi tổ chức các hoạt động cộng đồng và chụp ảnh. "
            "Bên cạnh là hồ cảnh quan Geneva với đường dạo bộ và các tiểu cảnh châu Âu.\n\n"
            "Phân khu có bể bơi ngoài trời, phòng gym, spa, sân chơi trẻ em, vườn nướng BBQ và các khu thể thao nhỏ. Sảnh các tòa "
            "được thiết kế sang trọng, có hệ thống thang máy tốc độ cao và thiết bị nhà thông minh trong căn hộ.\n\n"
            "Ngoại khu, The Zurich gần trường quốc tế Brighton College, trường Vinschool và trường liên cấp Deway. Cư dân sử dụng "
            "chung hồ Ngọc Trai, biển hồ nhân tạo, Vinmec, VinUni, Vincom Mega Mall và các tuyến xe buýt điện.\n\n"
            "Khu thương mại tầng đế đang dần được lấp đầy với cửa hàng tiện lợi, cà phê và nhà hàng.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Zurich",
            "Kiến trúc The Zurich theo phong cách Thụy Sỹ châu Âu: mặt đứng thanh lịch, gam màu trang nhã, chi tiết trang trí "
            "tinh tế, kết hợp không gian xanh trong nội khu.\n\n"
            "Mỗi tầng có 16 căn hộ. Căn studio có diện tích thông thủy khoảng 27 đến 34 mét vuông. Căn một phòng ngủ khoảng 41 "
            "đến 47 mét vuông. Căn hai phòng ngủ khoảng 56 đến 72 mét vuông, căn hai phòng ngủ cộng một khoảng 63 đến 75 mét vuông. "
            "Căn ba phòng ngủ khoảng 85 đến 100 mét vuông.\n\n"
            "Căn hộ được thiết kế tối ưu công năng, cửa sổ kính và cửa ban công rộng giúp mọi phòng đều đón ánh sáng tự nhiên. "
            "Căn hai phòng ngủ trở lên có hai phòng vệ sinh.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc; căn góc có thêm mặt thoáng.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tình trạng The Zurich",
            "The Zurich đã bàn giao từ tháng 8 năm 2025. Căn hộ được bàn giao theo tiêu chuẩn nội thất liền tường: sàn gỗ, trần "
            "thạch cao, điều hòa, tủ bếp và thiết bị bếp, thiết bị vệ sinh cao cấp, bình nóng lạnh, hệ thống chiếu sáng, khóa cửa "
            "điện tử và một số thiết bị nhà thông minh.\n\n"
            "Do mới bàn giao khoảng một năm, nhiều căn vẫn còn trong thời gian bảo hành của chủ đầu tư. Một phần chủ nhà đã vào ở, "
            "một phần đang hoàn thiện nội thất để cho thuê hoặc bán lại.\n\n"
            "Người mua lại nên kiểm tra biên bản bàn giao, thời hạn bảo hành và tình trạng thanh toán của chủ nhà với chủ đầu "
            "tư.\n\n"
            "Các tiện ích nội khu chính như quảng trường, hồ cảnh quan, bể bơi đã đưa vào sử dụng.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Zurich",
            "Căn hộ The Zurich là căn hộ chung cư thương mại, sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Vì mới bàn giao năm 2025, phần lớn căn hộ đang trong quá trình chủ đầu tư làm thủ tục cấp sổ hồng. Giao dịch thứ cấp "
            "hiện chủ yếu là chuyển nhượng hợp đồng mua bán có xác nhận của chủ đầu tư.\n\n"
            "Khi chuyển nhượng, người mua cần kiểm tra hợp đồng gốc, các đợt đã thanh toán, khoản vay ngân hàng và chi phí chuyển "
            "nhượng theo quy định của chủ đầu tư.\n\n"
            "Thời điểm cấp sổ cụ thể cần được Sales cập nhật.",
        ),
        "community": (
            "Cộng đồng và đối tượng phù hợp với The Zurich",
            "Cư dân The Zurich chủ yếu là gia đình trẻ và trung lưu, nhiều gia đình có con theo học tại Brighton College và "
            "Vinschool. Cộng đồng đang hình thành, không khí yên tĩnh hơn các phân khu bàn giao sớm.\n\n"
            "Phân khu phù hợp với gia đình ưu tiên giáo dục, người yêu thích phong cách châu Âu và khách hàng muốn sản phẩm mới "
            "bàn giao nhưng không muốn chờ xây dựng.\n\n"
            "So với The Beverly và The London trong cùng cụm The Metropolitan, The Zurich bàn giao sớm hơn nên tiện ích và cộng "
            "đồng ổn định hơn. Vì quỹ căn sơ cấp đã hết, khách chỉ có thể mua lại với giá do chủ nhà đặt.\n\n"
            "Điểm cần cân nhắc là khu thương mại chưa sầm uất và một số khu vực xung quanh vẫn đang hoàn thiện.",
        ),
    },
    "the-beverly": {
        "overview": (
            "Tổng quan phân khu The Beverly",
            "The Beverly là tiểu khu căn hộ thứ hai thuộc phân khu The Metropolitan, được mở bán sau The Zurich. Phân khu mang "
            "phong cách American Glory Living, được giới thiệu là “mảnh ghép chất Mỹ” duy nhất tại khu trung tâm Ocean Park.\n\n"
            "The Beverly gồm bốn tòa BE1, BE2, BE3 và BE4, mỗi tòa cao khoảng 32 tầng. Tòa BE1 có 22 căn mỗi tầng với tám thang "
            "máy, các tòa còn lại có 18 căn mỗi tầng. Phân khu vừa được bàn giao vào quý 3 năm 2026.\n\n"
            "Sản phẩm đa dạng gồm studio, một phòng ngủ, hai phòng ngủ, hai phòng ngủ cộng một và ba phòng ngủ, bàn giao nội thất "
            "liền tường. Giao dịch hiện nay gồm cả mua lại từ khách hàng đầu tiên và một phần quỹ căn còn lại.\n\n"
            "The Beverly phù hợp với khách trẻ năng động, gia đình yêu thích phong cách sống phóng khoáng và tiện ích giải trí "
            "kiểu Mỹ.",
        ),
        "location": (
            "Vị trí phân khu The Beverly",
            "The Beverly nằm ở khu trung tâm của đại đô thị trong cụm The Metropolitan, phía Tây Bắc gần công viên hồ San Hô, "
            "nối tiếp The Zurich.\n\n"
            "Từ The Beverly, cư dân đi bộ vài phút tới các công viên tiện ích có sân thể thao và sân chơi, khoảng mười phút đi xe "
            "buýt điện tới hồ Ngọc Trai, biển hồ nhân tạo và Vincom Mega Mall. Trường liên cấp Vinschool và trường Deway nằm "
            "gần phân khu.\n\n"
            "Ra bên ngoài, cư dân dùng đường Lý Thánh Tông để kết nối với Quốc lộ 5 và cao tốc Hà Nội – Hải Phòng. Hệ thống xe "
            "buýt điện có điểm dừng ngay trong khu vực.\n\n"
            "Các căn hướng về công viên hồ San Hô có cảnh quan thoáng, các căn ở mặt còn lại nhìn vào nội khu hoặc hướng thành "
            "phố.",
        ),
        "amenities": (
            "Tiện ích nội khu và ngoại khu The Beverly",
            "Tiện ích nổi bật của The Beverly là bể bơi Santa Monica phong cách California, quảng trường Beverly với đài phun "
            "nước, vườn đọc sách, sân chơi sắc màu và sân chơi trẻ em.\n\n"
            "Bên trong các tòa có phòng gym kèm phòng xông hơi, game room, kid corner và sảnh cư dân. Phân khu có hệ thống công "
            "viên tiện ích với sân thể thao và lối dạo bộ.\n\n"
            "Ngoại khu, cư dân The Beverly sử dụng chung bộ đôi hồ Ngọc Trai và biển hồ nhân tạo, Vinmec, VinUni, Vinschool, "
            "trường Deway, Vincom Mega Mall và các tuyến xe buýt điện của đại đô thị.\n\n"
            "Khu thương mại tầng đế đang trong giai đoạn lấp đầy sau bàn giao.",
        ),
        "design": (
            "Thiết kế và mặt bằng căn hộ The Beverly",
            "Kiến trúc The Beverly lấy cảm hứng từ phong cách Mỹ: mặt đứng hiện đại, nhiều mảng kính, gam màu tươi sáng và cảnh "
            "quan mang hơi hướng California.\n\n"
            "Căn studio có diện tích thông thủy khoảng 28 đến 35 mét vuông. Căn một phòng ngủ khoảng 43 đến 48 mét vuông. Căn hai "
            "phòng ngủ khoảng 54 đến 70 mét vuông, căn hai phòng ngủ cộng một khoảng 64 đến 75 mét vuông. Căn ba phòng ngủ khoảng "
            "81 đến 108 mét vuông.\n\n"
            "Tòa BE1 có mật độ 22 căn mỗi tầng nhưng được bố trí tám thang máy để giảm thời gian chờ. Các tòa BE2, BE3, BE4 có 18 "
            "căn mỗi tầng.\n\n"
            "Hướng ban công chủ yếu là Đông Nam và Tây Bắc; căn hướng về công viên hồ San Hô được định giá cao hơn.",
        ),
        "handover": (
            "Tiêu chuẩn bàn giao và tình trạng The Beverly",
            "The Beverly bàn giao vào quý 3 năm 2026. Căn hộ được bàn giao theo tiêu chuẩn nội thất liền tường: sàn gỗ, trần thạch "
            "cao, điều hòa, tủ bếp và thiết bị bếp, thiết bị vệ sinh, bình nóng lạnh, hệ thống chiếu sáng và khóa cửa điện tử.\n\n"
            "Do vừa bàn giao, nhiều căn hộ đang trong giai đoạn chủ nhà hoàn thiện nội thất, khu vực hành lang và thang máy có thể "
            "còn hoạt động thi công nội thất trong vài tháng đầu.\n\n"
            "Căn hộ vẫn trong thời gian bảo hành của chủ đầu tư. Người mua lại nên kiểm tra biên bản bàn giao và các lỗi đã được "
            "chủ đầu tư khắc phục hay chưa.\n\n"
            "Các tiện ích chính như bể bơi, quảng trường và sân chơi đã đưa vào sử dụng.",
        ),
        "legal": (
            "Pháp lý và quyền sở hữu tại The Beverly",
            "Căn hộ The Beverly là căn hộ chung cư thương mại, sở hữu lâu dài đối với người Việt Nam.\n\n"
            "Vì vừa bàn giao, căn hộ chưa được cấp sổ hồng; chủ đầu tư sẽ làm thủ tục cấp sổ sau khi hoàn tất các thủ tục pháp lý "
            "của dự án. Giao dịch thứ cấp được thực hiện bằng chuyển nhượng hợp đồng mua bán có xác nhận của chủ đầu tư.\n\n"
            "Với căn còn trong quỹ hàng, khách hàng ký hợp đồng mua bán trực tiếp với chủ đầu tư.\n\n"
            "Thời điểm cấp sổ cụ thể cần được Sales cập nhật.",
        ),
        "community": (
            "Cộng đồng và đối tượng phù hợp với The Beverly",
            "The Beverly thu hút người trẻ năng động, cặp vợ chồng mới cưới và gia đình trẻ thích phong cách sống phóng khoáng, "
            "nhiều tiện ích giải trí.\n\n"
            "Phân khu phù hợp với khách muốn sản phẩm mới bàn giao, tiêu chuẩn liền tường và mức giá ở tầm trung trong cụm "
            "The Metropolitan. Nhà đầu tư cũng quan tâm do nguồn cung căn studio và một phòng ngủ dồi dào.\n\n"
            "So với The Zurich, The Beverly mới hơn và có nhiều tiện ích giải trí hơn. So với The London, The Beverly có quy mô "
            "lớn hơn nên cộng đồng đông hơn.\n\n"
            "Điểm cần cân nhắc là mật độ căn hộ ở tòa BE1 cao và giai đoạn đầu sau bàn giao còn nhiều căn đang thi công nội thất.",
        ),
    },
}
