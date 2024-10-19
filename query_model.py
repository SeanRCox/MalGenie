import time
import requests
import sys
import os

from dotenv import load_dotenv

class Query:
    def __init__(self, args):
        load_dotenv()
        self.api_token = os.getenv("API_KEY")
        self.api_url = os.getenv("API_URL")
        self.headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        self.system_prompt = os.getenv("MODEL_SYSTEM_PROMPT")
        self.alternate_system_prompt = os.getenv("MODEL_ALTERNATE_SYSTEM_PROMPT")

        self.fix_errors = None
        if len(args) > 2:
            self.fix_errors = True

        self.query_model(args, self.fix_errors)

    def query_model(self, args, fix_errors=None):
        if fix_errors:
            prompt = self.alternate_system_prompt + args[1] + " " + args[2]
        else: 
            prompt = self.system_prompt + args[1]

        prompt += "MALWAREBOT RESPONSE:"

        start = time.time()
        model_output = self.send_query(prompt)
        end = time.time()

        print(model_output)
        generated_text = self.get_response(model_output)
        print(self.extract_code(generated_text))  # Print model output to stdout

        self.log_response(prompt, model_output, start, end)

    def send_query(self, model_input):
        response = requests.post(self.api_url, headers=self.headers, 
                                 json={"inputs": model_input, "parameters": {"max_new_tokens": 2500}})
        return response.json()
    
    def get_response(self, response):
        if isinstance(response, list) and len(response) > 0:
            response_json = response[0]
            return response_json['generated_text']
        return 'Error getting response'

    def extract_code(self, generated_text):
        # Find the start and end of the C code block
        start_code = generated_text.find("```c")
        end_code = generated_text.find("```", start_code + 3)

        if start_code != -1 and end_code != -1:
            return generated_text[start_code + 4:end_code].strip()
        else: 
            return "No C code found"
        
    def log_response(self, prompt, response, start, end):
        local_time = time.localtime(end)
        time_string = time.strftime("%m-%d_%H-%M.txt", local_time)
        file_name = "output/model_output_" + time_string

        with open(file_name, "w") as f:
            f.write(prompt)
            f.write(f"Total runtime: {end-start} seconds\n")
            f.write(str(response))

if __name__=="__main__":
    Query(sys.argv)