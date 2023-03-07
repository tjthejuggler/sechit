import random
#import the file 'chatgpt_req.py'
import chatgpt_req
import fake_chatgpt_req
from bot_game_summary import BotGameSummary
import read_gov_policies
import bot_speak
import sys
import game_state_dict
import json
import os
import threading
import time

debugging = False

cwd = os.getcwd()
bot_game_sum = BotGameSummary(debugging)
random_bot_comment = False

def debug_log(text):
    if debugging:
        print("DEBUG: "+text)

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
    for i in range(count):
        sys.stdout.write('\033[F\r')# use '\033[F' to move the cursor up one line, use '\r' to return the cursor to the beginning of the line
        sys.stdout.write(' ' * 150)
    sys.stdout.write('\r')
    sys.stdout.flush()

def show_secret(text_to_show):
        print(" ")
        print(text_to_show)
        print(" ")
        input("Press any key to hide this information!!".upper())
        clear_console_lines(5)    

def distribute_roles(num_players):
    seen_roles = set()
    roles = assign_roles(num_players)
    for i in range(1, num_players):        
        input(f"You are Player "+str(i+1)+": Press any key to reveal your role: ")
        text_to_show = ""
        if roles[i] == "Fascist":
            fascist_indices = [j+1 for j, role in enumerate(roles) if role == "Fascist" and j != i]
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
        show_secret(text_to_show)
    return roles

def ask_bot(request_message):
    #call the function from chatgpt_req.py
    bot_game_sum.append(["user",request_message])
    response = fake_chatgpt_req.send_request(bot_game_sum.read())
    bot_game_sum.append(["assistant",response])
    debug_log("-----")
    for item in bot_game_sum.read(): #this is for testing only, it should actually only be seen by the assistant
        debug_log(item['role'] + ": "+item['content'])
    debug_log("-----")
    #print(bot_game_sum.read()[-1]['content'])
    return(bot_game_sum.read()[-1]['content'])

def input_vote_results(bot_vote, game):
    vote_results = ""
    #debug_log('game3 '+ game)
    for voting_player in range(1, game["num_players"]+1):
        if voting_player in game["living_players"]:
            players_vote = ""
            if voting_player == 1:
                if bot_vote.lower().startswith(('y', 'j')) or 'yes' in bot_vote.lower():
                    players_vote = "Y"
                else:
                    players_vote = "N"
            else:
                players_vote = handle_user_response(f"Player {voting_player}: (J)a / (N)ein? ", game)
                if players_vote.lower() in ('j', 'y'):
                    players_vote = "Y"
                else:
                    players_vote = "N"
            vote_results += "p"+str(voting_player) +"-"+ players_vote + " "
    bot_game_sum.append_to_last_user("vote_results: "+vote_results)
    debug_log(json.dumps(bot_game_sum.read()))
    passed = vote_results.count("Y") > vote_results.count("N")
    return passed

def input_human_nomination(current_president, game):
    nomination = handle_user_response(f"Player {current_president}: Who do you want to nominate? ", game)
    bot_game_sum.append_to_last_user("p"+current_president+" nominated p"+nomination)
    debug_log(json.dumps(bot_game_sum.read()))

def increase_current_president(current_president, num_players):
    current_president += 1
    if current_president > num_players:
        current_president = 1
    return current_president

def check_for_policy_game_completion(game):
    game_is_going = True
    if game["fascist_policies"] == 6:
        game_is_going = False
        debug_log("game is over")
        if game["player_roles"][0] in ["Hitler","Fascist"]:
            make_bot_response("We won, Fascists!")
        else:
            make_bot_response("We lost, Liberals!")
    elif game["liberal_policies"] == 5:
        if game["player_roles"][0] in ["Hitler","Fascist"]:
            make_bot_response("We lost, Fascists!")
        else:
            make_bot_response("We won, Libers!")
    return game_is_going

def get_first_numeric_digit(string):
    for char in string:
        if char.isdigit():
            return char
    return "No digit found"

