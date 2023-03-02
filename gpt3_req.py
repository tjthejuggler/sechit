import requests

def make_request(prompt_text):
    with open('api_key.txt', 'r') as f:
        api_key = f.read().strip()

    url = "https://api.openai.com/v1/engines/curie/completions"
    prompt = prompt_text
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer "+api_key,
    }
    data = {
        "prompt": prompt,
        "temperature": 0.5,
        "max_tokens": 50,
        "stop": "\n"
    }

    response = requests.post(url, headers=headers, json=data)

    if "choices" in response.json():
        print(response.json()["choices"][0]["text"])
    else:
        print("No response from the API")

#make_request()