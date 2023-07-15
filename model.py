class Model:

    def __init(self, model_name):
        model_tokens = {
            # input limit for GPT-3.5 Turbo (context 4k, prompt 2.5k, response 1.5k)
            'gpt-3.5-turbo': 2500,
            'gpt-3.5-turbo-0301': 2500,
            # input limit for GPT-4 (context 8k, prompt 6k, response 2k)
            'gpt-4': 6000,
            'gpt-4-0314': 6000,
            'gpt-4-0613': 6000,
        }

        self.token_limit = model_tokens[model_name]

    def get_response(self, messages, model_name):
        try:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=messages,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logging.error(e)
            return "OpenAI API error. Please try again later."

