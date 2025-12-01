# backend/app/utils/llm_client.py
import os
import google.generativeai as genai
# import the SDK of your LLM provider here
# e.g., from openai import OpenAI

class LLMClient:
    def __init__(self):
        # load API key / init client
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            "gemini-2.5-flash-lite",
            generation_config ={
                "response_mime_type": "application/json"
             }
            )

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """
        Returns raw text response from LLM.
        For realism_agent we’ll ask it to output JSON.
        """
        # Call your provider here.
        # Example pseudo:
        # resp = client.responses.create(model="...", input=[{"role": "system", "content": system_prompt}, {...}])
        # return resp.output[0].content[0].text
        full_prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
        response = self.model.generate_content(full_prompt)

        print("\n\n=== SENDING TO GEMINI ===")
        print(full_prompt)
        print("==========================\n")

        print("\n\n=== GEMINI RAW RESPONSE OBJECT ===")
        print(response)
        print("==========================\n")

        return response.text if hasattr(response, 'text') else str(response) 
    

llm_client = LLMClient()
