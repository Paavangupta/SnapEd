import subprocess
import uuid
import os

def add_audio_to_video(video_path, audio_path, output_path=None):
    """
    Takes an MP4 video and an MP3 audio file, and produces a new MP4 file that:
      - Has the MP3 file as its audio track.
      - Loops the video as many times as needed to match the audio's duration.
      - Ensures the final video's duration exactly matches the length of the audio.
    
    After successful creation, the original video and audio files are deleted.
    
    Parameters:
        video_path (str): Path to the input MP4 video file.
        audio_path (str): Path to the input MP3 audio file.
        output_path (str, optional): Desired output file path. If not provided, one is generated.
    
    Returns:
        str: The path to the combined output video.
    """
    # Check if input files exist.
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Generate a unique output file name if not provided.
    if output_path is None:
        output_path = f"combined_{uuid.uuid4()}.mp4"
    
    # Build the FFmpeg command:
    # - "-stream_loop -1" loops the video indefinitely.
    # - "-i video_path" specifies the video input.
    # - "-i audio_path" specifies the audio input.
    # - "-c:v copy" copies the video stream without re-encoding.
    # - "-c:a aac" encodes the audio using AAC.
    # - "-shortest" ensures the output stops when the audio ends.
    command = [
        "ffmpeg",
        "-y",                           # Overwrite output file if it exists.
        "-stream_loop", "-1",           # Loop video indefinitely.
        "-i", video_path,               # Video input.
        "-i", audio_path,               # Audio input.
        "-c:v", "copy",                 # Copy video stream.
        "-c:a", "aac",                  # Encode audio with AAC.
        "-shortest",                    # End output when the audio ends.
        output_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed with error:")
        print(e.stderr)
        raise

    # Delete the original audio and video files.
    for file_path in [video_path, audio_path]:
        try:
            os.remove(file_path)
        except Exception as del_err:
            print(f"Warning: Could not delete file {file_path}: {del_err}")

    return output_path

# Example usage:
#combined_video = add_audio_to_video("input_video.mp4", "input_audio.mp3")
#print(f"Combined video created at: {combined_video}")
