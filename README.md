# STT_Vi

MVP boc bang ghi am tieng Viet dua tren cac model PhoWhisper local.

## Chuc nang hien tai

- Upload file audio/video qua web
- Chon model `tiny`, `small`, `base`, `medium` hoac `large`
- Chay transcript voi PhoWhisper local tren CPU
- Xem ket qua ngay tren giao dien
- Tai ket qua duoi dang `txt`, `srt`, `json`

## Chay local

```bash
pip install -r requirements.txt
python download_models.py tiny small base medium large
python main.py
```

Sau do mo `http://127.0.0.1:5000`.

## Luu y

- File wav PCM co the duoc doc truc tiep neu may chua cai ffmpeg.
- Voi mp3, mp4, m4a, aac hoac webm, nen cai ffmpeg hoac torchcodec de decode audio.
- Model duoc load o lan request dau tien nen request dau co the cham.
- Model duoc load tu thu muc `models/PhoWhisper-*`.
- Timestamp phu thuoc vao output cua model; neu model khong tra ve chi tiet tung doan, app van tao transcript va xuat SRT fallback.
- Ban dau nen uu tien file ro giong noi, thoi luong vua phai.
