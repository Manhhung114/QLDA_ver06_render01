from legal_documents import _extract_doc_number, _web_result_doc, _score_web_doc


def main():
    q = "Thông tư 06/2021/TT-BXD phân cấp công trình xây dựng"
    assert _extract_doc_number(q) == "06/2021/TT-BXD"
    assert _extract_doc_number("TCVN 5575:2024 Thiết kế kết cấu thép") == "TCVN 5575:2024"
    d = _web_result_doc({
        "title": "Thông tư 06/2021/TT-BXD phân cấp công trình xây dựng",
        "url": "https://vanban.chinhphu.vn/test",
        "snippet": "Ban hành ngày 30/06/2021",
        "engine": "Bing",
    }, q)
    assert d and d["number"] == "06/2021/TT-BXD"
    assert "chính thức" in d["status"].lower()
    assert _score_web_doc(d, q) > 100
    print("GLOBAL_SEARCH_TEST_OK")


if __name__ == "__main__":
    main()
