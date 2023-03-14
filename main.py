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
from datetime import datetime
from bot_conversation_box import BotTalkBox
import tkinter as tk
import glob

debugging = False

cwd = os.getcwd()
bot_game_sum = []
for i in range(10):
    indiv_sum = BotGameSummary(debugging, i)
    bot_game_sum.append(indiv_sum)
game = game_state_dict.AutoSaveDict(cwd+'/backups/game_state_backup.json', debugging)
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

def distribute_roles(num_bot_players, num_players):
    seen_roles = set()
    roles = assign_roles(num_players)
    for i in range(num_bot_players, num_players):        
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

def ask_bot(bot_num, request_message):
    bot_num = int(bot_num)
    #call the function from chatgpt_req.py
    bot_game_sum[bot_num].append(["user",request_message])
    response = fake_chatgpt_req.send_request(bot_game_sum[bot_num].read())
    bot_game_sum[bot_num].append(["assistant",response])
    debug_log("-----")
    for item in bot_game_sum[bot_num].read(): #this is for testing only, it should actually only be seen by the assistant
        debug_log(item['role'] + ": "+item['content'])
    debug_log("-----")
    #print(bot_game_sum[bot_num].read()[-1]['content'])
    bot_conversation_box.bot_talks(response)
    return(bot_game_sum[bot_num].read()[-1]['content'])

def append_all_bot_summaries(game, text):
    for bot in range(game["num_bot_players"]):
        bot_game_sum[bot].append_to_last_user(text)

def append_all_bot_summaries_except_president(game, text):
    for bot in range(game["num_bot_players"]):
        if bot != game["current_president"]:
            bot_game_sum[bot].append_to_last_user(text)

def input_vote_results(bot_votes, game): #BOT VOTES SHOULD BE CHANGED TO A LIST AND DEALT WITH ACCORDINGLY
    vote_results = ""
    #debug_log('game3 '+ game)
    for voting_player in range(game["num_bot_players"]+1, game["num_players"]+1):
        if voting_player in game["living_players"]:
            players_vote = ""
            if voting_player < game["num_bot_players"]:
                bot_vote = bot_votes[voting_player-1]
                if bot_vote.lower().startswith(('y', 'j')) or 'yes' in bot_vote.lower():
                    players_vote = "Y"
                else:
                    players_vote = "N"
            else:
                players_vote = handle_user_response(f"Player {voting_player}: (J)a / (N)ein? ", game, "yes_or_no_vote")
                if players_vote.lower() in ('j', 'y'):
                    players_vote = "Y"
                else:
                    players_vote = "N"
            vote_results += "p"+str(voting_player) +"-"+ players_vote + " "
    append_all_bot_summaries(game, "vote_results: "+vote_results)
    #debug_log(json.dumps(bot_game_sum.read()))
    passed = vote_results.count("Y") > vote_results.count("N")
    return passed

# def input_human_nomination(current_president, game):
#     nomination = handle_user_response(f"Player {current_president}: Who do you want to nominate? ", game, "nominate_player")
#     bot_game_sum.append_to_last_user("p"+current_president+" nominated p"+nomination)
#     debug_log(json.dumps(bot_game_sum.read()))

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
        if game["player_roles"][int(game["current_president"])-1] in ["Hitler","Fascist"]:
            make_bot_response("We won, Fascists!", game["current_president"])
        else:
            make_bot_response("We lost, Liberals!", game["current_president"])
    elif game["liberal_policies"] == 5:
        if game["player_roles"][int(game["current_president"])-1] in ["Hitler","Fascist"]:
            make_bot_response("We lost, Fascists!", game["current_president"])
        else:
            make_bot_response("We won, Libers!", game["current_president"])
    return game_is_going

def get_first_numeric_digit(string):
    for char in string:
        if char.isdigit():
            return char
    return "No digit found"

