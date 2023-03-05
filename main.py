import random
#import the file 'chatgpt_req.py'
import chatgpt_req
import fake_chatgpt_req
from game_summary import GameSummary
import read_gov_policies
import bot_speak
import sys
import auto_dict
import json
import os

cwd = os.getcwd()

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

def clear_console_lines(count):
    # use '\033[F' to move the cursor up one line, use '\r' to return the cursor to the beginning of the line
    for i in range(count):
        sys.stdout.write('\033[F\r')
        sys.stdout.write(' ' * 100)
    sys.stdout.write('\r')
    sys.stdout.flush()

def distribute_roles(num_players):
    seen_roles = set()
    roles = assign_roles(num_players)
    for i in range(1, num_players):
        
        input(f"You are Player "+str(i+1)+": Press any key to reveal your role: ")
        # if i > 0: #IS THIS EVER USED?
        #     print("Previous roles:")
        #     for j in range(i):
        #         if j not in seen_roles:
        #             print(f"Player {j+1}: Hidden")
        #     print("-------------")
        text_to_show = ""
        if roles[i] == "Fascist":
            fascist_indices = [j+1 for j, role in enumerate(roles) if role == "Fascist" and j != i]
            #if len(fascist_indices) == 1 and num_players < 7:
            hitler_index = next(j+1 for j, role in enumerate(roles) if role == "Hitler")
            if num_players < 7:           
                text_to_show += (f"Hitler is: Player {hitler_index}")
            else:
                text_to_show +=  (f"Your Fascists are: Players {', '.join(str(index) for index in fascist_indices)} and Hitler is: Player {hitler_index}")
        elif roles[i] == "Hitler":
            fascist_index = next(j+1 for j, role in enumerate(roles) if role == "Fascist")
            if num_players < 7:
                text_to_show +=  (f"Your Fascist is: Player {fascist_index}")
        text_to_show = (f"Your role: {roles[i].upper()}       ") + text_to_show
        seen_roles.add(i)
        print(" ")
        print(text_to_show)
        print(" ")
        input("Press any key to hide your role!!")
        clear_console_lines(5)
        #print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    return roles

def handle_request(request_message):
    #call the function from chatgpt_req.py
    game_sum.append(["user",request_message])
    response = fake_chatgpt_req.send_request(game_sum.read())
    game_sum.append(["assistant",response])
    print("-----")
    for item in game_sum.read(): #this is for testing only, it should actually only be seen by the assistant
        print(item['role'],": ",item['content'])
    print("-----")
    print(game_sum.read()[-1]['content'])
    return(game_sum.read()[-1]['content'])

def input_vote_results(bot_vote, game):
    vote_results = ""
    print('game3', game)
    for voting_player in range(1, game["num_players"]+1):
        if voting_player in game["living_players"]:
            players_vote = ""
            if voting_player == 1:
                if bot_vote.lower().startswith(('y', 'j')) or 'yes' in bot_vote.lower():
                    players_vote = "Y"
                else:
                    players_vote = "N"
            else:
                players_vote = user_input(f"Player {voting_player}: (J)a / (N)ein? ", game)
                if players_vote.lower() in ('j', 'y'):
                    players_vote = "Y"
                else:
                    players_vote = "N"
            vote_results += "p"+str(voting_player) +"-"+ players_vote + " "
    game_sum.append_to_last_user("vote_results: "+vote_results)
    print(game_sum.read())
    passed = vote_results.count("Y") > vote_results.count("N")
    return passed

def input_human_nomination(current_president, game):
    nomination = user_input(f"Player {current_president}: Who do you want to nominate? ", game)
    game_sum.append_to_last_user("p"+current_president+" nominated p"+nomination)
    print(game_sum.read())

def increase_current_president(current_president, num_players):
    current_president += 1
    if current_president > num_players:
        current_president = 1
    return current_president

def check_for_policy_game_completion(fascist_policies, liberal_policies):
    game_is_going = True
    if fascist_policies == 6 or liberal_policies == 5:
        game_is_going = False
        print("game is over")
    return game_is_going

def get_first_numeric_digit(string):
    for char in string:
        if char.isdigit():
            return char
    return "No digit found"

