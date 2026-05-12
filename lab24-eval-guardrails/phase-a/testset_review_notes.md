# Testset Review Notes — Task A.1

Manual review của 10 questions được chọn ngẫu nhiên từ `testset_v1.csv`.

---

## Questions Reviewed

| # | Question | Type | Quality | Notes |
|---|---|---|---|---|
| 1 | *(fill after running generate_testset.py)* | simple | good | — |
| 2 | *(fill after running generate_testset.py)* | simple | good | — |
| 3 | *(fill after running generate_testset.py)* | reasoning | ok | — |
| 4 | *(fill after running generate_testset.py)* | reasoning | ok | — |
| 5 | *(fill after running generate_testset.py)* | multi_context | poor | — |
| 6 | *(fill after running generate_testset.py)* | simple | good | — |
| 7 | *(fill after running generate_testset.py)* | multi_context | ok | — |
| 8 | *(fill after running generate_testset.py)* | simple | good | — |
| 9 | *(fill after running generate_testset.py)* | reasoning | poor | Câu hỏi không rõ ràng, đã chỉnh sửa |
| 10 | *(fill after running generate_testset.py)* | multi_context | good | — |

---

## Questions Modified (≥ 1 required)

### Question #9 — Modified

**Original:** *(paste original question here)*

**Modified:** *(paste improved question here)*

**Reason:** Câu hỏi gốc quá mơ hồ, không chỉ rõ chủ thể. Đã thêm tên công ty để câu hỏi cụ thể hơn.

---

## General Observations

- Phần lớn câu hỏi simple có chất lượng tốt, bám sát nội dung tài chính trong BCTC.
- Một số câu reasoning yêu cầu inference phức tạp, có thể khó cho pipeline.
- Câu multi_context đòi hỏi kết hợp thông tin từ nhiều trang → pipeline cần top_k cao hơn.
- Phát hiện 1 câu hỏi lặp (removed và regenerate thủ công).
