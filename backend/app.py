print("📦 app.py loaded")
import os
print("HERE -8")
import random
print("HERE -7")
import threading
print("HERE -6")
import time
print("HERE -5")
from flask import Flask, request, jsonify, send_from_directory
print("HERE -4")
from flask_cors import CORS
print("HERE -3")
from dotenv import load_dotenv
print("HERE -2")
import google.generativeai as genai
print("HERE -1")
import openai
from openai import RateLimitError, APIError
print("HERE 0")
import requests
print("HERE 1")
import Audio
print("HERE 2")
import Video
print("HERE 3")
import FinalVideo
print("HERE 4")
import UserData
import Runway
import gifToMp4
from threading import Event

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure Flask app and CORS
app = Flask(__name__)
CORS(app) # Allow requests from the frontend origin

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash') # Using 1.5 flash as 2.0 is not available via the SDK yet

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Assuming OPENAI_API_KEY is also in .env
if not OPENAI_API_KEY:
     # If you only have one key, Gemini key will be used for OpenAI as well.
     # This might not work depending on OpenAI's key format/validation.
     # It's recommended to have a separate OPENAI_API_KEY.
    print("Warning: OPENAI_API_KEY not found. Attempting to use GEMINI_API_KEY for OpenAI.")
    OPENAI_API_KEY = GEMINI_API_KEY
    # raise ValueError("OPENAI_API_KEY not found in environment variables.") # Or raise error

openai.api_key = OPENAI_API_KEY

# --- Global State ---
used_topics = [] # Initialize the list to store used topics
timer = None
next_video_data = None
stop_preload_event = Event()

# --- Helper Functions ---
def generate_image(prompt, results_list, index, max_retries=3, retry_delay=15):
    """Generates an image using DALL-E, with retries for rate limits."""
    retries = 0
    while retries < max_retries:
        try:
            response = openai.images.generate(
                model="dall-e-3", # Or "dall-e-2" if needed
                prompt=prompt,
                size="1024x1024", # Standard size
                quality="standard", # or "hd"
                n=1,
                response_format="url"
            )
            results_list[index] = response.data[0].url
            print(f"Successfully generated image for index {index}.") # Add success log

            # ⬇️ Save the image as "image {index}.jpg" in the images folder
            save_path = os.path.join("images", f"image {index}.jpg")
            os.makedirs("images", exist_ok=True)
            img_data = requests.get(response.data[0].url).content
            with open(save_path, "wb") as f:
                f.write(img_data)
            print(f"Saved image to {save_path}")

            return save_path # Exit function on success

        except RateLimitError as e:
            retries += 1
            print(f"Rate limit error generating image for index {index} (Attempt {retries}/{max_retries}): {e}. Retrying in {retry_delay}s...")
            if retries >= max_retries:
                print(f"Max retries reached for index {index}. Setting result to None.")
                results_list[index] = None
                return # Exit function after max retries
            time.sleep(retry_delay) # Wait before retrying

        except APIError as e: # Catch other specific OpenAI API errors
             print(f"OpenAI API error generating image for index {index}: {e}")
             results_list[index] = None
             return # Exit function on non-retriable API error
        except Exception as e: # Catch any other unexpected errors
            print(f"Unexpected error generating image for index {index}: {e}")
            results_list[index] = None
            return # Exit function on other errors

    # Safeguard if loop finishes unexpectedly
    if results_list[index] is None:
         print(f"Failed to generate image for index {index} after {max_retries} retries.")

def generate_partial_video(sentence, prompt, image_results, video_results, i, max_retries=3, retry_delay=15):
    if stop_preload_event.is_set():
        print(f"⛔️ Thread {i} stopped before starting.")
        return
    
    image = generate_image(prompt, image_results, i, max_retries, retry_delay)

    if stop_preload_event.is_set():
        print(f"⛔️ Thread {i} stopped after image gen.")
        return

    #video = Runway.gen_video(image)
    # Randomly choose an accent and gender
    accent = random.choice(["UK", "US"])
    gender = random.choice(["MALE", "FEMALE", "NEUTRAL"])
    audio = Audio.convert_text_to_mp3(sentence, accent, gender)

    if stop_preload_event.is_set():
        print(f"⛔️ Thread {i} stopped after audio gen.")
        return

    video_results[i] = Video.create_video_with_fade(image, audio)
    #video_results[i] = gifToMp4.add_audio_to_video(video, audio)
    