def handle_bot_investigation(game):
    bot_investigation = ""
    while True:
        human_ready = handle_user_response("Are you ready to ask who the bot will investigate? (Y)es ", game, "continue")
        if human_ready == "y":
            choices = special_power_choices(game)
            bot_investigation = ask_bot(int(game["current_president"])-1,"As president, you get to learn the party of another player. Which player would you like to investigate? Your choices are: "+choices+". Answer only with their number: ")
            bot_investigation = get_first_numeric_digit(bot_investigation)
            if bot_investigation == "No digit found":
                bot_investigation = handle_user_response("Enter the number of the player that the bot will investigate.", game, "special_power")
            make_bot_response("I have investigated player "+bot_investigation, int(game["current_president"])-1)
            ready_to_continue = handle_user_response("Are you ready to continue? (Y)es: ", game, "continue")
            if ready_to_continue:
                investigation_result = game["player_roles"][int(bot_investigation)-1]
                if investigation_result.lower() in ["hitler", "fascist"]:
                    bot_game_sum[int(game["current_president"])-1].append_to_last_user("p"+ bot_investigation+" is a Fascist")
                else:
                    bot_game_sum[int(game["current_president"])-1].append_to_last_user("p"+ bot_investigation+" is a Liberal")
                append_all_bot_summaries(game,"As President, p"+str(game["current_president"])+" investigated p"+bot_investigation)
            break

def handle_bot_execution(game):
    bot_execution = ""
    while True:
        human_ready = handle_user_response("Are you ready to ask who the bot will execute? (Y)es ", game, "continue")
        if human_ready == "y":
            choices = special_power_choices(game)
            bot_execution = ask_bot(int(game["current_president"])-1,"As president, you must execute one player at the table. Which player would you like to execute? Your choices are: "+choices+". Answer only with their number: ")
            bot_execution = get_first_numeric_digit(bot_execution)
            if bot_execution == "No digit found":
                bot_execution = input("Enter the number of the player that the bot will execute.", game, "special_power")
            make_bot_response("I formally execute Player "+bot_execution, int(game["current_president"])-1)
            game["living_players"].remove(int(bot_execution))
            append_all_bot_summaries(game,"As President, p"+str(game["current_president"])+" executed p"+bot_execution)
            break
    return game

def handle_special_election(game):
    bot_special_election = ""
    while True:
        human_ready = handle_user_response("Are you ready to ask who the bot will make president? (Y)es ", game, "continue")
        if human_ready == "y":
            choices = special_power_choices(game)
            bot_special_election = ask_bot(int(game["current_president"])-1,"As president, you get to choose the next President-elect. Which player would you like to choose? Your choices are: "+choices+". Answer only with their number: ")
            bot_special_election = get_first_numeric_digit(bot_special_election)
            if bot_special_election == "No digit found":
                bot_special_election = input("Enter the number of the player that the bot will choose as President-elect.", game, "special_power")
            make_bot_response("I will make player "+bot_special_election+"be President.", int(game["current_president"])-1)
            game["special_election_helper"] = -bot_special_election
            append_all_bot_summaries(game,"As President, p"+str(game["current_president"])+" gave the special election to p"+bot_special_election)
            break
    return game

def special_power_choices(game):
    special_power_choices = [i for i in game["living_players"] if i != game["current_president"]]
    special_power_choices_str = ", ".join([f"p{number}" for number in special_power_choices])
    return special_power_choices_str

