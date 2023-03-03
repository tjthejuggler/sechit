import random
#import the file 'chatgpt_req.py'
import chatgpt_req
import fake_chatgpt_req
from game_summary import GameSummary
import read_gov_policies

#chatgpt_req.make_request("if there are no oranges, what will you")
game_sum = GameSummary()

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
        if i > 0: #IS THIS EVER USED?
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
    return roles

def handle_request(request_message):
    #call the function from chatgpt_req.py
    game_sum.append(["user",request_message])
    response = fake_chatgpt_req.send_request(game_sum.read())
    game_sum.append(["assistant",response])
    print(game_sum.read()[-1]['content'])

    for item in game_sum.read(): #this is for testing only, it should actually only be seen by the assistant
        print(item['role'],": ",item['content'])

def input_vote_results(num_players, bot_vote, dead_players):
    vote_results = ""
    for voting_player in range(1, num_players+1):
        if voting_player not in dead_players:
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
                else:
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

def increase_current_player(current_player, num_players):
    current_player += 1
    if current_player > num_players:
        current_player = 1
    return current_player

def check_for_policy_game_completion(fascist_policies, liberal_policies):
    game_is_going = True
    if fascist_policies == 6 or liberal_policies == 5:
        game_is_going = False
        print("game is over")
    return game_is_going

def check_for_special_power(num_players, num_fascist_policies, player_number):
    if (num_players in [5,6]) and num_fascist_policies == 3:
        if player_number == 1:
            #SHOW BOT THE TOP 3 CARDS
            print("You are the Chancellor. You may look at the top 3 cards of the policy deck.")
        else:
            #SHOW PLAYER THE TOP 3 CARDS
            print("The Chancellor is looking at the top 3 cards of the policy deck.")
    elif (num_players in [7,8] and num_fascist_policies == 2) or (num_players in [9,10] and num_fascist_policies in [1,2]):
        if player_number == 1:
            #ASK BOT TO INVESTIGATE A PLAYER
            print("bot investigate")
        else:
            #ASK PLAYER TO INVESTIGATE A PLAYER
            print("player investigate")
    elif (num_fascist_policies in [4,5]):
        if player_number == 1:
            #ASK BOT TO KILL A PLAYER
            print("bot kill")
        else:
            #ASK PLAYER TO KILL A PLAYER
            print("player kill")

def make_read_policies_question(read_cards):
    policies_question = "you have been given the following policies: "
    for i, policy in enumerate(read_cards):
        if policy == "fascist":
            policies_question += str(i)+")fascist "
        else:
            policies_question += str(i)+")liberal "
                
    policies_question += ". Which policy would you like to enact? Answer with the number of the policy only."
    return policies_question

def check_for_veto(cards_seen, bots_role, current_chancellor, known_fascists, num_liberal_policies, num_fascist_policies):
    ask_for_veto = False
    policies_vetoed = False
    if bots_role == "Hitler" or (bots_role == "Fascist" and current_chancellor in known_fascists):
        if num_liberal_policies == 4 and cards_seen.count("liberal") == 2:
            ask_for_veto = True
    else:
        if num_fascist_policies == 5 and cards_seen.count("fascist") == 2:
            ask_for_veto = True
    if ask_for_veto:
        chancellor_response = input("Chancellor, would you like to veto this policy? (J)a / (N)ein? ")
        if chancellor_response == "J" or chancellor_response == "j" or chancellor_response == "Y" or chancellor_response == "y":
            policies_vetoed = True
    return policies_vetoed
        
def tell_bot_fellow_fascists_if(player_roles, num_players):
    hitler_index = [i for i, x in enumerate(player_roles) if x == "Hitler"]
    fascist_index = [i for i, x in enumerate(player_roles) if x == "Fascist"]
    known_fascists = []
    if num_players in [5,6]:
        if player_roles[0] == "Fascist":
            game_sum.append_to_last_user(["Hitler is p"+hitler_index[0]])
            known_fascists.append(hitler_index[0])
        elif player_roles[0] == "Hitler":
            game_sum.append_to_last_user(["The regular fascist is p"+fascist_index[0]])
            known_fascists.append(fascist_index[0])
    elif num_players in [7,8]:
        if player_roles[0] == "Fascist":
            game_sum.append_to_last_user(["Hitler is p"+hitler_index[0]+" and the other fascist is p"+fascist_index[1]])
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
    elif num_players in [9,10]:
        if player_roles[0] == "Fascist":
            game_sum.append_to_last_user(["Hitler is p"+hitler_index[0]+" and the other fascists are p"+fascist_index[1]+" and p"+fascist_index[2]])
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
            known_fascists.append(fascist_index[2])
    return(known_fascists)   

def show_game_state(game):
    for key, value in game.items():
        print(key, ":", value)

def main():
    game = {}  
    game["num_players"] = int(input("Enter the number of players: "))
    game["player_roles"] = distribute_roles(game["num_players"])
    game["known_fascists"] = tell_bot_fellow_fascists_if(game["player_roles"], game["num_players"])
    #randomaly select a number from num_players
    game["bot_role"] = game["player_roles"][0]
    game["starting_player"] = random.randint(1, game["num_players"]) 
    game["game_is_going"] = True
    game["current_player"] = game["starting_player"]
    #game["current_chancellor"] = 0
    game["num_fascist_policies"] = 0
    game["num_liberal_policies"] = 0
    game["dead_players"] = []
    show_game_state(game)
    while (game["game_is_going"]):
        if game["current_player"] == 1: #bot's turn
            print("bot's turn")
            bot_nomination = handle_request("who do you nominate as chancellor? answer with their player number only.")
            print("bot nominated ", bot_nomination) #maybe it will mess up the bot_nomination, there should be a way to ask again or something
            input("Press any key to see how the bot votes.")
            bot_vote = handle_request("how do you vote?")
            passed = input_vote_results(game["num_players"], bot_vote, game["dead_players"])
            if passed:
                #game["current_chancellor"] = bot_nomination
                if game["bot_role"] == "Hitler" and game["num_fascist_policies"] == 3:
                    print("Fascists Win due to Hitlerbot being President!")
                cards_seen = read_gov_policies.show(2)
                policies_vetoed = check_for_veto(cards_seen, game["bot_role"], bot_nomination, game["known_fascists"], game["fascist_policies"], game["liberal_policies"])
                if not policies_vetoed:
                    bot_vote = handle_request(make_read_policies_question(cards_seen))
                    bots_card = input("what card does the bot play? (F)ascist or (L)iberal?")
                    if bots_card == "F" or bots_card == "f":
                        bots_card = "fascist"
                    else:
                        bots_card = "liberal"
                    game_sum.append_to_last_user(["You played a "+bots_card+" policy."])
                    if bots_card == "fascist":
                        game["fascist_policies"] += 1
                        check_for_special_power(game["fascist_policies"], game["current_player"])
                    else:
                        game["liberal_policies"] += 1
                    game["game_is_going"] = check_for_policy_game_completion(game["fascist_policies"], game["current_player"])
            game["current_player"] = increase_current_player(game["current_player"], game["num_players"])
        else:
            print("player's turn")
            if game["turn_type"] == "nominate":
                nomination = input("who does player "+game["current_player"]+" nominate?")                
            if game["turn_type"] == "vote":
                input_human_vote(game["num_players"], game["current_player"])

    #while (game_is_going):

main()

# create an instance of the TextVariable class
# game_sum.append(["system","you are a five year old boy who loves insects a fascisticulous amount"])
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
