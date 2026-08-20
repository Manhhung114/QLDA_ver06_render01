from legal_documents import load_google_search_config, google_browser_url, _web_result_doc, _score_web_doc

def main():
    cfg = load_google_search_config()
    assert google_browser_url("Thông tư 06/2021/TT-BXD").startswith("https://www.google.com/search?q=")
    d = _web_result_doc({"title":"Thông tư 06/2021/TT-BXD phân cấp công trình", "url":"https://example.com/a", "snippet":"Thông tư về phân cấp công trình", "engine":"Google"}, "Thông tư 06/2021/TT-BXD")
    assert d and "06/2021/TT-BXD" in d["number"]
    assert _score_web_doc(d, "Thông tư 06/2021/TT-BXD") > 0
    print("OK - Google integration offline", "configured=" + str(cfg.get("configured")))

if __name__ == "__main__": main()