def check_for_special_power(game):
    debug_log("CHECK SPECIAL POWERS")
    #POLICY PEEK
    if (game["num_players"] in [5,6]) and game["fascist_policies"] == 3:
        if game["current_president"] <= int(game["num_bot_players"]):
            cards_seen = read_gov_policies.show(3, debugging)
            bot_game_sum[int(game["current_president"])-1].append_to_last_user(make_policy_peek_sentence(cards_seen))
        else:
            append_all_bot_summaries_except_president(game,"As president, p"+str(game["current_president"])+" peeked at the top 3 Policy tiles.")
    #SPECIAL ELECTION
    elif (game["num_players"] > 6) and game["fascist_policies"] == 3:
        if game["current_president"] <= int(game["num_bot_players"]):
            handle_special_election(game)
        else:
            human_player_special_election = handle_user_response("Which player did player "+str(game["current_president"])+" give the presidency to? Answer only with their number.", game,"special_power")
            game["special_election_helper"] = -int(human_player_special_election)
            append_all_bot_summaries(game,"As President, p"+ str(game["current_president"])+" has used the special election power and made player "+human_player_special_election+" be President-elect.")
    #INVESTIGATION
    elif (game["num_players"] in [7,8] and game["fascist_policies"] == 2) or (game["num_players"] in [9,10] and game["fascist_policies"] in [1,2]):
        if game["current_president"] <= int(game["num_bot_players"]):
            handle_bot_investigation(game)
        else:
            human_player_investigation = handle_user_response("Which player did player "+str(game["current_president"])+" investigate? Answer only with their number.", game, "special_power")
            if int(human_player_investigation) <= int(game["num_bot_players"]):
                input("Press any key to show the bot's role.")
                if(game["player_roles"][int(human_player_investigation)-1] in ["Hitler","Fascist"]):
                    show_secret("I am a Fascist!")
                    bot_game_sum[int(human_player_investigation)-1].append_to_last_user("As President, p"+ str(game["current_president"])+" has investigated you and learned that you are a Fascist!")
                else:
                    show_secret("I am a Liberal.")                    
                    bot_game_sum[int(human_player_investigation)-1].append_to_last_user("As President, p"+ str(game["current_president"])+" has investigated you and learned that you are a Liberal.")
            append_all_bot_summaries_except_president(game,"As President, p"+ str(game["current_president"])+" has investigated "+human_player_investigation+" and learned their loyalty.")
    #EXECUTION
    elif (game["fascist_policies"] in [4,5]):
        if debugging: print('in execution')
        if game["current_president"] <= int(game["num_bot_players"]):
            game = handle_bot_execution(game)
        else:
            human_player_execution = handle_user_response("Which player did player "+str(game["current_president"])+" execute? Answer only with their number.", game, "special_power")
            game["living_players"].remove(int(human_player_execution))
            append_all_bot_summaries_except_president(game,"As President, p"+ str(game["current_president"])+" has executed p"+human_player_execution+". p"+human_player_execution+" is no longer in the game.")
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

def check_for_bot_chancellor_veto(chancellor, cards_seen, game):
    ask_for_veto = False
    policies_vetoed = False
    if game["player_roles"][int(chancellor)-1] in ["Hitler","Fascist"] and game["liberal_policies"] == 4 and cards_seen.count("liberal") == 2:
        ask_for_veto = True
    elif game["player_roles"][int(chancellor)-1] == "Liberal":
        if cards_seen.count("fascist") == 2:
            ask_for_veto = True
    else:
        bot_response = ask_bot(int(chancellor)-1, "Would you like to ask the President, p"+str(game["current_president"])+" if they would like to veto? answer with a single word, Yes or No.")
        if bot_response.lower().startswith(('y', 'j')) or 'yes' in bot_response.lower():
            ask_for_veto = True
    if ask_for_veto:
        chancellor_response = handle_user_response("President p"+str(game["current_president"])+", would you like to veto? (J)a / (N)ein? ", game)
        if chancellor_response == "J" or chancellor_response == "j" or chancellor_response == "Y" or chancellor_response == "y":
            policies_vetoed = True
    return policies_vetoed

def determine_if_president_bot_wants_to_veto(cards_seen, game):
    bot_wants_to_veto = False
    if game["player_roles"][int(game["current_president"])-1] in ["Hitler","Fascist"] and game["liberal_policies"] == 4 and cards_seen.count("liberal") == 2:
        bot_wants_to_veto = True
    elif game["player_roles"][int(game["current_president"])-1] == "Liberal":
        if cards_seen.count("fascist") == 2:
            bot_wants_to_veto = True
    else:
        bot_response = ask_bot(int(game["current_president"])-1, "The Chancellor has asked if you want to veto these Policy tiles, answer with a single word, Yes or No.")
        if bot_response.lower().startswith(('y', 'j')) or 'yes' in bot_response.lower():
            bot_wants_to_veto = True
    return bot_wants_to_veto
        
