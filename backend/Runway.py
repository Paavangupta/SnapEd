import time, base64
from runwayml import RunwayML
import requests
import os

def gen_video(image):
  print("Converting Image to Clip")
  client = RunwayML()

  # encode image to base64
  with open(image, "rb") as f:
      base64_image = base64.b64encode(f.read()).decode("utf-8")

  # Create a new image-to-video task using the "gen3a_turbo" model
  task = client.image_to_video.create(
    model='gen3a_turbo',
    # Point this at your own image file
    prompt_image=f"data:image/png;base64,{base64_image}",
    prompt_text='Please animate the image to generate a video',
  )
  task_id = task.id

  # Poll the task until it's complete
  time.sleep(10)  # Wait for a second before polling
  task = client.tasks.retrieve(task_id)
  while task.status not in ['SUCCEEDED', 'FAILED']:
    time.sleep(10)  # Wait for ten seconds before polling
    task = client.tasks.retrieve(task_id)

  print('Task complete:', task)

  if task.status != 'SUCCEEDED' or not task.output:
        raise Exception("Video generation failed.")
  
  video_url = task.output[0]
  print("Downloading from:", video_url)
  
  # Download the video and save it locally
  response = requests.get(video_url)
  if response.status_code != 200:
      raise Exception("Failed to download video.")

  # Create a file name and save it in the current directory
  file_name = f"animated_output_{task_id}.mp4"
  file_path = os.path.join(os.getcwd(), file_name)

  with open(file_path, "wb") as f:
      f.write(response.content)

  print(f"✅ Video saved as {file_path}")
  return file_path