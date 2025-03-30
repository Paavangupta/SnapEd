import os
import modal

stub = modal.Stub("ai-script-generator")

@stub.function(cpu=2, memory=4096, timeout=60, secrets=[modal.Secret.from_name("gemini-secret")])
def generate_script_modal(prompt: str) -> str:
    import google.generativeai as genai

    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=GEMINI_API_KEY)

    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    response = gemini_model.generate_content(prompt)
    return response.text.strip()