def check_for_special_power(game):
    print("CHEC SPECIAL POWERDS")
    #POLICY PEEK
    if (game["num_players"] in [5,6]) and game["fascist_policies"] == 3:
        if game["current_president"] == 1:
            cards_seen = read_gov_policies.show(3)
            game_sum.append_to_last_user(make_policy_peek_sentence(cards_seen))
        else:
            game_sum.append_to_last_user("As president, p"+game["current_president"]+" peeked at the top 3 Policy tiles.")
    #INVESTIGATION
    elif (game["num_players"] in [7,8] and game["fascist_policies"] == 2) or (game["num_players"] in [9,10] and game["fascist_policies"] in [1,2]):
        if game["current_president"] == 1:
            bot_investigation = handle_request("As president, you get to learn the party of another player. Which player would you like to investigate? Answer only with their number.")
            bot_investigation = get_first_numeric_digit(bot_investigation)
            if bot_investigation == "No digit found":
                bot_investigation = user_input("Enter the number of the player that the bot will investigate.", game)
            print("The bot will investigate player "+bot_investigation)
            investigated_players_input = input("Player"+bot_investigation+", press (F)ascist or (L)iberal, then press enter.")
            if investigated_players_input.beginswith("F") or investigated_players_input.beginswith("f"):
                game_sum.append_to_last_user("p"+ bot_investigation+" is a Fascist")
            else:
                game_sum.append_to_last_user("p"+ bot_investigation+" is a Liberal")
        else:
            human_player_investigation = input("Which player did player "+game["current_president"]+" investigate? Answer only with their number.")
            if human_player_investigation == "1":
                input("Press any key to show the bot's role.")
                if(game["bot_role"] in ["Hitler","Fascist"]):
                    print("The bot is a Fascist!")
                    game_sum.append_to_last_user("As President, p"+ game["current_president"]+" has investigated you and learned that you are a Fascist!")
                else:
                    print("The bot is a Liberal.")
                    game_sum.append_to_last_user("As President, p"+ game["current_president"]+" has investigated you and learned that you are a Liberal.")
            game_sum.append_to_last_user("As President, p"+ game["current_president"]+" has investigated "+human_player_investigation+" and learned their loyalty.")
    #EXECUTION
    elif (game["fascist_policies"] in [4,5]):
        print('in execution')
        if game["current_president"] == 1:
            bot_execution = handle_request("As president, you get to execute one player at the table. Which player would you like to execute? Answer only with their number.")
            bot_execution = get_first_numeric_digit(bot_execution)
            if bot_execution == "No digit found":
                bot_execution = input("Enter the number of the player that the bot will execute.")
            print("The bot will execute player "+bot_execution)
            game["living_players"].remove(int(bot_execution))
        else:
            human_player_execution = input("Which player did player "+game["current_president"]+" execute? Answer only with their number.")
            game["living_players"].remove(int(human_player_execution))
            game_sum.append_to_last_user("As President, p"+ game["current_president"]+" has executed p"+human_player_execution+". p"+human_player_execution+" is no longer in the game.")
    return game["living_players"]

def make_read_policies_question(read_cards, government_partner):
    policies_question = ""
    if len(read_cards) == 2:
        policies_question = "You are Chancellor. Your President, p"+str(government_partner)+", has discarded a Policy tile and privately passed you the remaining two Policy tiles. They are: "
    else:
        policies_question = "You are President. You must privately discard one tile and pass the remaining two to your Chancellor, p"+government_partner+". The three Policy tiles you have to choose from are: "
    for i, policy in enumerate(read_cards):
        if policy == "fascist":
            policies_question += str(i+1)+")Fascist "
        else:
            policies_question += str(i+1)+")Liberal " 
    if len(read_cards) == 2:
         policies_question += ". Which Policy tile would you like to enact? Answer only with the number of the Policy tile that you want to play."
    else:
        policies_question += ". Which Policy tile would you like to discard? Answer only with the number of the Policy tile that you want to discard."
    return policies_question

def make_policy_peek_sentence(read_cards):
    peek_sentence = "As President, you get to secretly look at the top three Policy tiles in the Policy deck. They are: "
    policies = []
    for policy in read_cards:
        if policy == "fascist":
            policies.append("Fascist")
        else:
            policies.append("Liberal")
    peek_sentence += ", ".join(policies)
    peek_sentence += "."
    return peek_sentence