def tell_bot_fellow_fascists(bot, player_roles, num_players):
    hitler_index = [i for i, x in enumerate(player_roles) if x == "Hitler"]
    fascist_index = [i for i, x in enumerate(player_roles) if x == "Fascist"]
    known_fascists = []
    if num_players in [5,6]:
        if player_roles[bot] == "Fascist":
            bot_game_sum[bot].append_to_last_user("Hitler is p"+str(hitler_index[0]))
            known_fascists.append(hitler_index[0])
        elif player_roles[bot] == "Hitler":
            bot_game_sum[bot].append_to_last_user("The regular fascist is p"+str(fascist_index[0]))
            known_fascists.append(fascist_index[0])
    elif num_players in [7,8]:
        if player_roles[bot] == "Fascist":
            bot_game_sum[bot].append_to_last_user("Hitler is p"+str(hitler_index[0])+" and the other fascist is p"+str(fascist_index[1]))
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
    elif num_players in [9,10]:
        if player_roles[bot] == "Fascist":
            bot_game_sum[bot].append_to_last_user("Hitler is p"+str(hitler_index[0])+" and the other fascists are p"+str(fascist_index[1])+" and p"+str(fascist_index[2]))
            known_fascists.append(hitler_index[0])
            known_fascists.append(fascist_index[1])
            known_fascists.append(fascist_index[2])
    return(known_fascists)   

def handle_user_response(text, game, question_type):
    #print("welcome", text.lower())
    text = text.strip()
    bot_is_allowed_to_talk = False
    print(game)
    if question_type == "num_players": 
        allowed_answers = ["5","6","7","8","9","10"]
    elif question_type == "starting_player":
        allowed_answers = [str(i) for i in range(1, int(game["num_players"])+1)]
    elif question_type == "continue":
        bot_is_allowed_to_talk = True
        allowed_answers = ["y", "j"]
    elif question_type == "nominate":
        if "nom1" in text.lower():
            bot_is_allowed_to_talk = True
        allowed_answers = list(game["living_players"])
        allowed_answers.remove(game["current_president"])
        if game["previous_president"] != 0:
            if len(game["living_players"]) > 5:
                if game["previous_president"] in allowed_answers:
                    allowed_answers.remove(game["previous_president"])
            if game["previous_chancellor"] in allowed_answers:
                allowed_answers.remove(game["previous_chancellor"])
        allowed_answers = [str(num) for num in allowed_answers]
    elif question_type == "fas_lib":
        allowed_answers = ["f", "l"]
    elif question_type == "special_power":
        bot_is_allowed_to_talk = True
        allowed_answers = list(game["living_players"])
        allowed_answers.remove(game["current_president"])
        allowed_answers = [str(num) for num in allowed_answers]
    elif question_type in ["yes_or_no", "yes_or_no_vote"]:
        allowed_answers = ["y", "j", "n"]
    elif question_type == "new_load":
        allowed_answers = ["n", "l"]

    else:
        print("unknown question")

    if bot_conversation_box and bot_is_allowed_to_talk:
        bot_conversation_box.check_if_bot_wants_to_talk()

    while True:
        player_input = input("> " + text + " ")
        if player_input.lower() in allowed_answers:
            break
        else:
            clear_console_lines(1)
    
    if question_type == "yes_or_no_vote":
        if str(game["living_players"][-1]) in text:
            clear_console_lines(len(game["living_players"]))
    else:
        
        clear_console_lines(1)
    return player_input

def make_bot_response(text, speaking_bot):
    print('Bot: '+text, 'Speaking_bot: ', speaking_bot)
    bot_conversation_box.bot_talks(text)
    bot_response_thread = threading.Thread(target=bot_response, args=(text,speaking_bot,))
    bot_response_thread.start()

def bot_response(text, speaking_bot):
    try:
        bot_speak.say(text, bot_game_sum[speaking_bot].voice)
    except:
        pass

