import random

num_players = 5

def send_request(request_message):
    # with open('api_key.txt', 'r') as f:
    #     api_key = f.read().strip()
    # openai.api_key = (api_key)
    # response = openai.ChatCompletion.create(
    # model="gpt-3.5-turbo",
    # messages=request_message
    # )
    last_item = request_message[-1]["content"]
    response = ""

    print("last_item", last_item)

    if "nominate" in last_item:
        choices = [int(char) for char in last_item if char.isdigit()]
        response = str(random.choice(choices))
    elif "How do you vote?" in last_item:
        #randomly choose yes or no
        response = random.choice(["yes", "no"])
    elif "2)" in last_item:
        response = str(random.randint(1, 2))
    elif "3)" in last_item:
        response = str(random.randint(1, 3))
    else: 
        response = last_item+"response"

    #get last item of request_message
    
    return(response)

# print(send_request([
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Who won the world series in 2000?"},
#         ]))

#print(response)