def check_for_bot_chancellor_veto(cards_seen, game):
    ask_for_veto = False
    policies_vetoed = False
    if game["bot_role"] in ["Hitler","Fascist"] and game["liberal_policies"] == 4 and cards_seen.count("liberal") == 2:
        ask_for_veto = True
    elif game["bot_role"] == "Liberal":
        if cards_seen.count("fascist") == 2:
            ask_for_veto = True
    else:
        bot_response = handle_request("Would you like to ask the President, p"+game["current_president"]+" if they would like to veto? answer with a single word, Yes or No.")
        if bot_response.lower().startswith(('y', 'j')) or 'yes' in bot_response.lower():
            ask_for_veto = True
    if ask_for_veto:
        chancellor_response = user_input("President p"+game["current_president"]+", would you like to veto? (J)a / (N)ein? ", game)
        if chancellor_response == "J" or chancellor_response == "j" or chancellor_response == "Y" or chancellor_response == "y":
            policies_vetoed = True
    return policies_vetoed

def determine_if_president_bot_wants_to_veto(cards_seen, game):
    bot_wants_to_veto = False
    if game["bot_role"] in ["Hitler","Fascist"] and game["liberal_policies"] == 4 and cards_seen.count("liberal") == 2:
        bot_wants_to_veto = True
    elif game["bot_role"] == "Liberal":
        if cards_seen.count("fascist") == 2:
            bot_wants_to_veto = True
    else:
        bot_response = handle_request("The Chancellor has asked if you want to veto these Policy tiles, answer with a single word, Yes or No.")
        if bot_response.lower().startswith(('y', 'j')) or 'yes' in bot_response.lower():
            bot_wants_to_veto = True
    return bot_wants_to_veto
        
def tell_bot_fellow_fascists(player_roles, num_players):
    hitler_index = [i for i, x in enumerate(player_roles) if x == "Hitler"]
    fascist_index = [i for i, x in enumerate(player_roles) if x == "Fascist"]
    known_fascists = []
    if num_players in [5,6]:
        if player_roles[0] == "Fascist":
            game_sum.append_to_last_user("Hitler is p"+str(hitler_index[0]))
            known_fascists.append(hitler_index[0])
        elif player_roles[0] == "Hitler":
            game_sum.append_to_last_user("The regular fascist is p"+str(fascist_index[0]))
            known_fascists.append(fascist_index[0])
    elif num_players in [7,8]:
        if player_roles[0] == "Fascist":
            game_sum.append_to_last_user("Hitler is p"+str(hitler_index[0])+" and the other fascist is p"+str(fascist_index[1]))
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
    elif num_players in [9,10]:
        if player_roles[0] == "Fascist":
            game_sum.append_to_last_user("Hitler is p"+str(hitler_index[0])+" and the other fascists are p"+str(fascist_index[1])+" and p"+str(fascist_index[2]))
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
            known_fascists.append(fascist_index[2])
    return(known_fascists)   

def show_game_state(game):
    for key, value in game.items():
        print(key, ":", value)

def user_input(text, game):
    print('game8',game)
    if "Enter the number of players:" in text:
        allowed_answers = ["5","6","7","8","9","10"]
    elif "nominate" in text.lower():
        allowed_answers = list(game["living_players"])
        allowed_answers.remove(game["current_president"])
        if game["previous_president"] != 0:
            if len(game["living_players"]) > 5:
                if game["previous_president"] in allowed_answers:
                    allowed_answers.remove(game["previous_president"])
            print('allowed_answers',allowed_answers)
            if game["previous_chancellor"] in allowed_answers:
                allowed_answers.remove(game["previous_chancellor"])
        allowed_answers = [str(num) for num in allowed_answers]
    elif "execute" in text.lower() or "investigate" in text.lower():
        allowed_answers = list(game["living_players"])
        allowed_answers.remove(game["current_president"])
        allowed_answers = [str(num) for num in allowed_answers]
    elif "(Y)es" in text or "(J)a" in text:
        allowed_answers = ["y", "j", "n"]
    elif "What type of policy" in text:
        allowed_answers = ["f", "l"]
    elif "(L)oad" in text:
        allowed_answers = ["n", "l"]
    else:
        "unkown question"
    #print('game6',game)
    while True:
        #print('game7',game)
        player_input = input(text)
        if player_input.lower() in allowed_answers:
            break
        else:
            clear_console_lines(1)
    return player_input