def start_new_game(game):
    dir_path = cwd + "/backups"
    file_list = os.listdir(dir_path)
    for file_name in file_list:
        file_path = os.path.join(dir_path, file_name)
        os.remove(file_path)
    game["game_is_going"] = True
    game["num_players"] = int(handle_user_response("Enter the number of players: ",{},"num_players"))
    game["num_bot_players"] = int(handle_user_response("Enter the number of bot players: ",game,"starting_player"))
    game["current_president"] = int(handle_user_response("Enter the starting player: ",game,"starting_player"))
    game["player_roles"] = distribute_roles(game["num_bot_players"],game["num_players"]) 
    for bot in range(game["num_bot_players"]):
        if game["player_roles"][bot] == "Liberal":
            bot_game_sum[bot].append(["system",'You are an cunning game theorist about to play the game Secret Hitler. You have been randomly assigned the role of "Liberal" this game. Your goal is to get 5 liberal policy tiles passed. You should try to figure out who the Fascists are and convince the other players to vote against them. You should also try to convince the other players to vote for you.'])
        elif game["player_roles"][bot] == "Fascist":
            bot_game_sum[bot].append(["system",'You are an cunning game theorist about to play the game Secret Hitler. You have been randomly assigned the role of "Fascist" this game. Your goal is to get 6 fascist policy tiles passed or to get Hitler elected as Chancellor after 3 policies have been played. You should never let anyone know that you are a Fascist, if anyone asks, lie and say that you are a liberal. You should also try to convince the other players to vote for you.'])
        elif game["player_roles"][bot] == "Hitler":
            bot_game_sum[bot].append(["system",'You are an cunning game theorist about to play the game Secret Hitler. You have been randomly assigned the role of "Hitler" this game. Your goal is to get 6 fascist policy tiles passed or to get elected as Chancellor after 3 policies have been played. You should never let anyone know that you are a Hitler. If anyone asks, lie and say that you are a liberal. You should also try to convince the other players to vote for you.'])
        game["known_fascists"] = tell_bot_fellow_fascists(bot, game["player_roles"], game["num_players"])   
    game["fascist_policies"] = 0
    game["liberal_policies"] = 0
    game["living_players"] = [i for i in range(1, game["num_players"]+1)]
    game["previous_president"] = 0
    game["previous_chancellor"] = 0
    game["failed_elections"] = 0
    game["special_election_helper"] = 0
    return game

def election_passed(game, current_chancellor):
    game["failed_elections"] = 0
    game["previous_president"] = game["current_president"]
    game["previous_chancellor"] = int(current_chancellor)
    return game

def enact_top_policy(game):
    enacted_top_policy = handle_user_response("Enact the top policy, was it (F)ascist or (L)iberal? ", game, "fas_lib")
    append_all_bot_summaries(game, "Three consecutive governments failed, so the policy was enacted and it was a ")
    debug_log('enacted_top_policy '+enacted_top_policy)
    if enacted_top_policy == "f":
        game["fascist_policies"] += 1
        append_all_bot_summaries(game, "fascist policy tile.")
    else:
        game["liberal_policies"] += 1
        append_all_bot_summaries(game, "liberal policy tile.")
    return game

def get_eligible_chancellors(game):
    eligible_chancellors = [i for i in game["living_players"] if i != game["current_president"] and i != game["previous_chancellor"]]
    eligible_chancellors.remove(game["previous_president"]) if len(game["living_players"]) > 5 and game["previous_president"] in eligible_chancellors else None
    eligible_chancellors_str = ", ".join([f"p{number}" for number in eligible_chancellors])
    return eligible_chancellors_str

def handle_voting(game): 
    bot_votes = [] 
    while True:
        human_ready = handle_user_response("Are you ready to see how the bot votes? (Y)es:  ", game, "continue")
        if human_ready == "y":
            for bot in range(game["num_bot_players"]):
                bot_vote = ask_bot(bot, "How do you vote? Answer with a single word, Yes or No.")
                make_bot_response("I vote "+bot_vote+" for this government.", bot)   
                bot_votes.append(bot_vote)        
            break
    return bot_votes

def handle_bot_nomination(game):
    bot_nomination_for_chancellor = ""
    while True:
        human_ready = handle_user_response("Are you ready to ask who the bot will nominate? (Y)es:  ", game, "continue")
        if human_ready == "y":
            eligible_chancellors = get_eligible_chancellors(game)
            bot_nomination_for_chancellor = ask_bot(int(game["current_president"])-1,"You must nominate a chancelor. Your choices are "+eligible_chancellors+". Which player do you choose? Answer with their player number only.")                
            break
    make_bot_response("I nominate player "+bot_nomination_for_chancellor+" as chancellor.", int(game["current_president"])-1)
    return bot_nomination_for_chancellor

