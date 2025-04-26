const form = document.getElementById('uploadForm');

let uploadedWaveform = null;
let harmonyWaveform = null;
let combinedWaveform = null;

form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const response = await fetch('/recommend', {
        method: 'POST',
        body: formData
    });

    const resultDiv = document.getElementById('result');
    const chordList = document.getElementById('chords');
    const progressionText = document.getElementById('progression');

    chordList.innerHTML = '';
    progressionText.innerHTML = '';
    resultDiv.style.display = 'none';

    if (response.ok) {
        const data = await response.json();
        resultDiv.style.display = 'block';

        // Show chords
        data.recommended_chords.forEach(chord => {
            const li = document.createElement('li');
            li.textContent = chord;
            chordList.appendChild(li);
        });

        // Show chord progression
        progressionText.textContent = data.chord_progression.join(' -> ');

        // Destroy old waveforms if existing
        if (uploadedWaveform) uploadedWaveform.destroy();
        if (harmonyWaveform) harmonyWaveform.destroy();
        if (combinedWaveform) combinedWaveform.destroy();

        document.getElementById('uploadedWaveform').innerHTML = '';
        document.getElementById('harmonyWaveform').innerHTML = '';
        document.getElementById('combinedWaveform').innerHTML = '';

        // Load uploaded audio waveform
        if (data.uploaded_audio_url) {
            uploadedWaveform = WaveSurfer.create({
                container: '#uploadedWaveform',
                waveColor: '#999',
                progressColor: '#2196f3',
                height: 80
            });
            uploadedWaveform.load(data.uploaded_audio_url);
            uploadedWaveform.on('finish', () => {
                document.getElementById('playButton').textContent = 'Play';
            });
        }

        // Load harmony preview waveform
        if (data.harmony_preview_url) {
            harmonyWaveform = WaveSurfer.create({
                container: '#harmonyWaveform',
                waveColor: '#ccc',
                progressColor: '#4caf50',
                height: 60
            });
            harmonyWaveform.load(data.harmony_preview_url);
            harmonyWaveform.on('finish', () => {
                document.getElementById('harmonyPlayButton').textContent = 'Play';
            });
        }

        // Load combined audio waveform
        if (data.combined_audio_url) {
            combinedWaveform = WaveSurfer.create({
                container: '#combinedWaveform',
                waveColor: '#999',
                progressColor: '#ff9800',
                height: 80
            });
            combinedWaveform.load(data.combined_audio_url);
            combinedWaveform.on('finish', () => {
                document.getElementById('synthPlayButton').textContent = 'Play Combined';
            });

            const downloadLink = document.getElementById('downloadLink');
            downloadLink.href = data.combined_audio_url;
            downloadLink.style.display = 'inline';
        }
    } else {
        alert('Failed to get harmony recommendations.');
    }
});

// Play/pause uploaded audio
document.getElementById('playButton').addEventListener('click', () => {
    if (uploadedWaveform) {
        uploadedWaveform.playPause();
        document.getElementById('playButton').textContent = uploadedWaveform.isPlaying() ? 'Pause' : 'Play';
    }
});

// Replay uploaded audio
document.getElementById('replayButton').addEventListener('click', () => {
    if (uploadedWaveform) {
        uploadedWaveform.stop();
        uploadedWaveform.play();
        document.getElementById('playButton').textContent = 'Pause';
    }
});

// Play/pause harmony preview
document.getElementById('harmonyPlayButton').addEventListener('click', () => {
    if (harmonyWaveform) {
        harmonyWaveform.playPause();
        document.getElementById('harmonyPlayButton').textContent = harmonyWaveform.isPlaying() ? 'Pause' : 'Play';
    }
});

// Replay harmony preview
document.getElementById('harmonyReplayButton').addEventListener('click', () => {
    if (harmonyWaveform) {
        harmonyWaveform.stop();
        harmonyWaveform.play();
        document.getElementById('harmonyPlayButton').textContent = 'Pause';
    }
});

// Play/pause synthesized harmony
document.getElementById('synthPlayButton').addEventListener('click', () => {
    if (combinedWaveform) {
        combinedWaveform.playPause();
        document.getElementById('synthPlayButton').textContent = combinedWaveform.isPlaying() ? 'Pause Combined' : 'Play Combined';
    }
});

// Handle regeneration of harmony
document.getElementById('regenerateButton').addEventListener('click', async () => {
    const instrument = document.getElementById('instrument').value;

    if (!instrument) {
        alert("Please select an instrument.");
        return;
    }

    const regenerateBtn = document.getElementById('regenerateButton');
    regenerateBtn.textContent = 'Regenerating...';
    regenerateBtn.disabled = true;

    const response = await fetch('/regenerate', {
        method: 'POST',
        body: JSON.stringify({ instrument }),
        headers: { 'Content-Type': 'application/json' }
    });

    if (response.ok) {
        const data = await response.json();

        if (harmonyWaveform) harmonyWaveform.destroy();
        if (combinedWaveform) combinedWaveform.destroy();

        document.getElementById('harmonyWaveform').innerHTML = '';
        document.getElementById('combinedWaveform').innerHTML = '';

        // New harmony waveform
        harmonyWaveform = WaveSurfer.create({
            container: '#harmonyWaveform',
            waveColor: '#ccc',
            progressColor: '#4caf50',
            height: 60
        });
        harmonyWaveform.load(data.harmony_preview_url);

        harmonyWaveform.on('finish', () => {
            document.getElementById('harmonyPlayButton').textContent = 'Play';
        });

        // New combined waveform
        combinedWaveform = WaveSurfer.create({
            container: '#combinedWaveform',
            waveColor: '#999',
            progressColor: '#ff9800',
            height: 80
        });
        combinedWaveform.load(data.combined_audio_url);

        combinedWaveform.on('finish', () => {
            document.getElementById('synthPlayButton').textContent = 'Play Combined';
        });

        const downloadLink = document.getElementById('downloadLink');
        downloadLink.href = data.combined_audio_url;
        downloadLink.style.display = 'inline';

    } else {
        alert('Failed to regenerate harmony.');
    }

    regenerateBtn.textContent = 'Regenerate Harmony';
    regenerateBtn.disabled = false;
});