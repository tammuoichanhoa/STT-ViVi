const input = document.getElementById('audio');
const zone = document.getElementById('dropzone');
const meta = document.getElementById('fileMeta');
const selectedPreview = document.getElementById('selectedAudioPreview');
const selectedPlayer = document.getElementById('selectedAudioPlayer');
const selectedName = document.getElementById('selectedAudioName');
let selectedObjectUrl = null;

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