# def handle_bot_response(text):
#     print(text)
#     bot_speak.say(text)

import threading

def handle_bot_response(text):
    # create a new thread to handle the bot response
    bot_response_thread = threading.Thread(target=bot_response, args=(text,))
    bot_response_thread.start()

def bot_response(text):
    print(text)
    bot_speak.say(text)

def start_new_game(game):
    #game = auto_dict.AutoSaveDict('game_state_backup.json')
    game_sum.append(["system","You are an cunning game theorist about to play the game Secret Hitler."]) 
    game["game_is_going"] = True
    game["num_players"] = int(user_input("Enter the number of players: ",{}))
    game["player_roles"] = distribute_roles(game["num_players"])
    game["known_fascists"] = tell_bot_fellow_fascists(game["player_roles"], game["num_players"])
    game["bot_role"] = game["player_roles"][0]
    game["starting_player"] = random.randint(1, game["num_players"]) 
    game["current_president"] = game["starting_player"]
    game["fascist_policies"] = 0
    game["liberal_policies"] = 0
    game["living_players"] = [i for i in range(1, game["num_players"]+1)]
    game["previous_president"] = 0
    game["previous_chancellor"] = 0
    return game



# # the file path for the backup file


# # function to load the dictionary from the file
# def load_dict_from_file():
#     backup_file_path = 


# # load the dictionary from the file


# def load_previous_game():
#     # #game = auto_dict.AutoSaveDict('game_state_backup.json')
#     # with open('game_state_backup.json', 'r') as file:
#     #     return json.load(file)
#     game = 
#     game_sum.load_from_file()
#     return game



