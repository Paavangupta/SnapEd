import os
import time
import requests
import modal

# Create a Modal stub
stub = modal.Stub("ai-image-generator")

@stub.function(cpu=2, memory=4096, timeout=120)
def generate_image_modal(prompt: str, max_retries: int = 3, retry_delay: int = 15) -> str:
    """
    Generates an image using DALL-E via OpenAI's API with retries, saves the image locally, and returns the save path.
    
    Parameters:
        prompt (str): The text prompt for image generation.
        max_retries (int): Maximum number of retries in case of a rate limit error.
        retry_delay (int): Seconds to wait between retries.
    
    Returns:
        str: The local file path where the generated image is saved, or None on failure.
    """
    import openai
    from openai import RateLimitError, APIError

    # Configure the OpenAI API key (ensure this is set as a Modal secret or in the environment)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment variables.")
    openai.api_key = OPENAI_API_KEY

    retries = 0
    while retries < max_retries:
        try:
            response = openai.images.generate(
                model="dall-e-3",  # or "dall-e-2" if necessary
                prompt=prompt,
                size="1024x1024",  # Standard size
                quality="standard",  # or "hd"
                n=1,
                response_format="url"
            )
            image_url = response.data[0].url
            print(f"Successfully generated image for prompt: {prompt}")

            # Create a unique filename based on the current time
            save_path = os.path.join("images", f"image_{int(time.time())}.jpg")
            os.makedirs("images", exist_ok=True)
            img_data = requests.get(image_url).content
            with open(save_path, "wb") as f:
                f.write(img_data)
            print(f"Saved image to {save_path}")
            return save_path

        except RateLimitError as e:
            retries += 1
            print(f"Rate limit error (Attempt {retries}/{max_retries}): {e}. Retrying in {retry_delay}s...")
            if retries >= max_retries:
                print("Max retries reached. Returning None.")
                return None
            time.sleep(retry_delay)
        except APIError as e:
            print(f"OpenAI API error generating image: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error generating image: {e}")
            return None

    # If we exit the loop unexpectedly, return None.
    return None

if __name__ == "__main__":
    # For local testing: call the Modal function synchronously.
    test_prompt = "A futuristic city skyline at sunset, digital art"
    image_path = generate_image_modal.call(test_prompt)
    print("Generated image path:", image_path)