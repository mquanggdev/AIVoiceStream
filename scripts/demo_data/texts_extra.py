"""Đoạn bổ sung cho các bài knowledge_docs còn ngắn (mục tiêu ≥150 từ mỗi bài).

Khóa: (subdivision_slug, topic). Nội dung được nối vào cuối bài gốc.
Viết theo dạng các câu khách hay hỏi khi gọi điện tư vấn.
"""

EXTRA: dict[tuple[str, str], str] = {
    # ── Pháp lý ──────────────────────────────────────────────────────────────
    ("masteri-lakeside", "legal"): (
        "Khách hàng thường hỏi khi nào được ký hợp đồng mua bán. Theo lịch thanh toán, sau khi ký xác nhận đăng ký và văn "
        "bản thỏa thuận, khách ký hợp đồng mua bán ở đợt thứ hai. Từ thời điểm ký hợp đồng, quyền và nghĩa vụ của hai bên "
        "được ghi rõ, gồm tiến độ bàn giao, tiêu chuẩn vật liệu và mức phạt nếu chậm bàn giao. Khách muốn chuyển nhượng lại "
        "trước khi nhận nhà cần làm thủ tục chuyển nhượng hợp đồng có xác nhận của Masterise Homes và có thể phát sinh phí "
        "chuyển nhượng theo quy định của chủ đầu tư. Người nước ngoài mua căn hộ tại dự án được sở hữu theo hạn mức và thời "
        "hạn pháp luật cho phép."
    ),
    ("the-paris", "legal"): (
        "Nhiều khách hỏi mua căn The Paris có an toàn không khi dự án chưa bàn giao. Hợp đồng mua bán nhà ở hình thành trong "
        "tương lai phải có bảo lãnh của ngân hàng, nghĩa là nếu chủ đầu tư không bàn giao đúng cam kết, ngân hàng bảo lãnh có "
        "trách nhiệm hoàn trả khoản tiền khách đã thanh toán theo quy định. Khách nên yêu cầu bản sao thư bảo lãnh khi ký hợp "
        "đồng. Với khách muốn bán lại trước khi nhận nhà, có thể chuyển nhượng hợp đồng có xác nhận của chủ đầu tư. Sau khi "
        "bàn giao, khách đóng phần thanh toán còn lại và kinh phí bảo trì, chủ đầu tư làm thủ tục cấp sổ hồng."
    ),
    ("the-senique-hanoi", "legal"): (
        "Thỏa thuận ký quỹ là bước đặc thù của The Senique: khách ký quỹ có hoàn lại để giữ quyền mua căn, sau đó ký hợp đồng "
        "mua bán khi dự án đủ điều kiện. Nếu khách không tiếp tục trước khi ký hợp đồng, khoản ký quỹ được xử lý theo điều khoản "
        "đã thỏa thuận. Hợp đồng mua bán có bảo lãnh ngân hàng theo quy định. Vì dự án do CapitaLand Development phát triển, "
        "hồ sơ pháp lý và mẫu hợp đồng theo chuẩn của chủ đầu tư này, khách nên đọc kỹ các điều khoản về phí quản lý, quyền sử "
        "dụng tiện ích compound và quy định cho thuê lại căn hộ."
    ),
    ("the-palma", "legal"): (
        "Khi mua The Palma, khách ký văn bản thỏa thuận trong vòng 14 ngày kể từ đặt cọc, sau đó ký hợp đồng mua bán. Hợp đồng "
        "có bảo lãnh ngân hàng cho nhà ở hình thành trong tương lai. Các căn ba phòng ngủ góc có thang máy riêng, quyền sử dụng "
        "thang máy riêng được ghi trong phụ lục hợp đồng. Khách muốn chuyển nhượng trước bàn giao cần có xác nhận của Masterise "
        "Homes. Sổ hồng được cấp sau bàn giao; thời gian cụ thể phụ thuộc thủ tục với cơ quan nhà nước nên Sales sẽ cập nhật khi "
        "có thông tin chính thức."
    ),
    ("the-london", "legal"): (
        "Khách hỏi mua lại căn The London lúc này cần giấy tờ gì. Người bán cung cấp hợp đồng mua bán gốc, biên bản bàn giao, "
        "các phiếu thu đã thanh toán và giấy tờ tùy thân. Hai bên ký văn bản chuyển nhượng hợp đồng tại văn phòng công chứng, "
        "sau đó nộp hồ sơ để chủ đầu tư xác nhận. Nếu căn đang thế chấp ngân hàng, cần tất toán hoặc làm thủ tục chuyển khoản vay "
        "trước. Thuế thu nhập cá nhân 2% do bên bán chịu theo quy định, trừ khi hai bên thỏa thuận khác."
    ),
    ("masteri-waterfront", "legal"): (
        "Với căn đã có sổ, thủ tục mua lại gồm ký hợp đồng mua bán công chứng, kê khai thuế, nộp lệ phí trước bạ và đăng ký "
        "sang tên, thường mất khoảng hai đến bốn tuần. Với căn chưa có sổ, hai bên chuyển nhượng hợp đồng mua bán có xác nhận "
        "của Masterise Homes. Khách nên kiểm tra các khoản phí quản lý còn nợ và tình trạng thế chấp của căn hộ trước khi đặt "
        "cọc. Sales có thể hỗ trợ kiểm tra hồ sơ cùng khách."
    ),
    ("the-beverly", "legal"): (
        "Với căn mua từ quỹ hàng chủ đầu tư, khách ký hợp đồng mua bán trực tiếp, thanh toán theo chính sách hiện hành và nhận "
        "bàn giao ngay sau khi thanh toán đủ theo quy định. Với căn mua lại, khách cần kiểm tra hợp đồng gốc, lịch sử thanh toán "
        "và khoản vay ngân hàng của chủ nhà. Phí chuyển nhượng hợp đồng theo quy định của chủ đầu tư. Sổ hồng sẽ được cấp cho "
        "người đứng tên hợp đồng tại thời điểm chủ đầu tư làm thủ tục."
    ),
    ("the-zurich", "legal"): (
        "Một câu hỏi thường gặp là mua căn Zurich chưa có sổ có rủi ro không. Giao dịch chuyển nhượng hợp đồng có xác nhận của "
        "chủ đầu tư là hình thức hợp pháp; sau khi chuyển nhượng, người mua mới được ghi nhận là bên mua trong hợp đồng và sẽ "
        "đứng tên sổ hồng. Khách cần đảm bảo chủ nhà đã thanh toán đủ các đợt theo hợp đồng và không có tranh chấp. Thời gian "
        "chủ đầu tư xác nhận chuyển nhượng thường khoảng một đến hai tuần."
    ),
    ("the-pavilion", "legal"): (
        "Khách mua lại căn The Pavilion nên hỏi chủ nhà căn đã có sổ hay chưa. Nếu đã có sổ, giao dịch công chứng như căn hộ "
        "thông thường. Nếu chưa, chuyển nhượng hợp đồng có xác nhận của chủ đầu tư. Thời gian xử lý hồ sơ cấp sổ phụ thuộc cơ "
        "quan nhà nước, Sales sẽ cập nhật tiến độ cho từng tòa P1, P2 khi khách quan tâm căn cụ thể."
    ),
    ("the-zenpark", "legal"): (
        "Phí và thuế khi mua lại căn Zenpark có sổ gồm thuế thu nhập cá nhân của bên bán, lệ phí trước bạ của bên mua, phí công "
        "chứng và phí thẩm định hồ sơ."
    ),
    ("the-bayfront", "legal"): (
        "Khách đầu tư có thể chuyển nhượng hợp đồng trước khi nhận nhà, có xác nhận của chủ đầu tư và phí theo quy định."
    ),
    # ── Bàn giao ─────────────────────────────────────────────────────────────
    ("masteri-waterfront", "handover"): (
        "Khi nhận căn mua lại tại Masteri Waterfront, khách nên kiểm tra hoạt động của điều hòa, bình nóng lạnh, khóa điện tử, "
        "tình trạng sàn gỗ và chống thấm khu vệ sinh. Nếu căn còn trong thời gian bảo hành, chủ nhà có thể đề nghị chủ đầu tư "
        "sửa chữa trước khi bàn giao cho người mua. Với căn đã có nội thất đầy đủ, hai bên nên lập danh mục đồ đạc kèm theo hợp "
        "đồng để tránh tranh chấp. Phí quản lý của dự án cao hơn mặt bằng chung do tiêu chuẩn dịch vụ của Masterise Homes."
    ),
    ("the-senique-hanoi", "handover"): (
        "Căn bốn phòng ngủ và ba phòng ngủ diện tích lớn của The Senique có phòng giúp việc và kho, được bàn giao hoàn thiện như "
        "các phòng khác. Khu bếp được thiết kế bếp kín và bếp mở ở căn lớn, phù hợp thói quen nấu nướng của gia đình Việt. Khách "
        "nhận nhà sẽ được hướng dẫn sử dụng hệ thống khóa thông minh, thẻ ra vào compound và ứng dụng cư dân. Vì một phần quỹ căn "
        "chưa mở bán, khách quan tâm có thể đăng ký để Sales thông báo khi có đợt mở bán mới."
    ),
    ("the-london", "handover"): (
        "Với khách mua căn còn trong quỹ hàng chủ đầu tư, sau khi thanh toán theo chính sách, chủ đầu tư hẹn lịch bàn giao trong "
        "khoảng hai đến bốn tuần. Khách kiểm tra căn theo biên bản, ghi nhận lỗi nếu có để được khắc phục trong thời gian bảo hành. "
        "Khách mua lại từ chủ nhà nên kiểm tra căn đã được hoàn thiện nội thất chưa, và các hạng mục chủ nhà tự sửa có ảnh hưởng "
        "đến kết cấu hoặc bảo hành hay không."
    ),
    ("the-palma", "handover"): (
        "Các thương hiệu thiết bị cụ thể của The Palma được ghi trong phụ lục vật liệu của hợp đồng mua bán. Căn ba phòng ngủ góc "
        "có thang máy riêng dẫn thẳng vào sảnh căn hộ. Khách mua căn hình thành trong tương lai không xem được căn thực tế nhưng có "
        "thể tham quan nhà mẫu để cảm nhận vật liệu, ánh sáng và bố cục. Phí quản lý dự kiến cao hơn các phân khu khác do tiêu "
        "chuẩn dịch vụ hạng sang."
    ),
    ("the-paris", "handover"): (
        "Khách mua The Paris lúc này chỉ phải thanh toán khoảng ba mươi phần trăm trước khi bàn giao theo lịch thanh toán chuẩn, "
        "phần lớn còn lại thanh toán khi nhận nhà, phù hợp với khách cần thời gian chuẩn bị tài chính. Nếu chọn gói vay, chủ đầu "
        "tư hỗ trợ lãi suất đến khi bàn giao theo chính sách hiện hành. Sau khi nhận nhà, khách có thể đăng ký thi công nội thất "
        "bổ sung theo quy định của ban quản lý tòa nhà."
    ),
    ("masteri-lakeside", "handover"): (
        "Khách mua Masteri Lakeside lúc này có thời gian chờ ngắn vì dự án sắp bàn giao. Đợt thanh toán lớn nhất là khi nhận bàn "
        "giao, gồm phần giá trị còn lại, thuế giá trị gia tăng và kinh phí bảo trì. Khách nên chuẩn bị tài chính hoặc hồ sơ vay "
        "ngân hàng trước thời điểm này."
    ),
    ("the-beverly", "handover"): (
        "Thời gian thi công nội thất trong tòa được ban quản lý quy định theo khung giờ để hạn chế tiếng ồn cho cư dân đã vào ở."
    ),
    ("the-zurich", "handover"): (
        "Khách có thể xem căn thực tế tại The Zurich bằng cách đặt lịch với Sales để được hướng dẫn vào tòa."
    ),
    # ── Tiện ích ─────────────────────────────────────────────────────────────
    ("masteri-lakeside", "amenities"): (
        "Bể bơi bốn mùa có hệ thống nước ấm giúp cư dân bơi được cả mùa đông. Khu vui chơi trẻ em được bố trí gần sảnh, thuận tiện "
        "cho phụ huynh trông con. Lounge cư dân là nơi tiếp khách, làm việc hoặc tổ chức sinh nhật nhỏ. Vì nằm gần khu phố thương "
        "mại Biển Hồ, cư dân có nhiều lựa chọn nhà hàng, quán cà phê và cửa hàng tiện lợi chỉ cách vài phút đi bộ. Những ai thích "
        "chạy bộ có thể ra hồ Ngọc Trai hoặc chạy quanh hồ điều hòa của dự án."
    ),
    ("the-beverly", "amenities"): (
        "Bể bơi Santa Monica của The Beverly có khu bể nông cho trẻ em và khu ghế nằm thư giãn. Game room phù hợp với thanh thiếu "
        "niên và người trẻ, kid corner dành cho trẻ nhỏ chơi trong nhà vào những ngày mưa. Vườn đọc sách là không gian yên tĩnh "
        "trong nội khu. Quảng trường Beverly thường được dùng tổ chức sự kiện cộng đồng dịp lễ Tết."
    ),
    ("the-senique-hanoi", "amenities"): (
        "Bể bơi dài 50 mét của The Senique đủ tiêu chuẩn cho người tập bơi nghiêm túc. Vì là compound khép kín, tiện ích chỉ dành "
        "cho cư dân, không mở cho người ngoài, giúp không gian luôn yên tĩnh và riêng tư. Hầm đỗ xe thông minh có hệ thống nhận "
        "diện biển số, phù hợp với gia đình có ô tô."
    ),
    ("masteri-waterfront", "amenities"): (
        "Sảnh lounge phong cách khách sạn là điểm cộng lớn khi tiếp khách. Bể bơi bốn mùa trong nhà sử dụng được quanh năm. Cư dân "
        "có thể đi bộ ra hồ Ngọc Trai để chạy bộ buổi sáng, hoặc dạo biển hồ vào cuối tuần."
    ),
    ("the-palma", "amenities"): (
        "Bể bơi tràn bờ trên cao hướng về biển hồ là tiện ích đặc trưng của The Palma. Vườn trên cao là không gian thư giãn với tầm "
        "nhìn rộng. Spa và phòng gym được thiết kế theo chuẩn khách sạn, phục vụ riêng cho cư dân hai tòa."
    ),
    ("the-paris", "amenities"): (
        "Phòng làm việc chung và lounge âm nhạc phù hợp với người làm việc tự do hoặc làm việc từ xa. Phòng pilates và yoga có giáo "
        "viên theo lịch của ban quản lý."
    ),
    ("the-london", "amenities"): (
        "Cư dân đặt lịch phòng karaoke và phòng giải trí qua ứng dụng cư dân."
    ),
    # ── Thiết kế ─────────────────────────────────────────────────────────────
    ("masteri-lakeside", "design"): (
        "Căn studio của Masteri Lakeside nhỏ gọn, thiết kế thông minh với khu ngủ, khu bếp và vệ sinh khép kín, phù hợp người độc "
        "thân hoặc cho thuê. Căn một phòng ngủ cộng một có thêm không gian đa năng có thể làm phòng làm việc. Căn hai phòng ngủ cộng "
        "một phù hợp gia đình có một con nhỏ và cần thêm phòng cho ông bà hoặc người giúp việc. Căn ba phòng ngủ nằm ở góc tòa, có "
        "hai mặt thoáng và tầm nhìn rộng."
    ),
    ("the-senique-hanoi", "design"): (
        "Căn hai phòng ngủ của The Senique có biên độ diện tích rộng, từ căn nhỏ gọn cho vợ chồng trẻ đến căn lớn có thể bố trí "
        "thêm phòng làm việc. Căn bốn phòng ngủ ở góc tòa có ba phòng vệ sinh, phù hợp gia đình ba thế hệ. Tầng cao của tòa SQ1 có "
        "tầm nhìn rộng ra hồ cảnh quan và toàn cảnh khu đô thị."
    ),
    ("masteri-waterfront", "design"): (
        "Căn hai phòng ngủ cộng một là loại căn được ưa chuộng nhất vì linh hoạt cho gia đình trẻ. Căn ba phòng ngủ ở các góc tòa "
        "H1 và H2 thường có hai mặt nhìn hồ, là nhóm căn hiếm hàng trên thị trường thứ cấp."
    ),
    ("the-paris", "design"): (
        "Căn một phòng ngủ cộng một có thêm phòng nhỏ phù hợp làm phòng làm việc. Căn ba phòng ngủ ở góc có hai mặt thoáng."
    ),
    ("the-palma", "design"): (
        "Căn studio và một phòng ngủ phù hợp chuyên gia thuê dài hạn; căn hai phòng ngủ cộng một và ba phòng ngủ dành cho gia đình."
    ),
    ("the-london", "design"): (
        "Căn góc ba phòng ngủ có hai mặt thoáng, phù hợp gia đình đông người."
    ),
    ("the-beverly", "design"): (
        "Căn hai phòng ngủ cộng một phù hợp gia đình trẻ cần thêm một phòng nhỏ làm phòng làm việc."
    ),
    ("the-zurich", "design"): (
        "Căn góc ba phòng ngủ có hai mặt thoáng."
    ),
    # ── Cộng đồng ────────────────────────────────────────────────────────────
    ("masteri-lakeside", "community"): (
        "Khi tư vấn, nên hỏi khách mua để ở hay đầu tư. Khách mua ở thường chọn căn hai phòng ngủ hoặc hai phòng ngủ cộng một hướng "
        "hồ cảnh quan. Khách đầu tư cho thuê thường chọn studio hoặc một phòng ngủ cộng một do vốn đầu tư thấp hơn. Khách cần "
        "dòng tiền linh hoạt có thể tận dụng chính sách chiết khấu thanh toán sớm hoặc thanh toán theo tiến độ chuẩn."
    ),
    ("masteri-waterfront", "community"): (
        "Khách thuê tại Masteri Waterfront thường là giảng viên VinUni, bác sĩ Vinmec và chuyên gia các công ty nước ngoài, có yêu "
        "cầu cao về nội thất và dịch vụ. Căn view hồ có giá thuê cao hơn căn view nội khu."
    ),
    ("the-senique-hanoi", "community"): (
        "Khách hàng quan tâm Senique thường hỏi về phí quản lý và chi phí sinh hoạt; mức phí cao hơn tương xứng với dịch vụ compound "
        "và an ninh riêng."
    ),
    ("the-paris", "community"): (
        "Khách chưa quyết định giữa The Paris và các phân khu đã bàn giao nên cân nhắc thời điểm cần nhận nhà và dòng tiền."
    ),
    ("the-palma", "community"): (
        "Khách hàng nên tham quan nhà mẫu để cảm nhận chất lượng vật liệu trước khi quyết định."
    ),
    ("the-london", "community"): (
        "Khách có con nhỏ thường chọn căn hướng nội khu để yên tĩnh và gần sân chơi."
    ),
    ("the-beverly", "community"): (
        "Khách đầu tư có thể cân nhắc căn studio ở các tòa BE2 đến BE4 có mật độ thấp hơn BE1."
    ),
    ("the-zurich", "community"): (
        "Khách nên đặt lịch xem căn thực tế để đánh giá ánh sáng và tầm nhìn."
    ),
    ("the-pavilion", "community"): (
        "Khách có thể xem căn thực tế trước khi quyết định."
    ),
    # ── Vị trí ───────────────────────────────────────────────────────────────
    ("the-paris", "location"): (
        "Với gia đình có con học Vinschool hoặc Deway, quãng đường đưa đón ngắn là điểm cộng. Người đi làm vào nội thành có thể dùng "
        "xe buýt điện kết nối hoặc tự lái xe qua cầu Thanh Trì, cầu Vĩnh Tuy."
    ),
    ("masteri-lakeside", "location"): (
        "Người đi làm có thể dùng xe buýt điện VinBus có điểm dừng gần dự án, hoặc tự lái xe ra Quốc lộ 5 trong vài phút."
    ),
    ("masteri-waterfront", "location"): (
        "Vị trí trung tâm giúp cư dân đi bộ tới hầu hết tiện ích chính mà không cần dùng xe."
    ),
    ("the-senique-hanoi", "location"): (
        "Vị trí trung tâm giúp cư dân di chuyển nhanh tới mọi khu vực trong đại đô thị."
    ),
    ("the-palma", "location"): (
        "Đây là một trong số ít phân khu có thể đi bộ ra bãi cát biển hồ."
    ),
    ("the-beverly", "location"): (
        "Người đi làm có thể dùng xe buýt điện VinBus vào nội thành."
    ),
    # ── Tổng quan ────────────────────────────────────────────────────────────
    ("masteri-lakeside", "overview"): (
        "Khách hàng quan tâm có thể hỏi về bảng giá, lịch thanh toán và chiết khấu thanh toán sớm hiện hành."
    ),
}