def check_for_special_power(game):
    debug_log("CHECK SPECIAL POWERS")
    #POLICY PEEK
    if (game["num_players"] in [5,6]) and game["fascist_policies"] == 3:
        if game["current_president"] == 1:
            cards_seen = read_gov_policies.show(3, debugging)
            bot_game_sum.append_to_last_user(make_policy_peek_sentence(cards_seen))
        else:
            bot_game_sum.append_to_last_user("As president, p"+str(game["current_president"])+" peeked at the top 3 Policy tiles.")
    #INVESTIGATION
    elif (game["num_players"] in [7,8] and game["fascist_policies"] == 2) or (game["num_players"] in [9,10] and game["fascist_policies"] in [1,2]):
        if game["current_president"] == 1:
            bot_investigation = ask_bot("As president, you get to learn the party of another player. Which player would you like to investigate? Answer only with their number.")
            bot_investigation = get_first_numeric_digit(bot_investigation)
            if bot_investigation == "No digit found":
                bot_investigation = handle_user_response("Enter the number of the player that the bot will investigate.", game)
            make_bot_response("I will investigate player "+bot_investigation)
            investigated_players_input = input("Player"+bot_investigation+", press (F)ascist or (L)iberal, then press enter.")
            if investigated_players_input.beginswith("F") or investigated_players_input.beginswith("f"):
                bot_game_sum.append_to_last_user("p"+ bot_investigation+" is a Fascist")
            else:
                bot_game_sum.append_to_last_user("p"+ bot_investigation+" is a Liberal")
        else:
            human_player_investigation = input("Which player did player "+str(game["current_president"])+" investigate? Answer only with their number.")
            if human_player_investigation == "1":
                input("Press any key to show the bot's role.")
                if(game["player_roles"][0] in ["Hitler","Fascist"]):
                    show_secret("I am a Fascist!")
                    bot_game_sum.append_to_last_user("As President, p"+ str(game["current_president"])+" has investigated you and learned that you are a Fascist!")
                else:
                    show_secret("I am a Liberal.")                    
                    bot_game_sum.append_to_last_user("As President, p"+ str(game["current_president"])+" has investigated you and learned that you are a Liberal.")
            bot_game_sum.append_to_last_user("As President, p"+ str(game["current_president"])+" has investigated "+human_player_investigation+" and learned their loyalty.")
    #EXECUTION
    elif (game["fascist_policies"] in [4,5]):
        print('in execution')
        if game["current_president"] == 1:
            bot_execution = ask_bot("As president, you get to execute one player at the table. Which player would you like to execute? Answer only with their number.")
            bot_execution = get_first_numeric_digit(bot_execution)
            if bot_execution == "No digit found":
                bot_execution = input("Enter the number of the player that the bot will execute.")
            make_bot_response("I formally execute Player "+bot_execution)
            game["living_players"].remove(int(bot_execution))
        else:
            human_player_execution = input("Which player did player "+str(game["current_president"])+" execute? Answer only with their number.")
            game["living_players"].remove(int(human_player_execution))
            bot_game_sum.append_to_last_user("As President, p"+ str(game["current_president"])+" has executed p"+human_player_execution+". p"+human_player_execution+" is no longer in the game.")
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
    if game["player_roles"][0] in ["Hitler","Fascist"] and game["liberal_policies"] == 4 and cards_seen.count("liberal") == 2:
        ask_for_veto = True
    elif game["player_roles"][0] == "Liberal":
        if cards_seen.count("fascist") == 2:
            ask_for_veto = True
    else:
        bot_response = ask_bot("Would you like to ask the President, p"+game["current_president"]+" if they would like to veto? answer with a single word, Yes or No.")
        if bot_response.lower().startswith(('y', 'j')) or 'yes' in bot_response.lower():
            ask_for_veto = True
    if ask_for_veto:
        chancellor_response = handle_user_response("President p"+game["current_president"]+", would you like to veto? (J)a / (N)ein? ", game)
        if chancellor_response == "J" or chancellor_response == "j" or chancellor_response == "Y" or chancellor_response == "y":
            policies_vetoed = True
    return policies_vetoed

def determine_if_president_bot_wants_to_veto(cards_seen, game):
    bot_wants_to_veto = False
    if game["player_roles"][0] in ["Hitler","Fascist"] and game["liberal_policies"] == 4 and cards_seen.count("liberal") == 2:
        bot_wants_to_veto = True
    elif game["player_roles"][0] == "Liberal":
        if cards_seen.count("fascist") == 2:
            bot_wants_to_veto = True
    else:
        bot_response = ask_bot("The Chancellor has asked if you want to veto these Policy tiles, answer with a single word, Yes or No.")
        if bot_response.lower().startswith(('y', 'j')) or 'yes' in bot_response.lower():
            bot_wants_to_veto = True
    return bot_wants_to_veto
        
