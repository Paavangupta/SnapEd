"use client";

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
// Image component is no longer needed for the primary display
// import Image from 'next/image';

interface VideoResponse {
  video_url: string; // Expecting a URL to the generated video
}

export default function WatchPage() {
  const router = useRouter();
  const [topics, setTopics] = useState<string[]>([]);
  const [videoUrl, setVideoUrl] = useState<string | null>(null); // State to hold the video URL
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  // currentImageIndex is no longer needed
  // const [currentImageIndex, setCurrentImageIndex] = useState<number>(0);

  const hasFetched = useRef(false);

  const BACKEND_URL = 'http://127.0.0.1:5001/generate'; // Endpoint to generate video
  const BACKEND_BASE_URL = 'http://127.0.0.1:5001'; // Base URL for constructing the full video path if needed

  // Function to fetch data from backend
  const fetchVideoData = useCallback(async (currentTopics: string[]) => {
    if (currentTopics.length === 0) {
        setError("No topics found. Please go back and enter topics.");
        setIsLoading(false);
        return;
    }

    setIsLoading(true);
    setError(null);
    setVideoUrl(null); // Reset video URL on new fetch
    // setCurrentImageIndex(0); // No longer needed

    try {
      const response = await fetch(BACKEND_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topics: currentTopics }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
      }

      const data: VideoResponse = await response.json();

      // Basic validation of received data
      if (!data.video_url) {
          throw new Error("Received invalid data structure from backend (missing video_url).");
      }

      // Construct the full URL if the backend returns a relative path
      // Assuming the backend returns a full URL for now. If it's relative like '/videos/output.mp4', adjust here.
      const fullVideoUrl = data.video_url.startsWith('http') ? data.video_url : `${BACKEND_BASE_URL}${data.video_url}`;

      console.log("Received video URL:", fullVideoUrl);

      setVideoUrl(fullVideoUrl);
    } catch (err: any) {
      console.error("Failed to fetch video data:", err);
      setError(`Failed to generate video: ${err.message}`);
      setVideoUrl(null); // Clear video URL on error
    } finally {
      setIsLoading(false);
    }
  }, [BACKEND_BASE_URL]); // Add BACKEND_BASE_URL to dependencies if used inside

  // Effect to load topics and fetch initial data
  useEffect(() => {
    if (hasFetched.current) return;
    hasFetched.current = true;
  
    try {
      const storedTopics = localStorage.getItem('videoGeneratorTopics');
      if (storedTopics) {
        const parsedTopics = JSON.parse(storedTopics);
        if (Array.isArray(parsedTopics) && parsedTopics.length > 0) {
          setTopics(parsedTopics);
          fetchVideoData(parsedTopics); // Fetch initial data
        } else {
          setError("Invalid topics found. Please go back.");
          setIsLoading(false);
        }
      } else {
        setError("No topics found. Please go back and enter topics.");
        setIsLoading(false);
      }
    } catch (e) {
      console.error("LocalStorage read error:", e);
      setError("Failed to load topics. Please go back.");
      setIsLoading(false);
    }
  }, [fetchVideoData]);

  // handleNextImage and handlePrevImage are no longer needed as we display a single video
  // const handleNextImage = () => { ... };
  // const handlePrevImage = () => { ... };

  // Simulate "swipe up" with a button click for regeneration
  const handleRegenerate = () => {
    if (!isLoading && topics.length > 0) {
      fetchVideoData(topics);
    }
  };

  const handleExit = async () => { // Make async to await fetch
    // Clear stored topics on exit
    localStorage.removeItem('videoGeneratorTopics');

    // Call the backend endpoint to reset its used_topics list
    try {
      const resetResponse = await fetch('http://127.0.0.1:5001/reset_topics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // No body needed for this simple reset endpoint
      });
      if (!resetResponse.ok) {
        console.error("Failed to reset backend topics:", resetResponse.statusText);
        // Decide if you want to show an error to the user or just log it
      } else {
        console.log("Backend topics reset successfully.");
      }
    } catch (error) {
      console.error("Error calling reset topics endpoint:", error);
      // Handle network errors, etc.
    }

    router.push('/'); // Navigate back to home
  };

  // --- Rendering Logic ---

  // Update initial loading check to use videoUrl
  if (isLoading && !videoUrl) { // Show initial loading state when videoUrl is not yet available
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
        <p className="text-xl mb-4">Generating your video content...</p>
        {/* Optional: Add a spinner */}
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
        <p className="text-red-500 text-xl mb-4">Error: {error}</p>
        <button
          onClick={handleExit}
          className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        >
          Go Back
        </button>
      </div>
    );
  }

  // Update check for content loading failure - show if not loading AND videoUrl is still null
  if (!isLoading && !videoUrl) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
        <p className="text-xl mb-4">Could not load video content.</p>
        <button
          onClick={handleExit}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
        >
          Go Back
        </button>
      </div>
    );
  }

  // Image-related variables are no longer needed
  // const validImageUrls = videoData.image_urls.filter(url => url !== null) as string[];
  // const currentImageUrl = validImageUrls[currentImageIndex] || '/placeholder.svg'; // Fallback image

  return (
    <div className="flex flex-col h-screen bg-black text-white overflow-hidden relative">
       {/* Exit Button */}
       <button
         onClick={handleExit}
         className="absolute top-4 left-4 z-20 p-2 bg-gray-700 bg-opacity-70 text-white rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500" // Changed padding to p-2
         aria-label="Exit to home screen"
       >
         {/* X Icon SVG */}
         <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
           <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
         </svg>
       </button>

      {/* Video Display Area - Centered */}
      <div className="flex-grow flex items-center justify-center relative w-full h-full">
        {isLoading && ( // Loading indicator overlay (still useful during regeneration)
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center z-10">
                 <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        )}
        {/* Video Container */}
        <div className="relative w-full h-full max-w-screen-lg max-h-screen-lg flex items-center justify-center">
           {/* Render Video Player */}
           {videoUrl ? (
             <video
               key={videoUrl} // Force re-render if URL changes
               src={videoUrl}
               controls // Add basic video controls (play/pause, volume, etc.)
               autoPlay // Optional: Start playing automatically
               loop // Optional: Loop the video
               className="max-w-full max-h-full object-contain" // Ensure video fits within container
               onError={(e) => {
                  console.error("Video failed to load:", videoUrl, e);
                  setError("Failed to load video."); // Set error state if video fails
               }}
             >
               Your browser does not support the video tag.
             </video>
           ) : (
             // This case should ideally be handled by the loading/error states above,
             // but keep a fallback just in case. Render nothing or a placeholder if videoUrl is null/empty
             <div className="text-gray-400 text-center p-4">
               Video is preparing...
             </div>
           )}
        </div>

        {/* Left/Right Navigation Buttons are removed */}
        {/* Image index dots are removed */}

      </div>

      {/* Regenerate Button (Simulating Swipe Up) */}
      <button
        onClick={handleRegenerate}
        disabled={isLoading}
        className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
        aria-label="Generate next video clip"
      >
        {/* Down Arrow SVG Icon */}
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </button>

       {/* Image index dots are removed */}
    </div>
  );
}