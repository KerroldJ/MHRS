"use client";

import React, { useState } from "react";
import Header from "../components/Header";
import Link from "next/link";
import axios from "axios";

function Dashboard() {
    const [audioFile, setAudioFile] = useState(null);
    const [instrument, setInstrument] = useState("");
    const [tonalFeatures, setTonalFeatures] = useState(null);
    const [recommendedChords, setRecommendedChords] = useState("");
    const [chordProgression, setChordProgression] = useState("");
    const [harmonyPreview, setHarmonyPreview] = useState("");
    const [combinedAudio, setCombinedAudio] = useState("");
    const [uploadedAudioUrl, setUploadedAudioUrl] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const instruments = ["Acoustic Guitar", "Electric Guitar", "Bass", "Ukulele", "Piano"];

    const handleAudioUpload = (e) => {
        setAudioFile(e.target.files[0]);
        setError("");
    };

    const handleSubmit = async () => {
        if (!audioFile || !instrument) {
            setError("Please upload an audio file and select an instrument.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const formData = new FormData();
            formData.append("audio", audioFile);
            formData.append("instrument", instrument);

            const response = await axios.post("http://127.0.0.1:5000/recommend", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });

            const {
                tonal_features,
                recommended_chords,
                chord_progression,
                harmony_preview_url,
                uploaded_audio_url,
                combined_audio_url,
            } = response.data;

            setTonalFeatures(tonal_features);
            setRecommendedChords(recommended_chords || "");
            setChordProgression(chord_progression || "");
            setHarmonyPreview(harmony_preview_url || "");
            setUploadedAudioUrl(uploaded_audio_url || "");
            setCombinedAudio(combined_audio_url || "");
        } catch (error) {
            console.error("Error processing recommendation:", error);
            setError(error.response?.data?.error || "An error occurred during processing.");
        } finally {
            setLoading(false);
        }
    };

    const handleRegenerate = async () => {
        if (!instrument || !tonalFeatures) {
            setError("Select an instrument and ensure tonal features are available before regenerating.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const response = await axios.post(
                "http://127.0.0.1:5000/regenerate-harmony",
                {
                    instrument,
                    features: tonalFeatures,
                },
                { headers: { "Content-Type": "application/json" } }
            );

            const { recommended_chords, chord_progression, harmony_preview_url } = response.data;

            setRecommendedChords(recommended_chords || "");
            setChordProgression(chord_progression || "");
            setHarmonyPreview(harmony_preview_url || "");
        } catch (error) {
            console.error("Error regenerating harmony:", error);
            setError(error.response?.data?.error || "Failed to regenerate harmony.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white text-gray-800">
            <Header />
            <div className="max-w-5xl mx-auto px-6 py-12 bg-gray-100 mt-10 rounded-2xl">
                <h1 className="text-2xl font-bold text-center mb-6">Harmony Recommendation System</h1>
                {error && <p className="text-red-600 text-center mb-4">{error}</p>}
                <div className="space-y-4">
                    <div>
                        <label className="block mb-2 text-sm font-medium">Upload Audio</label>
                        <input
                            type="file"
                            accept="audio/mp3,audio/wav,audio/flac,audio/ogg"
                            onChange={handleAudioUpload}
                            className="w-full p-2 border rounded"
                            disabled={loading}
                        />
                    </div>

                    <div>
                        <label className="block mb-2 text-sm font-medium">Select Instrument</label>
                        <select
                            className="w-full p-2 border rounded"
                            value={instrument}
                            onChange={(e) => setInstrument(e.target.value)}
                            disabled={loading}
                        >
                            <option value="">Choose an instrument</option>
                            {instruments.map((inst) => (
                                <option key={inst} value={inst}>
                                    {inst}
                                </option>
                            ))}
                        </select>
                    </div>

                    <button
                        onClick={handleSubmit}
                        className="w-full bg-blue-600 text-white py-2 rounded mt-4 hover:bg-blue-700 disabled:bg-blue-400"
                        disabled={loading}
                    >
                        {loading ? "Processing..." : "Submit for Recommendation"}
                    </button>

                    <button
                        onClick={handleRegenerate}
                        className="w-full bg-green-600 text-white py-2 rounded mt-2 hover:bg-green-700 disabled:bg-green-400"
                        disabled={loading || !tonalFeatures}
                    >
                        {loading ? "Regenerating..." : "Regenerate Harmony"}
                    </button>

                    {tonalFeatures && (
                        <div>
                            <label className="block mb-1 font-medium text-sm">Tonal Features</label>
                            <textarea
                                className="w-full p-2 border rounded"
                                rows={2}
                                value={JSON.stringify(tonalFeatures, null, 2)}
                                readOnly
                            />
                        </div>
                    )}

                    {recommendedChords && (
                        <div>
                            <label className="block mb-1 font-medium text-sm">Recommended Chords</label>
                            <textarea
                                className="w-full p-2 border rounded"
                                rows={2}
                                value={recommendedChords}
                                readOnly
                            />
                        </div>
                    )}

                    {chordProgression && (
                        <div>
                            <label className="block mb-1 font-medium text-sm">Chord Progression</label>
                            <textarea
                                className="w-full p-2 border rounded"
                                rows={2}
                                value={chordProgression}
                                readOnly
                            />
                        </div>
                    )}

                    {uploadedAudioUrl && (
                        <div>
                            <label className="block mb-1 font-medium text-sm">Uploaded Audio</label>
                            <audio controls className="w-full">
                                <source src={uploadedAudioUrl} type="audio/mpeg" />
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    )}

                    {harmonyPreview && (
                        <div>
                            <label className="block mb-1 font-medium text-sm">Harmony Preview</label>
                            <audio controls className="w-full">
                                <source src={harmonyPreview} type="audio/mpeg" />
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    )}

                    {combinedAudio && (
                        <div>
                            <label className="block mb-1 font-medium text-sm">Combined Audio</label>
                            <audio controls className="w-full">
                                <source src={combinedAudio} type="audio/mpeg" />
                                Your browser does not support the audio element.
                            </audio>
                        </div>
                    )}
                </div>
            </div>

            <div className="mt-8 text-center">
                <Link href="/" className="text-blue-600 hover:underline">
                    Go Back To Home
                </Link>
            </div>
        </div>
    );
}

export default Dashboard;