def tell_bot_fellow_fascists(player_roles, num_players):
    hitler_index = [i for i, x in enumerate(player_roles) if x == "Hitler"]
    fascist_index = [i for i, x in enumerate(player_roles) if x == "Fascist"]
    known_fascists = []
    if num_players in [5,6]:
        if player_roles[0] == "Fascist":
            bot_game_sum.append_to_last_user("Hitler is p"+str(hitler_index[0]))
            known_fascists.append(hitler_index[0])
        elif player_roles[0] == "Hitler":
            bot_game_sum.append_to_last_user("The regular fascist is p"+str(fascist_index[0]))
            known_fascists.append(fascist_index[0])
    elif num_players in [7,8]:
        if player_roles[0] == "Fascist":
            bot_game_sum.append_to_last_user("Hitler is p"+str(hitler_index[0])+" and the other fascist is p"+str(fascist_index[1]))
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
    elif num_players in [9,10]:
        if player_roles[0] == "Fascist":
            bot_game_sum.append_to_last_user("Hitler is p"+str(hitler_index[0])+" and the other fascists are p"+str(fascist_index[1])+" and p"+str(fascist_index[2]))
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
            known_fascists.append(fascist_index[2])
    return(known_fascists)   

# def show_game_state(game):
#     for key, value in game.items():
#         debug_log(key, ":", value)

def conversation_mode(game, initiation):
    #clear_console_lines(1)

    possible_player_numbers = [2,3,4,5,6,7,8,9,10]
    if "living_players" in game:
        possible_player_numbers = list(game["living_players"])
        possible_player_numbers.remove(1)
    while True:        
        #debug_log('game7 '+game)
        if initiation == "bot":
            bot_comment = ask_bot("What would you like to say?")
            make_bot_response(bot_comment)
            input("Press Enter to continue...")
            clear_console_lines(2)
            initiation = "human"
        else:
            conversation_input = input("CONVERSATION MODE(enter to switch): Enter your player number, followed by your comment: ")
            player_number = conversation_input.split()[0] if len(conversation_input.split()) > 1 else ""
            # print("player number: "+player_number)
            # print("living players: "+str(possible_player_numbers))
            if conversation_input == "":
                clear_console_lines(1)
                break
            elif player_number.isdigit() and int(player_number) in possible_player_numbers:
                #print("living players: "+str(game["living_players"]))
                bot_response = ask_bot("p"+player_number+" says: "+conversation_input.split(None, 1)[1])
                make_bot_response(bot_response)
                input("Press Enter to continue...")
                clear_console_lines(3)
            else:
                clear_console_lines(1)


def check_if_bot_want_to_talk(game):
    bot_wants_to_talk = False
    if "player_roles" in game:
        bot_wants_to_talk_response = ask_bot("Is there anything you would like to say or ask? answer with a single word, Yes or No.")
        if bot_wants_to_talk_response.lower().startswith(('y', 'j')) or 'yes' in bot_wants_to_talk_response.lower():    
            bot_wants_to_talk = True
    return bot_wants_to_talk


def handle_user_response(text, game):
    if "Enter the number of players:" in text:
        allowed_answers = ["5","6","7","8","9","10"]
    elif "Enter the starting player: " in text:
        allowed_answers = [str(i) for i in range(1, int(game["num_players"])+1)]
    elif "nominate" in text.lower():
        allowed_answers = list(game["living_players"])
        allowed_answers.remove(game["current_president"])
        if game["previous_president"] != 0:
            if len(game["living_players"]) > 5:
                if game["previous_president"] in allowed_answers:
                    allowed_answers.remove(game["previous_president"])
            debug_log('allowed_answers '+str(allowed_answers))
            if game["previous_chancellor"] in allowed_answers:
                allowed_answers.remove(game["previous_chancellor"])
        allowed_answers = [str(num) for num in allowed_answers]
    elif "Enact the top policy, what is it? " in text:
        allowed_answers = ["f", "l"]
    elif "execute" in text.lower() or "investigate" in text.lower():
        allowed_answers = list(game["living_players"])
        allowed_answers.remove(game["current_president"])
        allowed_answers = [str(num) for num in allowed_answers]
    elif "(Y)es" in text or "(J)a" in text:
        allowed_answers = ["y", "j", "n"]
    elif "Which type of policy" in text:
        allowed_answers = ["f", "l"]
    elif "(L)oad" in text:
        allowed_answers = ["n", "l"]
    else:
        "unkown question"
    bot_wants_to_talk = False
    if "vote?" not in text:
        bot_wants_to_talk = check_if_bot_want_to_talk(game)
    while True:
        player_input = ""
        if not bot_wants_to_talk:
            player_input = input("GAME MODE(enter to switch): "+text)
        if bot_wants_to_talk:
            bot_wants_to_talk = False
            conversation_mode(game, "bot")   
        elif player_input == '':
            clear_console_lines(1)
            conversation_mode(game, "human")                         
        elif player_input.lower() in allowed_answers:
            break
        else:
            clear_console_lines(1)
    clear_console_lines(1)
    return player_input

