from pathlib import Path
import tempfile
import legal_documents as ld

sample1 = {
    "category": "Nghị định", "number": "06/2021/NĐ-CP",
    "title": "Quản lý chất lượng, thi công xây dựng và bảo trì công trình xây dựng",
    "issuer": "", "issue_date": "", "effective_date": "", "expiry_date": "",
    "status": "Nguồn tham khảo TVPL - cần đối chiếu nguồn chính thức",
    "field": "QLDA xây dựng / tra cứu pháp luật",
    "source_name": ld.TVPL_SOURCE_NAME,
    "source_url": "https://www.thuvienphapluat.vn/van-ban/Xay-dung-Do-thi/nghi-dinh-06-2021-ND-CP.aspx?utm_source=test",
    "is_draft": 0, "note": ""
}
sample2 = dict(sample1)
sample2["source_url"] = "https://thuvienphapluat.vn/van-ban/Xay-dung-Do-thi/nghi-dinh-06-2021-ND-CP.aspx"
sample2["issuer"] = "Chính phủ"
assert len(ld._dedupe_tvpl_docs([sample1, sample2])) == 1

p = Path(tempfile.gettempdir()) / "qlda_v409_tvpl_test.db"
p.unlink(missing_ok=True)
repo = ld.LegalRepository(p)
repo.upsert_many([{
    "category": "Nghị định", "number": "06/2021/NĐ-CP",
    "title": "Nghị định quản lý chất lượng thi công xây dựng",
    "issuer": "Chính phủ", "issue_date": "2021-01-26", "effective_date": "2021-01-26",
    "expiry_date": "", "status": "Nguồn chính thức - cần đối chiếu hiệu lực",
    "field": "QLDA xây dựng", "source_name": "VBPL / Cổng Chính phủ",
    "source_url": "https://vanban.chinhphu.vn/test-06-2021", "is_draft": 0, "note": ""
}])
repo.upsert_many([sample2])
assert repo.crosscheck_tvpl_with_official() == 1
rows = repo.list_documents(source=ld.TVPL_SOURCE_NAME)
assert len(rows) == 1 and "Đã đối chiếu số hiệu" in rows[0]["note"]

orig = ld.fetch_thuvienphapluat_qlda
try:
    ld.fetch_thuvienphapluat_qlda = lambda: [sample2]
    result = ld.sync_source(repo, "tvpl")
    assert result["source"] == ld.TVPL_SOURCE_NAME
    assert result.get("crosschecked", 0) >= 1
finally:
    ld.fetch_thuvienphapluat_qlda = orig

print("TVPL_SYNC_TEST_OK")
