import requests

class WriterAgent:
    def __init__(self, api_key):
        self.api_key = api_key

    def write_pitch(self, query, research_data, strategy, country, user_profile):
        """
        Generates the final response with strict 'No Country Name' rules using OpenAI.
        """
        if not self.api_key:
            return "Error: No OpenAI API Key provided."

        # Handle Country Logic
        # Context: We tell the AI about the country so it understands the market.
        # Constraint: We forbid the AI from writing the name.
        target_market = country if country else "Global Market"

        try:
            # The "Ma'am Approved" System Prompt (UNCHANGED)
            system_instruction = f"""
            ### ROLE
            You are {user_profile}.
            Strategy/Tone: {strategy.get('raw_strategy', 'Professional')}
            
            ### CONTEXT (Internal Knowledge Only)
            - You are writing for an audience in: **{target_market}**.
            - Use your knowledge of {target_market} (regulations, currency, habits) to inform your logic.
            
            ### STRICT NEGATIVE CONSTRAINTS (CRITICAL)
            1. **NO LOCATION NAMES:** You must NEVER write the word "{target_market}", specific city names, or regions in the final output.
            2. **NO LOCAL PHRASING:** Do not say "Here in..." or "In our country".
            3. **ANTI-ECHO:** Do not repeat the user's question at the start.
            4. **NO SYMBOLS:** Do not use hyphens (-) or complex symbols.
            
            ### WRITING RULES
            1. **Perspective:** Start with "I predict" or "In my experience" (First Person). Switch to Third Person for facts.
            2. **Flow:** Use "fluffy" but professional human language. Use connecting words. Avoid short, choppy sentences.
            3. **Language:** British English (UK English).
            4. **Length:** Approx 150 words.
            5. **Sentence Lenght**: Must be 25 words or less.
            
            ### RESEARCH DATA TO USE
            {research_data}
            """

            # OpenAI API Configuration
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # Map inputs to OpenAI Message Structure
            # System Role = Your Instructions
            # User Role = The Query + Trigger Task
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"USER QUERY: {query}\n\nTASK: Write the response now."}
                ],
                "temperature": 0.7
            }

            # Execute Request
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status() # Raise error for bad status codes (4xx, 5xx)
            
            # Extract Content
            clean_text = response.json()['choices'][0]['message']['content']
            
            # POST-PROCESSING SAFETY CHECK (Optional)
            # Removes the country name if the AI accidentally slipped it in.
            if country and country.lower() in clean_text.lower():
                clean_text = clean_text.replace(country, "the market")
                
            return clean_text

        except Exception as e:
            return f"Writer Error: {str(e)}"