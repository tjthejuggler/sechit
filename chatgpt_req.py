import requests

url = "https://api.openai.com/v1/chat/gpt"
prompt = "Hello, how are you?"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_API_KEY"
}
data = {
    "prompt": prompt,
    "temperature": 0.5,
    "max_tokens": 50,
    "stop": "\n"
}

response = requests.post(url, headers=headers, json=data)
print(response.json()["choices"][0]["text"])