def make_bot_response(text):
    # create a new thread to handle the bot response
    print('Bot: '+text)
    bot_response_thread = threading.Thread(target=bot_response, args=(text,))
    bot_response_thread.start()

def bot_response(text):
    bot_speak.say(text)

def start_new_game(game):
    #game = auto_dict.AutoSaveDict('game_state_backup.json')
    #bot_game_sum.append(["system","You are an cunning game theorist about to play the game Secret Hitler."]) 
    game["game_is_going"] = True
    game["num_players"] = int(handle_user_response("Enter the number of players: ",{}))
    game["current_president"] = int(handle_user_response("Enter the starting player: ",game))
    game["player_roles"] = distribute_roles(game["num_players"]) 
    if game["player_roles"][0] == "Liberal":
        bot_game_sum.append(["system",'You are an cunning game theorist about to play the game Secret Hitler. You have been randomly assigned the role of "Liberal" this game. Your goal is to get 5 liberal policy tiles passed. You should try to figure out who the Fascists are and convince the other players to vote against them. You should also try to convince the other players to vote for you.'])
    elif game["player_roles"][0] == "Fascist":
        bot_game_sum.append(["system",'You are an cunning game theorist about to play the game Secret Hitler. You have been randomly assigned the role of "Fascist" this game. Your goal is to get 6 fascist policy tiles passed or to get Hitler elected as Chancellor after 3 policies have been played. You should never let anyone know that you are a Fascist, if anyone asks, lie and say that you are a liberal. You should also try to convince the other players to vote for you.'])
    elif game["player_roles"][0] == "Hitler":
        bot_game_sum.append(["system",'You are an cunning game theorist about to play the game Secret Hitler. You have been randomly assigned the role of "Hitler" this game. Your goal is to get 6 fascist policy tiles passed or to get elected as Chancellor after 3 policies have been played. You should never let anyone know that you are a Hitler. If anyone asks, lie and say that you are a liberal. You should also try to convince the other players to vote for you.'])
    game["known_fascists"] = tell_bot_fellow_fascists(game["player_roles"], game["num_players"])   
    game["fascist_policies"] = 0
    game["liberal_policies"] = 0
    game["living_players"] = [i for i in range(1, game["num_players"]+1)]
    game["previous_president"] = 0
    game["previous_chancellor"] = 0
    game["failed_elections"] = 0
    return game

def election_passed(game, current_chancellor):
    game["failed_elections"] = 0
    game["previous_president"] = game["current_president"]
    game["previous_chancellor"] = int(current_chancellor)
    return game

def enact_top_policy(game):
    enacted_top_policy = handle_user_response("Enact the top policy, was it (F)ascist or (L)iberal? ", game)
    bot_game_sum.append_to_last_user("Three consecutive governments failed, so the policy was enacted and it was a ")
    debug_log('enacted_top_policy '+enacted_top_policy)
    if enacted_top_policy == "f":
        game["fascist_policies"] += 1
        bot_game_sum.append_to_last_user("fascist policy tile.")
    else:
        game["liberal_policies"] += 1
        bot_game_sum.append_to_last_user("liberal policy tile.")
    return game

def get_eligible_chancellors(game):
    eligible_chancellors = [i for i in game["living_players"] if i != game["current_president"] and i != game["previous_chancellor"]]
    eligible_chancellors.remove(game["previous_president"]) if len(game["living_players"]) > 5 else None
    eligible_chancellors = ", ".join([f"p{number}" for number in [1, 3, 4, 5, 6, 7]])
    return eligible_chancellors

