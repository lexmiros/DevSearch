import os
from openai import OpenAI
from dotenv import load_dotenv


def get_client():
    load_dotenv()
    open_api_key = os.getenv("OPENAI_API_KEY")

    return OpenAI(api_key = open_api_key)

def get_script():
    script_file_path = "./WebScraper/OpenAI/ChatGPTScript.txt"

    with open(script_file_path, 'r') as script:
        script_content = script.read()
    return script_content


def call_gpt_with_script() -> dict:
    client = get_client()
    script = get_script()

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a analyst looking over job adds for the software developer market in Australia"},
            {"role": "user", "content": script}
        ]  
    )
    print(completion.choices[0].message)


if __name__ == "__main__":
    call_gpt_with_script()
