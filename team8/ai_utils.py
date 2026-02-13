import os
import requests
import json
import urllib3
import random

class AIService:
    def __init__(self):
        # We use the environment variable for the key
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        # Disable SSL warnings if needed for your environment
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.model = "llama-3.1-8b-instant" 

    def fetch_word_info(self, word=None, level="A2"):
        # 1. Logic for Randomness:
        # If no word is provided, we randomly select a topic and a starting letter
        # This forces the AI to generate something different every time.
        if word:
            target = f"the word '{word}'"
            temp_setting = 0.5 # Low creativity for specific definitions
        else:
            topics = ["technology", "emotions", "business", "nature", "travel", "philosophy", "arts", "science", "daily life"]
            letters = "abcdefghlmnoprstuvw" 
            random_topic = random.choice(topics)
            random_letter = random.choice(letters)
            
            target = f"a random, useful {level} level English vocabulary word related to '{random_topic}' or starting with the letter '{random_letter}'"
            temp_setting = 1.1 # High creativity for random generation

        system_prompt = (
            f"You are an English teacher. Provide details for {target} in strict JSON format. "
            "Use these keys: 'word', 'ipa', 'definition', 'synonyms', 'antonyms', 'collocations', 'examples'. "
            "Synonyms, antonyms, collocations, and examples MUST be arrays of strings."
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": temp_setting
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        response = requests.post(self.url, headers=headers, json=payload, timeout=45, verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    def generate_mnemonic_story(self, word):
        system_prompt = (
            f"You are a creative memory expert. For the English word '{word}', "
            "create a short, vivid visual mnemonic (max 2 sentences) and a short memory story (2-3 sentences). "
            "Return valid JSON with keys: 'mnemonic_text' and 'story_text'."
        )
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.8
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        response = requests.post(self.url, headers=headers, json=payload, timeout=45, verify=False)
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return json.loads(content)

    def generate_image_hf(self, prompt, retry_count=0):
    """
    Generate an image using multiple fallback services.
    Always returns a URL – either AI‑generated or a stable placeholder.
    """
    import time
    import urllib.parse
    import requests
    import os
    import random

    # ----- 1. Hugging Face (Stable Diffusion 2.1) -----
    hf_token = os.environ.get("HF_TOKEN")
    if hf_token:
        try:
            api_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
            headers = {"Authorization": f"Bearer {hf_token}"}
            response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=30)
            if response.status_code == 200:
                img_base64 = base64.b64encode(response.content).decode('utf-8')
                print("✅ Hugging Face SD2.1 success")
                return f"data:image/png;base64,{img_base64}"
            else:
                print(f"⚠️ Hugging Face SD2.1 failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Hugging Face SD2.1 exception: {e}")

    # ----- 2. Hugging Face (FLUX.1-dev – often works without terms) -----
    if hf_token:
        try:
            api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
            headers = {"Authorization": f"Bearer {hf_token}"}
            response = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=30)
            if response.status_code == 200:
                img_base64 = base64.b64encode(response.content).decode('utf-8')
                print("✅ Hugging Face FLUX.1-dev success")
                return f"data:image/png;base64,{img_base64}"
            else:
                print(f"⚠️ Hugging Face FLUX.1-dev failed: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Hugging Face FLUX.1-dev exception: {e}")

    # ----- 3. Pollinations.ai (with fallback to a simple working prompt) -----
    try:
        # Simplify the prompt – sometimes long prompts trigger the 1033 error
        short_prompt = prompt.split(',')[0]  # take only the word
        encoded = urllib.parse.quote(short_prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{encoded}?width=512&height=512&nologo=true"
        
        # Test if the endpoint works for this prompt (HEAD request)
        head_resp = requests.head(pollinations_url, timeout=5)
        if head_resp.status_code == 200:
            print("✅ Pollinations success")
            return pollinations_url
        else:
            print(f"⚠️ Pollinations returned {head_resp.status_code}")
    except Exception as e:
        print(f"⚠️ Pollinations exception: {e}")

    # ----- 4. Ultimate fallback – a real, always‑working image -----
    # Using LoremFlickr with a keyword from the prompt
    keyword = prompt.split(',')[0].strip().replace(' ', '_')
    fallback_url = f"https://loremflickr.com/512/512/{keyword}"
    print(f"🟡 Using fallback image: {fallback_url}")
    return fallback_url

    def generate_practice_set(self, word):
        """
        Generates 4 practice exercises using the requests library to match 
        the rest of the class architecture.
        """
        prompt = f"""
        Generate 4 English practice exercises for the word: "{word}".
        Return ONLY a JSON object with a key "exercises" containing an array of 4 objects.
        The array must follow this order: 
        1. Meaning (Multiple Choice)
        2. Context (Multiple Choice)
        3. Collocation (Multiple Choice)
        4. Sentence (Multiple Choice)

        Format:
        {{
        "exercises": [
            {{
            "question": "What is the meaning of '{word}'?",
            "options": ["option1", "option2", "option3", "option4"],
            "answer": "correct_option"
            }},
            ...
        ]
        }}
        """

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}", 
            "Content-Type": "application/json"
        }

        # We call the API using requests, just like fetch_word_info
        response = requests.post(self.url, headers=headers, json=payload, timeout=45, verify=False)
        response.raise_for_status()
        
        # Return the content string just like the WordCard view expects
        return response.json()['choices'][0]['message']['content']