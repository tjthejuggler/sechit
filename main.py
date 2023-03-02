import random
#import the file 'chatgpt_req.py'
import chatgpt_req
import fake_chatgpt_req
from game_summary import GameSummary
import read_gov_policies

#chatgpt_req.make_request("if there are no oranges, what will you")
game_sum = GameSummary()
game_status = {}

def assign_roles(num_players):
    if num_players < 5 or num_players > 10:
        raise ValueError("Invalid number of players.")
    elif num_players < 7:
        roles = ['Liberal'] * (num_players - 2) + ['Hitler', 'Fascist']
    elif num_players < 9:
        roles = ['Liberal'] * (num_players - 3) + ['Hitler', 'Fascist', 'Fascist']
    else:
        roles = ['Liberal'] * (num_players - 4) + ['Hitler', 'Fascist', 'Fascist', 'Fascist']
    random.shuffle(roles)
    return roles

def distribute_roles(num_players):
    seen_roles = set()
    roles = assign_roles(num_players)
    for i in range(1, num_players):
        input(f"Player "+str(i+1)+": Press any key to reveal your role: ")
        if i > 0:
            print("Previous roles:")
            for j in range(i):
                if j not in seen_roles:
                    print(f"Player {j+1}: Hidden")
            print("-------------")
        if roles[i] == "Fascist":
            fascist_indices = [j+1 for j, role in enumerate(roles) if role == "Fascist" and j != i]
            #if len(fascist_indices) == 1 and num_players < 7:
            hitler_index = next(j+1 for j, role in enumerate(roles) if role == "Hitler")
            if num_players < 7:           
                print(f"Hitler is: Player {hitler_index}")
            else:
                print(f"Your team mates are: Players {', '.join(str(index) for index in fascist_indices)} and Hitler is: Player {hitler_index}")
        elif roles[i] == "Hitler":
            fascist_index = next(j+1 for j, role in enumerate(roles) if role == "Fascist")
            if num_players < 7:
                print(f"Your team mate is: Player {fascist_index}")
        print(f"Your role: {roles[i]}")
        seen_roles.add(i)
        input("Press any key to hide your role.")
        print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    return roles[i]

def handle_request(request_message):
    #call the function from chatgpt_req.py
    game_sum.append(["user",request_message])
    response = fake_chatgpt_req.send_request(game_sum.read())
    game_sum.append(["assistant",response])
    print(game_sum.read()[-1]['content'])

    for item in game_sum.read(): #this is for testing only, it should actually only be seen by the assistant
        print(item['role'],": ",item['content'])

def input_vote_results(num_players, bot_vote):
    vote_results = ""
    for voting_player in range(1, num_players+1):
        if voting_player not in game_status["dead_players"]:
            players_vote = ""
            if voting_player == 1:
                if bot_vote.startswith("Y") or bot_vote.startswith("y") or bot_vote.startswith("J") or bot_vote.startswith("j") or bot_vote.contains("Yes") or bot_vote.contains("yes"):
                    players_vote = "Y"
                else:
                    players_vote = "N"
                players_vote = bot_vote
            else:
                players_vote = input(f"Player {voting_player}: (J)a / (N)ein? ")
                if players_vote == "J" or players_vote == "j" or players_vote == "Y" or players_vote == "y":
                    players_vote = "Y"
                elif players_vote == "N" or players_vote == "n":
                    players_vote = "N"
            vote_results += "p"+voting_player +"-"+ players_vote    
    game_sum.append_to_last_user(["vote_results",vote_results])
    print(game_sum.read())
    passed = vote_results.count("Y") > vote_results.count("N")
    return passed

def input_human_nomination(current_player):
    nomination = input(f"Player {current_player}: Who do you want to nominate? ")
    game_sum.append_to_last_user(["p"+current_player+" nominated p"+nomination])
    print(game_sum.read())

def increase_current_player():
    game_status["current_player"] += 1
    if game_status["current_player"] > game_status["num_players"]:
        game_status["current_player"] = 1

def main():    
    game_status["num_players"] = int(input("Enter the number of players: "))
    bot_role = distribute_roles(game_status["num_players"])
    print("bot role is ", bot_role)
    #randomaly select a number from num_players
    game_status["starting_player"] = random.randint(1, game_status["num_players"]) 
    game_status["game_is_going"] = True
    game_status["current_player"] = game_status["starting_player"]
    game_status["turn_type"] = "nominate"
    game_status["red_policies"] = 0
    game_status["blue_policies"] = 0
    game_status["dead_players"] = []
    while (game_status["game_is_going"]):
        if game_status["turn_type"] == "nominate":
            print("nominate")
        if game_status["turn_type"] == "vote":
            print("vote")
        if game_status["turn_type"] == "policy_chancellor":
            print("policy_chancellor")
        if game_status["turn_type"] == "policy_president":
            print("policy_president")
        if game_status["turn_type"] == "investigate":
            print("investigate")
        if game_status["turn_type"] == "special_election":
            print("special_election")
        if game_status["turn_type"] == "execution":
            print("execution")

        if game_status["current_player"] == 1: #bot's turn
            print("bot's turn")
            if game_status["turn_type"] == "nominate":
                bot_nomination = handle_request("who do you nominate as chancellor?")
                print("bot nominated ", bot_nomination) #maybe it will mess up the bot_nomination, there should be a way to ask again or something
                input("Press any key to see how the bot votes.")
                bot_vote = handle_request("how do you vote?")
                passed = input_vote_results(game_status["num_players"], bot_vote)
                if passed:
                    #show two policies to the bot
                    bot_vote = handle_request(read_gov_policies.show(2))
                    #play the card that the bot selected
                    #add the bots card to the game summary
                    if 
                else:
                    increase_current_player()
                




            #input_vote_results()
                
            
        else:

            print("player's turn")
            if game_status["turn_type"] == "nominate":
                nomination = input("who does player "+game_status["current_player"]+" nominate?")
                
            if game_status["turn_type"] == "vote":
                input_human_vote(game_status["num_players"], game_status["current_player"])

    #while (game_is_going):

main()

# create an instance of the TextVariable class
# game_sum.append(["system","you are a five year old boy who loves insects a rediculous amount"])
# handle_request("what is your favorite thing to do on the weekend?")

# read the current value of the text attribute
# print(game_sum.read())   # output: "Hello, world!"

# # append a new string to the text attribute
# game_sum.append(["user"," How are you?"])
# print(game_sum.read())   # output: "Hello, world! How are you?"

# print(chatgpt_req.send_request([
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Who won the world series in 2000?"},
#         ]))
