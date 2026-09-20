from bench import BENCHMARKS, load_corpus, run_benchmark


def main() -> None:
    documents = load_corpus(strategy="fixed_size", chunk_size=300)
    assert len(documents) == 215
    assert all(len(document.content) <= 300 for document in documents)
    assert round(sum(len(document.content) for document in documents) / len(documents), 2) == 293.87

    results = run_benchmark(strategy="fixed_size", chunk_size=300)
    assert len(results) == len(BENCHMARKS) == 5
    assert all(result["expected_in_top_3"] for result in results)

    contexts = ["\n".join(item["content"] for item in result["top_3"]) for result in results]
    assert "7–14 ngày làm việc" not in contexts[0]
    assert all(marker in contexts[1] for marker in ("Khác với mô tả", "Tất cả sản phẩm"))
    assert "trong vòng 6 ngày" in contexts[2]
    assert "Đơn vị vận chuyển đến lấy hàng" in contexts[3]
    assert all(marker not in contexts[3] for marker in ("Trả hàng tại bưu cục", "Tự sắp xếp"))
    assert all(
        marker in contexts[4]
        for marker in ("Lý do khiếu nại rõ ràng", "Mã vận đơn hoặc thông tin vận chuyển")
    )
    assert "Bằng chứng cho thấy hàng hoàn bị sai" not in contexts[4]

    answers = [result["agent_answer"] for result in results]
    assert "7–14 ngày làm việc" not in answers[0]
    assert all(marker in answers[1] for marker in ("Khác với mô tả", "Tất cả sản phẩm"))
    assert "trong vòng 6 ngày" in answers[2]
    assert all(marker not in answers[3] for marker in ("Đơn vị vận chuyển đến lấy hàng", "Tự sắp xếp"))
    assert "Bằng chứng cho thấy hàng hoàn bị sai" not in answers[4]


if __name__ == "__main__":
    main()
    print("Fixed-size benchmark verification passed.")
