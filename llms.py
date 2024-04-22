from openai import OpenAI

class OpenAIChatManager:
    def __init__(self, model="gpt-3.5-turbo-0125", api_key=None, **kwargs):
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.kwargs = kwargs  # Store additional kwargs

    def chat_query(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **self.kwargs  # Pass all stored kwargs to the API call
            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"Error querying OpenAI Chat: {e}")
            return None


class OpenAICompletionManager:
    def __init__(self, model="gpt-3.5-turbo-instruct", api_key=None, **kwargs):
        self.model = model
        self.client = OpenAI(api_key=api_key)
        self.kwargs = kwargs  # Store additional kwargs

    def query(self, prompt):
        try:
            response = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                **self.kwargs  # Pass all stored kwargs to the API call
            )
            return response.choices[0].text.strip()
        except Exception as e:
            print(f"Error querying OpenAI Completions: {e}")
            return None