def main():
    game = auto_dict.AutoSaveDict(cwd+'/backups/game_state_backup.json')
    if user_input("Would you like to start a (N)ew game or (L)oad the previous one? ", {}) == "n":
        game = start_new_game(game)
    else:
        game.load_from_file()
        game_sum.load_from_file()

    show_game_state(game)
    while (game["game_is_going"]):
        current_president_str = str(game["current_president"])
        if game["current_president"] == 1: #bot's turn
            bot_nomination_for_chancellor = handle_request("who do you nominate as chancellor? answer with their player number only.")
            handle_bot_response("I nominate player "+bot_nomination_for_chancellor+" as chancellor.")
            #print("bot nominated ", bot_nomination_for_chancellor) #maybe it will mess up the bot_nomination_for_chancellor, there should be a way to ask again or something
            input("Press any key to see how the bot votes.")
            bot_vote = handle_request("How do you vote? Answer with a single word, Yes or No.")
            handle_bot_response("I vote "+bot_vote+" for this government.")
            passed = input_vote_results(bot_vote, game)
            if passed:
                game["previous_president"] = game["current_president"]
                game["previous_chancellor"] = int(bot_nomination_for_chancellor)
                if game["bot_role"] == "Hitler" and game["fascist_policies"] == 3:
                    print("Fascists win due to Hitlerbot being President!") #an ominous sound here would be nice
                cards_seen = read_gov_policies.show(3)
                policies_vetoed = False
                if(game["fascist_policies"] == 5): #veto possibility
                    human_chancellor_veto_offer = user_input("Does p"+current_president_str+" want to offer a veto? (Y)es or (N)o?", game)
                    if (human_chancellor_veto_offer in ["Y","y"]):                        
                        determine_if_president_bot_wants_to_veto(cards_seen, game["bot_role"], bot_nomination_for_chancellor, game["known_fascists"], game["fascist_policies"], game["liberal_policies"])
                    else:
                        print("human chancellor didn't want to veto.")                                
                if not policies_vetoed:
                    bot_president_policy_selection = handle_request(make_read_policies_question(cards_seen, bot_nomination_for_chancellor))
                    handle_bot_response("Discard policy number "+bot_president_policy_selection)
                    
                    chancellor_policy_selection = user_input("What type of policy did p"+bot_nomination_for_chancellor+" select? (F)ascist or (L)iberal?", game)
                    cards_seen.remove(cards_seen[int(bot_president_policy_selection)-1])
                    game_sum.append_to_last_user("You passed p"+bot_nomination_for_chancellor+" the following Policy tiles: "+cards_seen[0]+", "+cards_seen[1]+" and they played a ")
                    if chancellor_policy_selection in ["F","f"]:
                        game_sum.append_to_last_user("fascist policy tile.")
                        game["living_players"] = check_for_special_power(game)
                    else:
                        game_sum.append_to_last_user("liberal policy tile.")
            game["current_president"] = increase_current_president(game["current_president"], game["num_players"])
        else:
            #print('game1', game)
            humans_nomination_for_chancellor = user_input("Player "+current_president_str+", who do you nominate as chancellor? answer with their player number only: ", game)
            #print('game5',game)
            if humans_nomination_for_chancellor == "1":
                game_sum.append_to_last_user("P"+current_president_str+" has nominated you as Chancellor")
            else:
                game_sum.append_to_last_user("P"+current_president_str+" has nominated P"+humans_nomination_for_chancellor+" as Chancellor")
            #print('game4',game)
            input("Press any key to see how the bot votes.")
            bot_vote = handle_request("How do you vote?")
            handle_bot_response("I vote "+bot_vote+" for this government.")
            passed = input_vote_results(bot_vote, game)
            if passed:
                #print('game2', game)
                game["previous_president"] = game["current_president"]
                game["previous_chancellor"] = int(humans_nomination_for_chancellor)
                #RIGHT NOW THE BOT GETS THE ELECTRION RESULTS, BUT IS NOT TOLD WHO THE CHANCELLOR IS - MAYBE WE WANT TO DO THIS TOO
                if game["player_roles"][game["current_president"]-1] == "Hitler" and game["fascist_policies"] == 3:
                    print("Fascists Win due to Player "+current_president_str+" being elected President as Hitler!") #a sound effect would be nice 
                if humans_nomination_for_chancellor == "1":
                    cards_seen = read_gov_policies.show(2)
                policies_vetoed = False
                if(game["fascist_policies"] == 5):
                    if humans_nomination_for_chancellor == "1":
                        policies_vetoed = check_for_bot_chancellor_veto(cards_seen, game)
                    else:
                        human_president_veto_response = user_input("Does p"+humans_nomination_for_chancellor+" want to veto? (Y)es or (N)o?", game)
                        if (human_president_veto_response in ["Y","y"]):
                            policies_vetoed = True
                if not policies_vetoed:
                    if humans_nomination_for_chancellor == "1":
                        bot_chancellor_policy_selection = handle_request(make_read_policies_question(cards_seen, game["current_president"]))
                        handle_bot_response("Play policy number "+bot_chancellor_policy_selection)
                        bots_card = user_input("What type of policy does the bot play? (F)ascist or (L)iberal?", game)
                        if bots_card == "F" or bots_card == "f":
                            bots_card = "fascist"
                        else:
                            bots_card = "liberal"
                        game_sum.append_to_last_user("You played a "+bots_card+" policy.")
                        if bots_card == "fascist":
                            game["fascist_policies"] += 1
                            game["living_players"] = check_for_special_power(game)
                        else:
                            game["liberal_policies"] += 1
                        game["game_is_going"] = check_for_policy_game_completion(game["fascist_policies"], game["current_president"])
                    else:
                        human_chancellor_policy_selection = user_input("What type of policy p"+humans_nomination_for_chancellor+" play? (F)ascist or (L)iberal?", game)
                        if human_chancellor_policy_selection == "F" or human_chancellor_policy_selection == "f":
                            human_chancellor_policy_selection = "Fascist"
                        else:
                            human_chancellor_policy_selection = "Liberal"
                        game_sum.append_to_last_user("p"+humans_nomination_for_chancellor+" plays a "+human_chancellor_policy_selection+" Policy tile.")

#CARRY ON FROM BELOW HERE

                    # bots_card = input("what card does the bot play? (F)ascist or (L)iberal?")
                    # if bots_card == "F" or bots_card == "f":
                    #     bots_card = "fascist"
                    # else:
                    #     bots_card = "liberal"
                    # game_sum.append_to_last_user("You played a "+bots_card+" policy."])
                    # if bots_card == "fascist":
                    #     game["fascist_policies"] += 1
                    #     game["living_players"] = check_for_special_power(game["fascist_policies"], game["current_president"], game["bot_role"], game["living_players"])
                    # else:
                    #     game["liberal_policies"] += 1
                    # game["game_is_going"] = check_for_policy_game_completion(game["fascist_policies"], game["current_president"])
            game["current_president"] = increase_current_president(game["current_president"], game["num_players"])

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
