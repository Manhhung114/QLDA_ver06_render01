from legal_documents import _web_result_doc, SPECIFIED_SEARCH_DOMAINS, REFERENCE_WEB_DOMAINS
assert "thuvienphapluat.vn" in SPECIFIED_SEARCH_DOMAINS
x=_web_result_doc({"title":"Thông tư 06/2021/TT-BXD phân cấp công trình xây dựng","url":"https://thuvienphapluat.vn/van-ban/Xay-dung-Do-thi/Thong-tu-06-2021-TT-BXD-phan-cap-cong-trinh-xay-dung-480818.aspx","snippet":"Số hiệu 06/2021/TT-BXD"}, "06/2021/TT-BXD")
assert x and "Thư Viện Pháp Luật" in x["source_name"]
assert "tham khảo" in x["status"].lower()
print("SPECIFIED_SITES_TEST_OK")
