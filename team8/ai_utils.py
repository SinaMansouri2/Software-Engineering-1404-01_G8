import os
import requests
import json
import urllib3
class AIService:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.model = "llama-3.1-8b-instant" 

    def fetch_word_info(self, word=None, level="B2"):
        target = f"the word '{word}'" if word else f"a random useful {level} level English vocabulary word"
        
        system_prompt = (
            f"You are an English teacher. Provide details for {target} in strict JSON format. "
            "Use these keys: 'word', 'ipa', 'definition', 'synonyms', 'antonyms', 'collocations', 'examples'. "
            "Synonyms, antonyms, collocations, and examples MUST be arrays of strings."
        )

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.7
        }

        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        
        response = requests.post(self.url, headers=headers, json=payload, timeout=45,verify=False)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']