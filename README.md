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

## Dong goi cho Windows

Khuyen nghi build truc tiep tren Windows 10/11 64-bit. `PyInstaller` khong cross-build exe Windows on dinh tu Linux.

### 1. Build file exe

Cai Python 3.11 tren Windows, sau do chay PowerShell trong thu muc du an:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\build_windows.ps1 -Models small
```

Script se:

- Tao `.venv`
- Cai dependency va `pyinstaller`
- Tai model PhoWhisper duoc chi dinh
- Build `dist\STT_Vi.exe`

Neu muon bo qua buoc tai model, sua tham so:

```powershell
.\build_windows.ps1 -Models @()
```

### 2. Tao file cai dat `.exe`

Cai Inno Setup 6, mo file `installer.iss`, sau do build installer. Ket qua se nam trong:

```text
dist\installer\STT_Vi_Setup.exe
```

Installer se:

- Cai `STT_Vi.exe`
- Copy thu muc `models\` vao may nguoi dung
- Tao shortcut Start Menu va Desktop

### 3. Luu y khi dong goi

- Can co san thu muc `models/PhoWhisper-*` truoc khi tao installer neu muon phan mem chay offline ngay.
- Thu muc `uploads` va `outputs` khi chay ban dong goi se duoc dat tai `%LOCALAPPDATA%\STT_Vi`.
- App se mo browser tai `http://127.0.0.1:5000` va chay bang Waitress thay vi Flask dev server.
