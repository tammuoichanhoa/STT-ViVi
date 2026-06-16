# STT_Vi

MVP boc bang ghi am tieng Viet dua tren `vinai/PhoWhisper-small`.

## Chuc nang hien tai

- Upload file audio/video qua web
- Chay transcript voi PhoWhisper tren CPU
- Xem ket qua ngay tren giao dien
- Tai ket qua duoi dang `txt`, `srt`, `json`

## Chay local

```bash
pip install -r requirements.txt
python main.py
```

Sau do mo `http://127.0.0.1:5000`.

## Luu y

- Model duoc load o lan request dau tien nen request dau co the cham.
- Timestamp phu thuoc vao output cua model; neu model khong tra ve chi tiet tung doan, app van tao transcript va xuat SRT fallback.
- Ban dau nen uu tien file ro giong noi, thoi luong vua phai.
