document.getElementById('uploadForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const resultDiv = document.getElementById('result');
    const chordsUl = document.getElementById('chords');
    const progressionP = document.getElementById('progression');
    const downloadLink = document.getElementById('downloadLink');

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        // Display results
        resultDiv.style.display = 'block';
        chordsUl.innerHTML = data.chords.map(chord => `<li>${chord}</li>`).join('');
        progressionP.textContent = data.progression;
        downloadLink.href = `/download/${data.harmony_file}`;
        downloadLink.style.display = 'inline';

        // Initialize WaveSurfer for waveforms
        const uploadedWaveform = WaveSurfer.create({
            container: '#uploadedWaveform',
            waveColor: '#4a90e2',
            progressColor: '#2a6abf'
        });
        uploadedWaveform.load(URL.createObjectURL(document.getElementById('audio').files[0]));

        const harmonyWaveform = WaveSurfer.create({
            container: '#harmonyWaveform',
            waveColor: '#e94e77',
            progressColor: '#b3395e'
        });
        harmonyWaveform.load(`/download/${data.harmony_file}`);

        const combinedWaveform = WaveSurfer.create({
            container: '#combinedWaveform',
            waveColor: '#28a745',
            progressColor: '#1e7e34'
        });
        combinedWaveform.load(`/download/${data.harmony_file}`);

        // Play buttons
        document.getElementById('playButton').onclick = () => uploadedWaveform.playPause();
        document.getElementById('replayButton').onclick = () => {
            uploadedWaveform.stop();
            uploadedWaveform.play();
        };
        document.getElementById('harmonyPlayButton').onclick = () => harmonyWaveform.playPause();
        document.getElementById('harmonyReplayButton').onclick = () => {
            harmonyWaveform.stop();
            harmonyWaveform.play();
        };
        document.getElementById('synthPlayButton').onclick = () => combinedWaveform.playPause();
        document.getElementById('regenerateButton').onclick = () => document.getElementById('uploadForm').submit();
    } catch (error) {
        alert('Error: ' + error.message);
    }
});