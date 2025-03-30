import ffmpeg
import csv
import time

class Timer:
    def __init__(self, video_path, topic):
        self._start_time = None
        self.video_path = video_path
        self.topic = topic

    def start(self):
        """Start the timer by setting the start time."""
        self._start_time = time.perf_counter()

    def end(self):
        """
        End the timer and return the elapsed time in seconds.
        Raises:
            ValueError: If the timer was not started.
        """
        if self._start_time is None:
            raise ValueError("Timer has not been started. Please call start() before end().")
        elapsed_time = time.perf_counter() - self._start_time
        self._start_time = None  
        return round(elapsed_time, 2)


    def log_watch_time(self, watch_time: float) -> None:
        """
        Appends to a CSV file the topic name and the ratio of watch_time to video duration.
        
        Parameters:
            video_path (str): Path to the input MP4 video file.
            watch_time (float): The time (in seconds) the video was watched.
            topic (str): A string representing the topic.
        """
        # Set the CSV file path internally.
        csv_path = "video_watch_log.csv"
        
        # Probe the video to get its duration.
        """try:
            probe = ffmpeg.probe(self.video_path)
            duration = float(probe['format']['duration'])
        except ffmpeg.Error as e:
            print(f"Error probing the video file: {e}")
            return """
        
        """ if duration <= 0:
            print("Invalid video duration.")
            return """
        duration = 30.00
        print("duration:" , duration)
        print("watch_time:", watch_time)

        # Calculate the watch ratio.
        watch_ratio = watch_time / duration

        # Append the topic and the watch ratio to the CSV file.
        try:
            with open(csv_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([self.topic, watch_ratio])
            print(f"Logged: {self.topic} with watch ratio {watch_ratio:.2f}")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")

# Example usage:
""" timer = Timer()
timer.start()
time.sleep(150)  # Simulate a delay of 1.5 seconds -- replace with user watchtime
video_file = "FinalVideo.mp4"
watch_time_seconds = timer.end()
topic_name = "Cool Project Topic"
log_watch_time(video_file, watch_time_seconds, topic_name) """

##Start the timer as soon as video is displayed to user
##end the timer as soon as the user clicks next video
##pass the watchtimeseconds to the function