# def save_game_history():
#     print("Game over. History saved.")
#     now = datetime.now()
#     dt_string = now.strftime("%d%m%Y%H%M")
#     with open(cwd+"/backups/game_state_backup.json", "r") as file1, open(cwd+"/backups/game_summary_backup.json", "r") as file2, open(cwd+"/backups/player_roles.txt", "r") as file3:
#         file1_contents = json.load(file1)
#         file2_contents = json.load(file2)
#         file3_contents = file3.read()
#     with open(cwd+"/history/"+dt_string+".txt", "w") as output_file:
#         output_file.write(json.dumps(file1_contents))
#         output_file.write(json.dumps(file2_contents))
#         output_file.write(file3_contents)
#     sys.exit(0)


def save_game_history():
    print("Game over. History saved.")
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M")

    # Get a list of all game summary backup files in the directory
    game_summary_files = glob.glob(cwd + "/backups/game_summary_backup*.json")

    # Load the contents of each file into a list
    game_summary_contents = []
    for file_path in game_summary_files:
        with open(file_path, "r") as file:
            game_summary_contents.append(json.load(file))

    # Load the contents of the other backup files
    with open(cwd+"/backups/game_state_backup.json", "r") as file1, open(cwd+"/backups/player_roles.txt", "r") as file2:
        file1_contents = json.load(file1)
        file2_contents = file2.read()

    # Write the history to a file
    with open(cwd+"/history/"+dt_string+".txt", "w") as output_file:
        output_file.write(json.dumps(file1_contents))
        for game_summary in game_summary_contents:
            output_file.write(json.dumps(game_summary))
        output_file.write(file2_contents)

    sys.exit(0)

    #TO GRACEFULLY EXIT THE GAME, THE TKINTER WINDOW NEEDS DESTROYED


def check_for_hitler_win(game, current_chancellor):
    game_is_going = True
    if game["player_roles"][int(current_chancellor)-1] == "Hitler" and game["fascist_policies"] > 2:
        if game["player_roles"][int(current_chancellor)-1] == "Hitler":
            make_bot_response("We win! I'm Hitler, fools.", current_chancellor)
        elif game["player_roles"][int(game["current_president"])-1] == "Fascist":
            make_bot_response("We win! Player "+str(current_chancellor)+" is Hitler.", game["current_president"])
        game_is_going = False
    return game_is_going

def bot_chancellor_policy_selection(chancellor, cards_seen, game):
    bot_chancellor_policy_choice = ask_bot(int(chancellor)-1, make_read_policies_question(cards_seen, game["current_president"]))
    bots_card =  cards_seen[int(bot_chancellor_policy_choice)-1]
    print("about to make it")
    make_bot_response("Play policy number "+bot_chancellor_policy_choice+". It is a " + bots_card + " policy.", int(chancellor)-1)
    bot_game_sum[int(chancellor)-1].append_to_last_user("You played a "+bots_card+" policy.")
    if bots_card == "fascist":
        game["fascist_policies"] += 1
        game["living_players"] = check_for_special_power(game)
    else:
        game["liberal_policies"] += 1
    game["game_is_going"] = check_for_policy_game_completion(game)
    return game