def handle_voting(game):
    bot_vote = ""
    while True:
        human_ready = handle_user_response("Are you ready to see how the bot votes? (Y)es ", game)
        if human_ready == "y":
            bot_vote = ask_bot("How do you vote? Answer with a single word, Yes or No.")
            make_bot_response("I vote "+bot_vote+" for this government.")            
            break
    return bot_vote

def handle_bot_nomination(game):
    bot_nomination_for_chancellor = ""
    while True:
        human_ready = handle_user_response("Are you ready to ask who the bot will nominate? (Y)es ", game)
        if human_ready == "y":
            eligible_chancellors = get_eligible_chancellors(game)
            bot_nomination_for_chancellor = ask_bot("You must nominate a chancelor. Your choices are "+eligible_chancellors+". Which player do you choose? Answer with their player number only.")                
            break
    make_bot_response("I nominate player "+bot_nomination_for_chancellor+" as chancellor.")
    return bot_nomination_for_chancellor

def main():
    clear_console_lines(2)
    game = game_state_dict.AutoSaveDict(cwd+'/backups/game_state_backup.json', debugging)
    print("\n")
    if handle_user_response("Would you like to start a (N)ew game or (L)oad the previous one? ", {}) == "n":
        game = start_new_game(game)
    else:
        game.load_from_file()
        bot_game_sum.load_from_file()
    while (game["game_is_going"]):
        if game["failed_elections"] == 3:
            game = enact_top_policy(game)
        if game["current_president"] == 1:
            bot_nomination_for_chancellor = handle_bot_nomination(game)
            bot_vote = handle_voting(game)
            passed = input_vote_results(bot_vote, game)
            if passed:
                game = election_passed(game, bot_nomination_for_chancellor)
                if game["player_roles"][0] == "Hitler" and game["fascist_policies"] == 3:
                    make_bot_response("We win! I'm Hitler, fools.")
                make_bot_response("Please show me 3 cards.")
                cards_seen = read_gov_policies.show(3, debugging)
                policies_vetoed = False
                if(game["fascist_policies"] == 5): #veto possibility
                    human_chancellor_veto_offer = handle_user_response("Does p"+str(game["current_president"])+" want to offer a veto? (Y)es or (N)o?", game)
                    if (human_chancellor_veto_offer in ["Y","y"]):                        
                        determine_if_president_bot_wants_to_veto(cards_seen, game["player_roles"][0], bot_nomination_for_chancellor, game["known_fascists"], game["fascist_policies"], game["liberal_policies"])
                    else:
                        print("human chancellor didn't want to veto.")                                
                if not policies_vetoed:
                    bot_president_policy_selection = ask_bot(make_read_policies_question(cards_seen, bot_nomination_for_chancellor))
                    make_bot_response("Discard policy number "+bot_president_policy_selection)                    
                    chancellor_policy_selection = handle_user_response("Which type of policy did Player "+bot_nomination_for_chancellor+" select? (F)ascist or (L)iberal?", game)
                    cards_seen.remove(cards_seen[int(bot_president_policy_selection)-1])
                    bot_game_sum.append_to_last_user("You passed p"+bot_nomination_for_chancellor+" the following Policy tiles: "+cards_seen[0]+", "+cards_seen[1]+" and they played a ")
                    if chancellor_policy_selection in ["F","f"]:
                        bot_game_sum.append_to_last_user("fascist policy tile.")
                        game["fascist_policies"] += 1
                        game["living_players"] = check_for_special_power(game)
                    else:
                        bot_game_sum.append_to_last_user("liberal policy tile.")
                        game["liberal_policies"] += 1
                    game["game_is_going"] = check_for_policy_game_completion(game)
            else:
                game["failed_elections"] += 1
            game["current_president"] = increase_current_president(game["current_president"], game["num_players"])
        else:
            #debug_log('game1 '+ game)
            humans_nomination_for_chancellor = handle_user_response("Player "+str(game["current_president"])+", who do you nominate as chancellor? answer with their player number only: ", game)
            #debug_log('game5 '+game)
            if humans_nomination_for_chancellor == "1":
                bot_game_sum.append_to_last_user("P"+str(game["current_president"])+" has nominated you as Chancellor")
            else:
                bot_game_sum.append_to_last_user("P"+str(game["current_president"])+" has nominated P"+humans_nomination_for_chancellor+" as Chancellor")
            #debug_log('game4 '+game)
            bot_vote = handle_voting(game)
            # input("Press any key to see how the bot votes.")
            # bot_vote = ask_bot("How do you vote?")
            # make_bot_response("I vote "+bot_vote+" for this government.")
            passed = input_vote_results(bot_vote, game)
            if passed:
                #debug_log('game2 '+ game)
                game = election_passed(game, humans_nomination_for_chancellor)
                #RIGHT NOW THE BOT GETS THE ELECTRION RESULTS, BUT IS NOT TOLD WHO THE CHANCELLOR IS - MAYBE WE WANT TO DO THIS TOO
                if game["player_roles"][game["current_president"]-1] == "Hitler" and game["fascist_policies"] == 3:
                    make_bot_response("We win! Player "+str(game["current_president"])+" is Hitler.")
                if humans_nomination_for_chancellor == "1":
                    cards_seen = read_gov_policies.show(2, debugging)
                policies_vetoed = False
                if(game["fascist_policies"] == 5):
                    if humans_nomination_for_chancellor == "1":
                        policies_vetoed = check_for_bot_chancellor_veto(cards_seen, game)
                    else:
                        human_president_veto_response = handle_user_response("Does p"+humans_nomination_for_chancellor+" want to veto? (Y)es or (N)o?", game)
                        if (human_president_veto_response in ["Y","y"]):
                            policies_vetoed = True
                if not policies_vetoed:
                    if humans_nomination_for_chancellor == "1":
                        bot_chancellor_policy_selection = ask_bot(make_read_policies_question(cards_seen, game["current_president"]))
                        bots_card =  cards_seen[int(bot_chancellor_policy_selection)-1]
                        make_bot_response("Play policy number "+bot_chancellor_policy_selection+". It is a " + bots_card + " policy.")
                        bot_game_sum.append_to_last_user("You played a "+bots_card+" policy.")
                        if bots_card == "fascist":
                            game["fascist_policies"] += 1
                            game["living_players"] = check_for_special_power(game)
                        else:
                            game["liberal_policies"] += 1
                        game["game_is_going"] = check_for_policy_game_completion(game)
                    else:
                        human_chancellor_policy_selection = handle_user_response("Which type of policy did Player "+humans_nomination_for_chancellor+" play? (F)ascist or (L)iberal?", game)
                        if human_chancellor_policy_selection == "F" or human_chancellor_policy_selection == "f":
                            human_chancellor_policy_selection = "Fascist"
                            game["fascist_policies"] += 1
                            game["living_players"] = check_for_special_power(game)
                        else:
                            human_chancellor_policy_selection = "Liberal"
                            game["liberal_policies"] += 1
                        bot_game_sum.append_to_last_user("p"+humans_nomination_for_chancellor+" plays a "+human_chancellor_policy_selection+" Policy tile.")
            else:
                game["failed_elections"] += 1
            game["current_president"] = increase_current_president(game["current_president"], game["num_players"])
