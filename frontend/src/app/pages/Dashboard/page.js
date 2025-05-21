"use client";

import React, { useState } from 'react';
import Header from '../components/Header';
import Link from 'next/link';

function Dashboard() {
    const [audioFile, setAudioFile] = useState(null);
    const [instrument, setInstrument] = useState('');
    const [tonalFeatures, setTonalFeatures] = useState('');
    const [recommendedChords, setRecommendedChords] = useState('');
    const [chordProgression, setChordProgression] = useState('');
    const [harmonyPreview, setHarmonyPreview] = useState('');
    const [combinedAudio, setCombinedAudio] = useState('');

    const instruments = ['Acoustic Guitar', 'Electric Guitar', 'Bass', 'Ukulele', 'Piano'];

    const handleAudioUpload = (e) => {
        const file = e.target.files[0];
        setAudioFile(file);
    };

    return (
        <div className="min-h-screen bg-white text-gray-800">
            <Header />
            <div className="max-w-5xl mx-auto px-6 py-12 bg-gray-100 mt-10 rounded-2xl">
                <h1 className="text-2xl font-bold text-center">Harmony Recommendation System</h1>
                <div>
                    <label className="block mb-2 text-sm font-medium">Upload Audio</label>
                    <input
                        type="file"
                        accept="audio/*"
                        onChange={handleAudioUpload}
                        className="w-full p-2 border rounded"
                    />
                </div>

                <div>
                    <label className="block mb-2 text-sm font-medium">Select Instrument</label>
                    <select
                        className="w-full p-2 border rounded"
                        value={instrument}
                        onChange={(e) => setInstrument(e.target.value)}
                    >
                        <option value="">Choose an instrument</option>
                        {instruments.map((inst) => (
                            <option key={inst} value={inst}>{inst}</option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block mb-1 font-medium text-sm">Tonal Features</label>
                    <textarea
                        className="w-full p-2 border rounded"
                        rows={2}
                        value={tonalFeatures}
                        onChange={(e) => setTonalFeatures(e.target.value)}
                    />
                </div>

                <div>
                    <label className="block mb-1 font-medium text-sm">Recommended Chords</label>
                    <textarea
                        className="w-full p-2 border rounded"
                        rows={2}
                        value={recommendedChords}
                        onChange={(e) => setRecommendedChords(e.target.value)}
                    />
                </div>

                <div>
                    <label className="block mb-1 font-medium text-sm">Chord Progression</label>
                    <textarea
                        className="w-full p-2 border rounded"
                        rows={2}
                        value={chordProgression}
                        onChange={(e) => setChordProgression(e.target.value)}
                    />
                </div>

                <div>
                    <label className="block mb-1 font-medium text-sm">Uploaded Audio</label>
                    {audioFile && (
                        <audio controls className="w-full">
                            <source src={URL.createObjectURL(audioFile)} type="audio/mpeg" />
                        </audio>
                    )}
                </div>

                <div>
                    <label className="block mb-1 font-medium text-sm">Harmony Preview</label>
                    {harmonyPreview && (
                        <audio controls className="w-full">
                            <source src={harmonyPreview} type="audio/mpeg" />
                        </audio>
                    )}
                </div>

                <div>
                    <label className="block mb-1 font-medium text-sm">Combined Audio</label>
                    {combinedAudio && (
                        <audio controls className="w-full">
                            <source src={combinedAudio} type="audio/mpeg" />
                        </audio>
                    )}
                </div>
            </div>
            
            <div className="mt-8 text-center">
                <Link href="/">Go Back To Home</Link>
            </div>
        </div>  
    );
}

export default Dashboard;
