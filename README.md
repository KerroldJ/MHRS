# 🎵 Musical Harmony Recommendation System

A system that analyzes a user-uploaded audio file, identifies its tonal characteristics, and recommends harmonies based on a selected instrument (e.g., acoustic guitar, electric guitar, ukulele, piano, bass). Generates a harmonized audio preview to assist in music composition and arrangement.

## 🚀 Features

- 🔍 Analyzes uploaded audio to extract tonal features (pitch, timbre, attack/decay)
- 🎹 Supports harmony generation for multiple instruments:
  - Acoustic Guitar
  - Electric Guitar
  - Piano
  - Ukulele
  - Bass
- 🧠 Intelligent harmony recommendation using tonal feature matching
- 🎧 Audio preview generation for harmonized output
- 🖥 Web-based interface built with React.js
- 🐍 Backend powered by Python and Flask

## 🎤 How It Works

1. **Upload Audio**: Users upload a short audio recording (WAV/MP3).
2. **Select Instrument**: Choose an instrument for harmonization.
3. **Analyze**: The system extracts audio features using Python libraries.
4. **Recommend & Harmonize**: Harmony is generated based on musical theory and tonal compatibility.
5. **Preview**: The harmonized audio is returned and previewed in the browser.

## 🛠 Tech Stack

| Component     | Technology        |
|---------------|-------------------|
| Frontend      | React.js          |
| Backend       | Flask (Python)    |
| Audio Analysis| Librosa, NumPy    |
| Audio Output  | Soundfile, Pydub  |
| ML/AI (optional) | Scikit-learn, TensorFlow (if used) |