#CARRY ON FROM BELOW HERE

                    # bots_card = input("what card does the bot play? (F)ascist or (L)iberal?")
                    # if bots_card == "F" or bots_card == "f":
                    #     bots_card = "fascist"
                    # else:
                    #     bots_card = "liberal"
                    # bot_game_sum.append_to_last_user("You played a "+bots_card+" policy."])
                    # if bots_card == "fascist":
                    #     game["fascist_policies"] += 1
                    #     game["living_players"] = check_for_special_power(game["fascist_policies"], game["current_president"], game["player_roles"][0], game["living_players"])
                    # else:
                    #     game["liberal_policies"] += 1
                    # game["game_is_going"] = check_for_policy_game_completion(game["fascist_policies"], game["current_president"])
            

    #while (game_is_going):
        event_thread.join()
main()

# create an instance of the TextVariable class
# bot_game_sum.append(["system","you are a five year old boy who loves insects a fascisticulous amount"])
# ask_bot("what is your favorite thing to do on the weekend?")

# read the current value of the text attribute
# print(bot_game_sum.read())   # output: "Hello, world!"

# # append a new string to the text attribute
# bot_game_sum.append(["user"," How are you?"])
# print(bot_game_sum.read())   # output: "Hello, world! How are you?"

# print(chatgpt_req.send_request([
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": "Who won the world series in 2000?"},
#         ]))
