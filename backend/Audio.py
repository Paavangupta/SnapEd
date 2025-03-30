import json
import requests
import base64
from datetime import datetime
import os
import random

# Your API key (be cautious about exposing API keys in production code)
API_KEY = "AIzaSyDT3U3pE_xTChROAPhsriSMv0Vp0lE8fxY"

def convert_text_to_mp3(text: str, accent = "UK", gender = "FEMALE", speaking_rate: float = 1.0) -> str:
    """
    Converts a given text string to an MP3 file using Google Cloud's WaveNet TTS via REST API.
    The function randomizes the voice accent (US or UK) and gender (MALE, FEMALE, NEUTRAL) each call.
    
    Parameters:
      text: The text to convert.
      speaking_rate: Desired speaking rate (1.0 is default; lower is slower, higher is faster).
    
    Returns:
      The generated MP3 file name on success, or None if an error occurs.
    """
    
    
    # Mapping of accent and gender to voice names.
    # For US, we use default WaveNet voices.
    # For UK, we pick a corresponding voice (adjust as needed based on available voices).
    voices = {
        "US": {
            "MALE": "en-US-Wavenet-D",
            "FEMALE": "en-US-Wavenet-F",
            "NEUTRAL": "en-US-Wavenet-C"
        },
        "UK": {
            "MALE": "en-GB-Wavenet-B",
            "FEMALE": "en-GB-Wavenet-D",
            "NEUTRAL": "en-GB-Wavenet-C"  # Since UK may not have an explicit neutral voice, using one available.
        }
    }
    
    # Determine languageCode based on accent
    language_code = "en-US" if accent == "US" else "en-GB"
    voice_name = voices[accent][gender]
    
    print(f"Randomly selected accent: {accent}, gender: {gender}, voice: {voice_name}")

    # Construct the REST endpoint URL with the API key
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"

    # Build the payload with the provided text
    payload = {
        "input": {
            "text": text
        },
        "voice": {
            "languageCode": language_code,
            "name": voice_name,
            "ssmlGender": gender
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": speaking_rate
        }
    }

    # Make the POST request
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # raise an error for bad status codes
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None

    # Parse the response
    try:
        response_data = response.json()
        #print("Full API response:", json.dumps(response_data, indent=2))
        audio_content = response_data.get("audioContent")
        if not audio_content:
            print("No audio content found in the response.")
            return None
    except Exception as e:
        print(f"Error parsing response: {e}")
        return None

    # Decode the base64-encoded audio content
    try:
        audio_data = base64.b64decode(audio_content)
    except Exception as e:
        print(f"Error decoding audio content: {e}")
        return None

    # Generate a unique output file name using a timestamp (including microseconds)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    output_file = f"output_{timestamp}.mp3"

    # Write the audio data to the MP3 file
    try:
        with open(output_file, 'wb') as out:
            out.write(audio_data)
        print(f"Audio content successfully written to '{output_file}'.")
    except Exception as e:
        print(f"Error writing to file: {e}")
        return None

    return output_file

def convert_file_to_mp3(file_path: str, speaking_rate: float = 1.0) -> str:
    """
    Reads text from a file and converts it to an MP3 file by calling convert_text_to_mp3.
    
    Parameters:
      file_path: Path to the text file.
      speaking_rate: Desired speaking rate (1.0 is default).
    
    Returns:
      The generated MP3 file name on success, or None if an error occurs.
    """
    # Read the text from the file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None

    # Call the conversion function with the file's text
    return convert_text_to_mp3(text, speaking_rate)