def human_chancellor_policy_selection(game, current_chancellor, cards_seen_pres):
    print("cards seen pres: "+str(cards_seen_pres))
    print("cards seen pres: "+str(cards_seen_pres))
    print("cards seen pres: "+str(cards_seen_pres))
    print("cards seen pres: "+str(cards_seen_pres))
    print("cards seen pres: "+str(cards_seen_pres))
    print("cards seen pres: "+str(cards_seen_pres))
    print("cards seen pres: "+str(cards_seen_pres))
    print("cards seen pres: "+str(cards_seen_pres))
    human_chancellor_policy_selection = handle_user_response("Which type of policy did Player "+current_chancellor+" play? (F)ascist or (L)iberal?", game, "fas_lib")
    if game["current_president"] <= int(game["num_bot_players"]):    
        text_to_append = "You passed p"+current_chancellor+" the following Policy tiles: "+cards_seen_pres[0]+", "+cards_seen_pres[1]+" and they played a "    
        bot_game_sum[int(game["current_president"])-1].append_to_last_user(text_to_append)
    if human_chancellor_policy_selection.lower() == "f":
        human_chancellor_policy_selection = "Fascist"
        game["fascist_policies"] += 1
        game["living_players"] = check_for_special_power(game)
    else:
        human_chancellor_policy_selection = "Liberal"
        game["liberal_policies"] += 1
    game["game_is_going"] = check_for_policy_game_completion(game)
    if game["current_president"] <= int(game["num_bot_players"]):
        bot_game_sum[int(game["current_president"])-1].append_to_last_user("p"+current_chancellor+" plays a "+human_chancellor_policy_selection+" Policy tile.")
    return game

bot_conversation_box = None


def create_tkinter_window(index):
    global bot_conversation_box
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.wm_attributes("-topmost", 1)
    #set the width and height of the window
    width = 2000
    height = 150

    # calculate the x and y positions of the window
    # x_pos = (root.winfo_screenwidth() // 2) - (width // 2)
    # y_pos = (root.winfo_screenheight() // 2) - (height // 2)

# set the geometry of the window to the specified values

    y_pos = 100 + (index * 150)
    bot_conversation_box = BotTalkBox(root, index, bot_game_sum, game, ask_bot, make_bot_response)
    root.geometry(f"{width}x{height}+0+{y_pos}")
    root.mainloop()


def start_bot_chat_boxes(num_bots):
    threads = []
    for i in range(num_bots):
        thread = threading.Thread(target=create_tkinter_window, args=(i,))
        threads.append(thread)
    for thread in threads:
        thread.start()

