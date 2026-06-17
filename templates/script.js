const input = document.getElementById('audio');
const zone = document.getElementById('dropzone');
const meta = document.getElementById('fileMeta');
const selectedPreview = document.getElementById('selectedAudioPreview');
const selectedPlayer = document.getElementById('selectedAudioPlayer');
const selectedName = document.getElementById('selectedAudioName');
const form = document.getElementById('transcribeForm');
const submitButton = document.getElementById('submitButton');
const inferenceStatus = document.getElementById('inferenceStatus');
const inferencePercent = document.getElementById('inferencePercent');
const progressFill = document.getElementById('progressFill');
const inferenceNote = document.getElementById('inferenceNote');
let selectedObjectUrl = null;
let inferenceTimer = null;

['dragenter', 'dragover'].forEach(evt =>
    input.addEventListener(evt, () => zone.classList.add('is-drag'))
);

['dragleave', 'drop'].forEach(evt =>
    input.addEventListener(evt, () => zone.classList.remove('is-drag'))
);

input.addEventListener('change', () => {
    if (input.files && input.files[0]) {
        const f = input.files[0];
        const sizeMb = (f.size / (1024 * 1024)).toFixed(1);
        meta.textContent = f.name + ' · ' + sizeMb + ' MB';
        zone.classList.add('has-file');

        if (selectedObjectUrl) {
            URL.revokeObjectURL(selectedObjectUrl);
        }

        selectedObjectUrl = URL.createObjectURL(f);
        selectedPlayer.src = selectedObjectUrl;
        selectedName.textContent = f.name;
        selectedPreview.classList.add('is-visible');
    }
});

function updateProgress(value, message) {
    const percent = Math.max(0, Math.min(100, Math.round(value)));
    progressFill.style.width = percent + '%';
    inferencePercent.textContent = percent + '%';
    progressFill.parentElement.setAttribute('aria-valuenow', String(percent));

    if (message) {
        inferenceNote.textContent = message;
    }
}

if (form) {
    form.addEventListener('submit', () => {
        if (!input.files || !input.files[0]) {
            return;
        }

        if (inferenceTimer) {
            window.clearInterval(inferenceTimer);
        }

        let progress = 6;
        let phase = 0;
        const milestones = [
            { limit: 28, step: 4, message: 'Đang tải file lên server...' },
            { limit: 62, step: 3, message: 'Đang nạp model và tiền xử lý audio...' },
            { limit: 88, step: 2, message: 'Mô hình đang suy luận transcript...' },
            { limit: 96, step: 1, message: 'Đang tổng hợp transcript và chuẩn bị kết quả...' },
        ];

        inferenceStatus.classList.add('is-visible');
        inferenceStatus.setAttribute('aria-hidden', 'false');
        submitButton.disabled = true;
        submitButton.textContent = 'Đang bóc băng...';

        updateProgress(progress, milestones[phase].message);

        inferenceTimer = window.setInterval(() => {
            const current = milestones[phase];
            progress = Math.min(current.limit, progress + current.step);
            updateProgress(progress, current.message);

            if (progress >= current.limit && phase < milestones.length - 1) {
                phase += 1;
            }
        }, 450);
    });
}