def generate_script(selected_topic):
    # 2. Generate script using Gemini
    prompt = (
        f"Choose a specific and interesting subtopic related to '{selected_topic}', and explain it clearly in four connected sentences. "
        "Start your response with a <t> tag containing the specific topic being explained. "
        "Then, write four engaging and educational sentences that flow together to explain the concept in a way that is easy to visualize and understand. "
        "Make the explanation suitable for a general audience, avoiding technical jargon, and include vivid imagery or real-world metaphors when helpful. "
        "Each sentence should be enclosed in <s> and </s> tags. "
        "Do not include any extra commentary or explanation — just return the title in <t> and the four sentences in <s> blocks.\n\n"
        "Example for topic 'Black Holes':\n"
        "<t>What happens if you fall into a black hole?</t>\n"
        "<s>If you fell into a black hole, you’d be stretched like spaghetti by its intense gravity.</s>\n"
        "<s>This process is called 'spaghettification' — yes, that’s the real word scientists use.</s>\n"
        "<s>The closer you get to the center, the more time slows down for you compared to the outside world.</s>\n"
        "<s>Eventually, you'd cross the event horizon — the point of no return — and disappear from view forever.</s>\n\n"
        f"Now write a similar explanation for the topic: '{selected_topic}'"
        f"Make sure it is not about any of the following: '{str(used_topics)}'"
    )
    response = gemini_model.generate_content(prompt)
    script_text = response.text.strip()
    script_sentences = [s.split('</s>')[0].strip() for s in script_text.split('<s>') if '</s>' in s]
    specific_topic = [s.split('</t>')[0].strip() for s in script_text.split('<t>') if '</t>' in s][0]
    print(f"Specific Topic: {specific_topic}")
    used_topics.append(specific_topic)

    # Ensure exactly four sentences, pad or truncate if necessary (basic handling)
    if len(script_sentences) > 4:
        script_sentences = script_sentences[:4]
    while len(script_sentences) < 4:
        # Attempt to generate more or use placeholder - simple placeholder for now
        print(f"Warning: Generated script for '{selected_topic}' has less than 4 sentences. Padding.")
        script_sentences.append(f"({selected_topic} continued...)") # Placeholder

    print(f"Generated Script for '{selected_topic}':\n{script_text}") # Print script to backend console

    return script_sentences

def gen_video(topics):
    try:
        selected_topic = random.choice(topics)
        script_sentences = generate_script(selected_topic)

        image_styles = ["A photorealistic DSLR-quality photo. The image should resemble a real photograph captured with a high-end camera using natural lighting. "
            "Include realistic skin tones, natural shadows, sharp depth of field, accurate human proportions, and environmental detail such as grass, trees, or buildings as applicable. "
            "Textures (clothing, objects, surfaces) should be highly detailed and authentic. "
            "Avoid all illustrations, CGI, stylization, drawings, or unrealistic rendering. "
            "Do not include any text, watermarks, logos, or symbols.", 

            f"A documentary-style real-world image. The image should resemble an unfiltered moment captured by a field journalist using a professional DSLR or mirrorless camera. "
            "Use soft, natural lighting, realistic skin tones, and subtle environmental noise like dust or uneven ground. "
            "Focus on authenticity — slight motion blur, imperfect framing, or subtle imperfections can be present. "
            "Avoid stylization, dramatic color grading, animation-like clarity, or artificial scene composition. "
            "Do not include text, symbols, or overlays in the image.",
            
            f"A vintage 1970s film-style image. The image should resemble a photograph taken on a 1970s analog camera using film stock like Kodak Ektachrome or Fujifilm. "
            "Use slightly faded colors, warm tones, film grain, and natural light leaks to give it a nostalgic and aged appearance. "
            "Skin tones should be slightly desaturated, with vintage-style clothing and soft focus around the edges. "
            "Avoid modern photography sharpness, clean gradients, or digitally crisp textures. "
            "Do not include text, logos, or anachronistic elements.",
            
            f"A noir-style black and white photograph. The image should be high contrast, moody, and resemble classic film noir shots with dramatic shadows and strategic lighting. "
            "Use strong directional lighting, long shadows, and high black-point contrast to highlight form and mood. "
            "Include period-appropriate environments if possible, with realistic clothing and grainy textures. "
            "Avoid color, modern objects, flat lighting, or stylistic over-editing. "
            "Do not include any logos, watermarks, or graphical overlays.",
            
            f"A soft watercolor illustration. The image should resemble a hand-painted watercolor artwork on textured paper, using pastel tones, soft gradients, and fluid color blending. "
            "Edges should be loose and organic, with transparency in overlapping areas and natural paper bleed. "
            "Focus on mood, simplicity, and emotional tone over fine detail. "
            "Avoid hard lines, digital sharpness, or photorealism. "
            "Do not include text, filters, or overlays.",
            
            f"A childlike crayon drawing. The image should resemble a drawing made by a child using crayons on white paper, with bold primary colors, uneven lines, and playful interpretation of shapes. "
            "Perspective may be exaggerated or naive, with expressive creativity over realism. "
            "Backgrounds can be simple, textured with scribbles or clouds, and outlines should be rough or shaky. "
            "Avoid polished textures, realism, or structured composition. "
            "Do not add any logos, overlays, or digital effects.",

            f"A 2D cel-shaded animation still. The image should resemble a frame from a hand-drawn animated film like those by Studio Ghibli, with clean line work, flat shading, and painterly backgrounds. "
            "Use expressive facial features, exaggerated poses, and harmonious color palettes. "
            "Shadows should be soft and layered with visible flat tone shading. "
            "Avoid 3D rendering, photo textures, or hyperrealism. "
            "Do not include text, studio logos, or UI elements.",
            
            f"A comic book panel. The image should resemble a page from a modern graphic novel or superhero comic, with bold ink lines, dramatic poses, and high-contrast colors. "
            "Use halftone shading, dynamic action lines, and exaggerated anatomy when appropriate. "
            "Facial expressions and scenes should be intense and stylized, capturing emotion and motion. "
            "Avoid photographic realism, gradients, or painterly rendering. "
            "Do not include speech bubbles, text captions, or watermarks.",
            
            f"A classic Disney-style animation frame. The image should resemble a frame from a hand-drawn Disney film from the 1940s–1990s, with expressive cartoon characters, painterly backgrounds, and clear color blocking. "
            "Use clean ink lines, subtle shading, and storybook-style lighting. "
            "Character poses should be dynamic and animated with strong silhouettes and emotion. "
            "Avoid 3D effects, overly modern digital polish, or realism. "
            "Do not include captions, logos, or UI.",
            ]
        
        image_style = random.choice(image_styles)
        image_prompts = [s.strip() + " " + image_style + " This is the general topic: " + used_topics[-1] for s in script_sentences]

        print("**********************USED TOPICS********************" + str(used_topics))

        image_results = [None] * len(image_prompts)
        video_results = [None] * len(image_prompts)
        threads = []

        for i, prompt in enumerate(image_prompts):
            thread = threading.Thread(target=generate_partial_video, args=(script_sentences[i], prompt, image_results, video_results, i))
            threads.append(thread)
            time.sleep(1)
            thread.start()

        for thread in threads:
            thread.join()

        final_video_path = FinalVideo.stitch_videos(video_results)
        video_url = f"/videos/{os.path.basename(final_video_path)}"

        return {
            "script": script_sentences,
            "image_urls": image_results,
            "video_url": video_url,
            "topic": selected_topic
        }
    except Exception as e:
        print(f"Error preloading next video: {e}")
        return None

