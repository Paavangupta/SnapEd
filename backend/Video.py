import subprocess
import uuid
import os

def get_audio_duration(audio_path):
    """
    Uses ffprobe to get the duration (in seconds) of the audio file.
    """
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    duration_str = result.stdout.strip()
    try:
        return float(duration_str)
    except ValueError:
        raise Exception("Could not parse audio duration.")

def create_video_with_fade(image_path, audio_path, output_path=None):
    """
    Creates a video from a static image and an audio clip.
    The image will fade in during the first second and fade out during the last second.
    The video duration is set to the length of the audio file.
    
    Parameters:
        image_path (str): Path to the input image.
        audio_path (str): Path to the input MP3 audio clip.
        output_path (str, optional): Desired output file path. If not provided, one is generated.
    
    Returns:
        str: The path to the generated video.
    """
    # Check if input files exist.
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Generate a unique output path if one is not provided.
    if output_path is None:
        output_path = f"output_{uuid.uuid4()}.mp4"
    
    # Get the duration of the audio file.
    duration = get_audio_duration(audio_path)
    
    # Build the FFmpeg command:
    # -loop 1: loop the image continuously
    # -i: specify the input files (first the image, then the audio)
    # -filter_complex: apply fade-in and fade-out effects to the image stream
    #   fade=t=in:st=0:d=1 -> fade in starting at 0 sec lasting 1 sec
    #   fade=t=out:st=(duration-1):d=1 -> fade out starting at (duration - 1) sec lasting 1 sec
    # -map: select the video and audio streams
    # -t duration: set the total video duration to the audio duration
    # -c:v and -c:a: specify the codecs for video and audio
    command = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-filter_complex", f"[0:v]fade=t=in:st=0:d=1,fade=t=out:st={duration - 1}:d=1[v]",
        "-map", "[v]",
        "-map", "1:a",
        "-t", str(duration),
        "-c:v", "libx264",
        "-c:a", "aac",
        output_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed with error:")
        print(e.stderr)
        raise

    # Delete the audio file after successfully stitching the video.
    try:
        os.remove(audio_path)
    except Exception as del_err:
        print(f"Warning: Could not delete audio file {audio_path}: {del_err}")

        # Delete the image file after successfully stitching the video.
    try:
        os.remove(image_path)
    except Exception as del_err:
        print(f"Warning: Could not delete image file {image_path}: {del_err}")

    return output_path

# Example usage:
#video_file = create_video_with_fade("Unknown.jpeg", "output_20250329035727981036.mp3")
#print(f"Video created at: {video_file}")
