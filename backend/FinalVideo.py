import os
import uuid
import subprocess
import tempfile

def stitch_videos(input_files, output_path=None):
    """
    Stitches together multiple MP4 files into one combined video and deletes the input files.
    
    Parameters:
        input_files (list): List of file paths to MP4 videos to be stitched.
        output_path (str, optional): Desired output file path. If not provided, one is generated.
        
    Returns:
        str: The path to the combined video.
        
    Raises:
        Exception: If FFmpeg fails to combine the videos.
    """
    # Check that each input file exists
    for f in input_files:
        if not os.path.isfile(f):
            raise FileNotFoundError(f"Input file not found: {f}")
    
    # Generate unique output file if not provided
    if output_path is None:
        output_path = f"combined_{uuid.uuid4()}.mp4"
    
    # Create a temporary file to list the input videos for FFmpeg concat demuxer
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as list_file:
        list_filename = list_file.name
        for file_path in input_files:
            # FFmpeg concat demuxer requires each line to be in format: file '/path/to/file'
            safe_path = os.path.abspath(file_path).replace("'", "'\\''")
            list_file.write(f"file '{safe_path}'\n")

    
    # Build the FFmpeg command:
    # -f concat: use concat demuxer
    # -safe 0: allow unsafe file paths
    # -i list_filename: input list of files
    # -c copy: copy codec to avoid re-encoding (requires identical codecs)
    # If the files are not identical in codecs/format, you may need to re-encode (remove "-c copy")
    command = [
        "ffmpeg",
        "-y",  # overwrite output if exists
        "-f", "concat",
        "-safe", "0",
        "-i", list_filename,
        "-c", "copy",
        output_path
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as e:
        print("FFmpeg failed with error:")
        print(e.stderr)
        # Cleanup the temporary list file before raising the error
        os.remove(list_filename)
        raise Exception("Video stitching failed.") from e
    
    # Delete the temporary list file
    os.remove(list_filename)
    
    # Delete the input files after successful stitching
    for file_path in input_files:
        try:
            os.remove(file_path)
        except Exception as del_err:
            print(f"Warning: Could not delete {file_path}: {del_err}")
    
    return output_path


#files = ["output_89a4ba08-2d75-497b-b299-3e603edfc562.mp4", "output_89a4ba08-2d75-497b-b299-3e603edfc562.mp4"]
#combined_video = stitch_videos(files)
#print(f"Combined video created at: {combined_video}")

