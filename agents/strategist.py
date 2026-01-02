import requests

class StrategistAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def analyze_query(self, query, user_profile):
        """
        Determines the tone and angle using GPT-4o-mini.
        """
        if not self.api_key:
            return {"error": "Missing OpenAI API Key"}

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        system_prompt = f"""
        Role: Expert PR Strategist.
        Query: "{query}"
        My Profile: "{user_profile}"
        
        Task: Define the winning strategy to get featured.
        1. What is the best TONE? (e.g., Authoritative, Empathetic, Data-Driven)
        2. What is the best ANGLE? (e.g., Contrarian view, Personal story, Hard stats)
        
        Output Format (Strict Text):
        Tone: [Tone]
        Angle: [Angle]
        """

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful PR strategist."},
                {"role": "user", "content": system_prompt}
            ],
            "temperature": 0.7
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status() # Raise error for bad status codes
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return {"raw_strategy": content}
            
        except Exception as e:
            return {"error": str(e)}