def preload_next_video(topics):
    global next_video_data
    print("🔄 Preloading next video...")
    next_video_data = gen_video(topics)
    print("✅ Next video preloaded.")


# --- API Endpoints ---
@app.route('/generate', methods=['POST'])
def generate_video_data():
    global used_topics, timer, next_video_data
    stop_preload_event.clear()

    if timer is not None:
        watch_time_seconds = timer.end()
        timer.log_watch_time(watch_time_seconds)

    data = request.get_json()
    topics = data.get('topics')

    if not topics or not isinstance(topics, list) or len(topics) == 0:
        return jsonify({"error": "Invalid or missing 'topics' list"}), 400

    valid_topics = [topic for topic in topics if topic and topic.strip()]
    if not valid_topics:
        return jsonify({"error": "No valid topics provided"}), 400

    print("📤 Returning preloaded video if available...")

    try:
        # If preloaded, serve it and begin preloading the next
        if next_video_data:
            served_data = next_video_data
            next_video_data = None

            timer = UserData.Timer(served_data["video_url"], served_data["topic"])
            timer.start()

            # Start generating the next video in background
            threading.Thread(target=preload_next_video, args=(valid_topics,)).start()

            return jsonify({
                "script": served_data["script"],
                "image_urls": served_data["image_urls"],
                "video_url": served_data["video_url"]
            })

        # If not preloaded, generate normally and preload after
        print("❌ No preloaded video found. Generating now...")
        video = gen_video(topics)

        timer = UserData.Timer(video["video_url"], video["topic"])
        timer.start()

        # Start next one in background
        threading.Thread(target=preload_next_video, args=(valid_topics,)).start()

        return jsonify({
            "script": video["script"],
            "image_urls": video["image_urls"],
            "video_url": video["video_url"]
        })

    except Exception as e:
        print(f"Error in /generate endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/reset_topics', methods=['POST'])
def reset_used_topics():
    """
    Clears the list of recently used topics stored in the backend.
    """
    global used_topics
    used_topics.clear()
    preload_next_video = None
    stop_preload_event.set()
    print("Reset Videos, Next Video: " + str(preload_next_video))
    print("Used topics list has been reset.")
    return jsonify({"message": "Used topics reset successfully"}), 200

@app.route('/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory('.', filename)

# --- Run Flask App ---
if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible on the network if needed,
    # otherwise 127.0.0.1 (localhost) is safer.
    print("🚀 Flask app is starting on http://127.0.0.1:5001 ...")
    app.run(host='127.0.0.1', port=5001, debug=True) # Using port 5001 to avoid potential conflicts