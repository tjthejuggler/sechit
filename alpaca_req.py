import requests

#to use this you must first run this command in a seperate terminal:
#sudo docker run -p 8080:8080 -ti --rm quay.io/go-skynet/llama-cli:latest api

url = 'http://localhost:8080/predict'
headers = {'Content-Type': 'application/json'}
data = {
    "text": "What is an alpaca?",
    "topP": 0.8,
    "topK": 50,
    "temperature": 0.7,
    "tokens": 100
}
response = requests.post(url, headers=headers, json=data)
response_string = response.text

#just key the value of the prediction key
response_string = response_string[response_string.find("prediction")+13:-3].replace('\\n', '')

print(response_string)
