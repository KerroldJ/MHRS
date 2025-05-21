"use client";

import React, { useState, useEffect } from 'react';
import Header from './pages/components/Header';
import Link from 'next/link';


const aboutText = `Our Harmony Recommendation System is designed to analyze tonal features of your audio and generate customized harmony suggestions based on selected instruments.

Whether you're working with vocals, guitar, or piano, our intelligent backend ensures your audio is harmonized accurately and creatively.
By leveraging advanced audio analysis and machine learning, our system can identify key tonal attributes—such as pitch, timbre, and rhythm—and provide harmony lines that blend naturally with your original recording.

Whether you're a music producer, composer, or a hobbyist looking to enhance your sound, our platform simplifies the harmony creation process.
Simply upload your audio, choose an instrument like acoustic guitar, bass, piano, or ukulele, and receive a harmonized output in seconds.

We aim to empower creativity by offering an intuitive and accessible tool for musicians of all levels.
No matter your genre or experience, our system adapts to your musical needs, helping you bring your vision to life with clarity and precision.`;

function Home() {
  const [typedText, setTypedText] = useState('');
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (index < aboutText.length) {
      const timeout = setTimeout(() => {
        setTypedText((prev) => prev + aboutText.charAt(index));
        setIndex(index + 1);
      }, 15);
      return () => clearTimeout(timeout);
    }
  }, [index]);

  return (
    <div className="min-h-screen bg-white text-gray-800">
      <Header />
      <main className="max-w-5xl mx-auto px-6 py-12">
        <section className="bg-gray-100 rounded-2xl shadow-sm p-8">
          <h1 className="text-2xl font-bold text-gray-800 mb-4 text-center">
            Welcome to our Harmony Recommendation System
          </h1>
          <h2 className="text-xl font-semibold text-gray-700 mb-4 text-left">About Us</h2>
          <p className="text-gray-600 text-base leading-relaxed whitespace-pre-line min-h-[300px]">
            {typedText}
            <span className="animate-pulse">|</span>
          </p>

          {/* Button */}
          {index >= aboutText.length && (
            <div className="mt-8 text-center">
              <Link href="/pages/Dashboard">Continue to System</Link>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default Home;
