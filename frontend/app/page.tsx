"use client"; // Required for useState, useEffect, event handlers

import { useState } from 'react';
import { useRouter } from 'next/navigation'; // Use next/navigation for App Router

export default function Home() {
  const router = useRouter();
  const [topics, setTopics] = useState<string[]>(['', '', '']); // Start with 3 empty topics
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const MAX_TOPICS = 5;
  const MIN_TOPICS = 1;

  const handleTopicChange = (index: number, value: string) => {
    const newTopics = [...topics];
    newTopics[index] = value;
    setTopics(newTopics);
    setError(null); // Clear error when user types
  };

  const addTopic = () => {
    if (topics.length < MAX_TOPICS) {
      setTopics([...topics, '']);
      setError(null);
    } else {
      setError(`Maximum of ${MAX_TOPICS} topics allowed.`);
    }
  };

  const removeTopic = (index: number) => {
    if (topics.length > MIN_TOPICS) {
      const newTopics = topics.filter((_, i) => i !== index);
      setTopics(newTopics);
      setError(null);
    } else {
      setError(`Minimum of ${MIN_TOPICS} topic required.`);
    }
  };

  const handleWatch = async () => {
    setError(null); // Clear previous errors
    const filledTopics = topics.filter(topic => topic.trim() !== '');

    if (filledTopics.length !== topics.length) {
      setError('All topic fields must be filled.');
      return;
    }

    if (filledTopics.length === 0) {
        setError('Please enter at least one topic.');
        return;
    }

    setIsLoading(true);
    // Store topics for the next page (e.g., using localStorage or query params)
    // Using localStorage for simplicity here, but query params are also an option
    try {
        localStorage.setItem('videoGeneratorTopics', JSON.stringify(filledTopics));
        router.push('/watch'); // Navigate to the watch page
    } catch (e) {
        setError("Failed to prepare topics for the next page. Please try again.");
        console.error("LocalStorage error:", e);
        setIsLoading(false);
    }

    // The actual API call will happen on the /watch page after navigation
    // to ensure the topics are available there.
  };

  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen p-4"
      style={{
        backgroundImage: `url('/background.png')`, // Path relative to the public directory root
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="w-full max-w-lg bg-white bg-opacity-80 p-8 rounded-lg shadow-md"> {/* Added bg-opacity-80 for readability */}
        <h1 className="text-4xl font-bold mb-6 text-center text-gray-800">
          SnapEd
        </h1>

        <p className="mb-4 text-gray-600">Enter your topic(s) here:</p>

        <div className="space-y-3 mb-6">
          {topics.map((topic, index) => (
            <div key={index} className="flex items-center space-x-2">
              <input
                type="text"
                value={topic}
                onChange={(e) => handleTopicChange(index, e.target.value)}
                placeholder={`Topic ${index + 1}`}
                className="flex-grow p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                disabled={isLoading}
              />
              {topics.length > MIN_TOPICS && (
                <button
                  onClick={() => removeTopic(index)}
                  className="p-2 text-red-500 hover:text-red-700 disabled:opacity-50"
                  aria-label={`Remove Topic ${index + 1}`}
                  disabled={isLoading}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </button>
              )}
            </div>
          ))}
        </div>

        {error && (
          <p className="text-red-500 text-sm mb-4">{error}</p>
        )}

        <div className="flex justify-between items-center mb-6">
          <button
            onClick={addTopic}
            disabled={topics.length >= MAX_TOPICS || isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Add Topic
          </button>
          <span className="text-sm text-gray-500">
            {topics.length} / {MAX_TOPICS}
          </span>
        </div>

        <button
          onClick={handleWatch}
          disabled={isLoading}
          className="w-full px-4 py-3 bg-green-500 text-white font-bold rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-wait"
        >
          {isLoading ? 'Processing...' : 'Watch!'}
        </button>
      </div>
    </div>
  );
}