def main():
    global game
    clear_console_lines(2)
    print("\n")
    if handle_user_response("Would you like to start a (N)ew game or (L)oad the previous one? ", {}, "new_load") == "n":
        game = start_new_game(game)
    else:
        game.load_from_file()
        for bot in range(game["num_bot_players"]):
            bot_game_sum[bot].load_from_file()
    start_bot_chat_boxes(game["num_bot_players"])
    while (game["game_is_going"]):
        if game["current_president"] not in game["living_players"]:
            game["current_president"] = increase_current_president(game["current_president"], game["num_players"])
        global bot_conversation_box
        if game["failed_elections"] == 3:
            game = enact_top_policy(game)
        if game["current_president"] <= int(game["num_bot_players"]):
            #print("player1 pres")
            bot_nomination_for_chancellor = handle_bot_nomination(game)
            bot_votes = handle_voting(game)
            passed = input_vote_results(bot_votes, game)
            if passed:
                game = election_passed(game, bot_nomination_for_chancellor)
                game["game_is_going"] = check_for_hitler_win(game, bot_nomination_for_chancellor)
                make_bot_response("Please show me 3 cards.", int(game["current_president"])-1)
                cards_seen_pres = read_gov_policies.show(3, debugging)
                bot_president_policy_discard = ask_bot(int(game["current_president"])-1,make_read_policies_question(cards_seen_pres, bot_nomination_for_chancellor))
                make_bot_response("Discard policy number "+bot_president_policy_discard, int(game["current_president"])-1)
                cards_seen_pres.pop(int(bot_president_policy_discard)-1)
                policies_vetoed = False
                if(game["fascist_policies"] == 5): #veto possibility
                    if int(bot_nomination_for_chancellor) <= int(game["num_bot_players"]):
                        policies_vetoed = check_for_bot_chancellor_veto(bot_nomination_for_chancellor, cards_seen_pres, game)
                    else:
                        human_chancellor_veto_offer = handle_user_response("Does Player"+str(bot_nomination_for_chancellor)+" want to offer a veto? (Y)es or (N)o?", game, "yes_or_no")
                        if (human_chancellor_veto_offer in ["Y","y"]):                        
                            determine_if_president_bot_wants_to_veto(cards_seen_pres, game["player_roles"][int(game["current_president"])-1], bot_nomination_for_chancellor, game["known_fascists"], game["fascist_policies"], game["liberal_policies"])
                        else:
                            bot_game_sum[int(game["current_president"])-1].append_to_last_user("Your Chancellor, P"+str(bot_nomination_for_chancellor)+" did not want a veto.")
                if not policies_vetoed:  
                    if int(bot_nomination_for_chancellor) <= int(game["num_bot_players"]):
                        time.sleep(3)
                        game = bot_chancellor_policy_selection(bot_nomination_for_chancellor, cards_seen_pres, game)
                    else:
                        #cards_seen_pres.remove(cards_seen_pres[int(bot_president_policy_discard)-1])
                        print("remaining cards2: "+str(cards_seen_pres))
                        game = human_chancellor_policy_selection(game, bot_nomination_for_chancellor, cards_seen_pres)
            else:
                game["failed_elections"] += 1
            game["current_president"] = increase_current_president(game["current_president"], game["num_players"])
        else:
            #debug_log('game1 '+ game)
            humans_nomination_for_chancellor = handle_user_response("Player "+str(game["current_president"])+", who do you nominate as chancellor? answer with their player number only: ", game, "nominate")
            #debug_log('game5 '+game)
            if int(humans_nomination_for_chancellor) <= int(game["num_bot_players"]):
                bot_game_sum[int(humans_nomination_for_chancellor)-1].append_to_last_user("P"+str(game["current_president"])+" has nominated you as Chancellor")
                for bot in range(game["num_bot_players"]):
                    if bot != int(humans_nomination_for_chancellor):
                        bot_game_sum[bot].append_to_last_user("P"+str(game["current_president"])+" has nominated P"+humans_nomination_for_chancellor+" as Chancellor")
            else:
                append_all_bot_summaries_except_president(game, "P"+str(game["current_president"])+" has nominated P"+humans_nomination_for_chancellor+" as Chancellor")
            #debug_log('game4 '+game)
            bot_votes = handle_voting(game)
            passed = input_vote_results(bot_votes, game)
            if passed:
                game = election_passed(game, humans_nomination_for_chancellor)
                #RIGHT NOW THE BOT GETS THE ELECTRION RESULTS, BUT IS NOT TOLD WHO THE CHANCELLOR IS - MAYBE WE WANT TO DO THIS TOO
                game["game_is_going"] = check_for_hitler_win(game, humans_nomination_for_chancellor)
                if int(humans_nomination_for_chancellor) <= int(game["num_bot_players"]):
                    cards_seen = read_gov_policies.show(2, debugging)
                policies_vetoed = False
                if(game["fascist_policies"] == 5):
                    if int(humans_nomination_for_chancellor) <= int(game["num_bot_players"]):
                        policies_vetoed = check_for_bot_chancellor_veto(humans_nomination_for_chancellor, cards_seen, game)
                    else:
                        human_president_veto_response = handle_user_response("Does p"+humans_nomination_for_chancellor+" want to veto? (Y)es or (N)o?", game, "yes_or_no")
                        if (human_president_veto_response in ["Y","y"]):
                            policies_vetoed = True
                if not policies_vetoed:
                    if int(humans_nomination_for_chancellor) <= int(game["num_bot_players"]):
                        game = bot_chancellor_policy_selection(humans_nomination_for_chancellor, cards_seen, game)
                    else:
                        game = human_chancellor_policy_selection(game, humans_nomination_for_chancellor, [])

            else:
                game["failed_elections"] += 1
            # if game["special_election_helper"] < 11:
            #     game["current_president"] = game["special_election_helper"]
            #     game["special_election_helper"] = 11
            if game["special_election_helper"] < 0:
                temp = game["current_president"]
                game["current_president"] = -game["special_election_helper"]
                game["special_election_helper"] = temp
            elif game["special_election_helper"] > 0:
                game["current_president"] = game["special_election_helper"]
                game["special_election_helper"] = 0
                game["current_president"] = increase_current_president(game["current_president"], game["num_players"])
            else:
                game["current_president"] = increase_current_president(game["current_president"], game["num_players"])

    save_game_history()

main()