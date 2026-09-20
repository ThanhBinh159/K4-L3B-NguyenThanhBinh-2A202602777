from pathlib import Path
import subprocess
import sys

from bench import BENCHMARKS, DATA_DIR, run_benchmark


def main() -> None:
    assert len(BENCHMARKS) == 5
    assert {item["kind"] for item in BENCHMARKS} == {
        "số liệu",
        "điều kiện",
        "quy trình",
        "liệt kê",
        "lọc metadata",
    }
    assert any(item["metadata_filter"] == {"audience": "seller"} for item in BENCHMARKS)

    for item in BENCHMARKS:
        source = Path(DATA_DIR, f"{item['expected_doc_id']}.md").read_text(encoding="utf-8")
        assert item["evidence"] in source

    results = run_benchmark()
    assert len(results) == 5
    assert all(result["evidence_in_top_3"] for result in results)
    answer_markers = [
        "7–14 ngày làm việc",
        "Khác với mô tả",
        "trong vòng 6 ngày",
        "Tự sắp xếp",
        "Mã vận đơn hoặc thông tin vận chuyển",
    ]
    assert all(marker in result["agent_answer"] for marker, result in zip(answer_markers, results))
    assert all(
        marker in results[3]["agent_answer"]
        for marker in ("Đơn vị vận chuyển đến lấy hàng", "Trả hàng tại bưu cục", "Tự sắp xếp")
    )

    completed = subprocess.run(
        [sys.executable, "bench.py"],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert completed.returncode == 0, completed.stderr


if __name__ == "__main__":
    main()
    print("Benchmark verification passed: 5/5 expected documents in top-3.")
