from pathlib import Path

code = (Path(__file__).parent / "google_drive_appscript" / "Code.gs").read_text(encoding="utf-8")

def test_adaptive_chunk_transport():
    assert "RECOMMENDED_CHUNK_BYTES = 2 * 1024 * 1024" in code
    assert "expectedChunkSize" in code
    assert "transport_mismatch" in code
    assert "recommended_chunk_bytes" in code
    assert "blob.size" in code
    assert "const QUANTUM=262144" in code


def test_intermediate_chunk_quantum_and_final_exception():
    assert "const isFinalChunk = bytes.length === remaining" in code
    assert "!isFinalChunk && bytes.length % quantum !== 0" in code
