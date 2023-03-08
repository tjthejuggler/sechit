# import tkinter as tk

# class BotTalkBox:
#     def __init__(self, master):
#         self.master = master
#         self.label = None
#         self.text_box = None
#         self.create_widgets()

#     def create_widgets(self):
#         # create a label widget with a larger font
#         self.label = tk.Label(self.master, text="Enter some text:", font=("Arial", 14))
#         self.label.pack()

#         # create a text box widget with a larger font
#         self.text_box = tk.Text(self.master, height=5, width=30, font=("Arial", 14))
#         self.text_box.pack()

#         # bind the Return key to the submit_text function
#         self.text_box.bind("<Return>", self.submit_text)

#     def submit_text(self, event=None):
#         # move the insertion cursor to the beginning of the widget
#         self.text_box.see("1.0")
    
#         text = self.text_box.get("1.0", "end-1c")
#         print(text)
#         self.text_box.delete('1.0', tk.END)
#         self.text_box.focus_set()


import tkinter as tk
import random

class BotTalkBox:
    def __init__(self, master, bot_game_sum, game, ask_bot, make_bot_response):
        self.master = master
        self.bot_game_sum = bot_game_sum
        self.game = game
        self.label = None
        self.text_box = None
        self.ask_bot = ask_bot
        self.make_bot_response = make_bot_response
        self.create_widgets()

    def create_widgets(self):
        # create a label widget with a larger font
        self.label = tk.Label(self.master, text="Enter some text:", font=("Arial", 14))
        self.label.pack()

        # create a text box widget with a larger font
        self.text_box = tk.Text(self.master, height=5, width=30, font=("Arial", 14))
        self.text_box.pack()

        # bind the Return key to the submit_text function
        self.text_box.bind("<Return>", self.submit_text)

        # schedule the update_label function to be called after a random delay
        self.randomly_offer_to_let_bot_talk()

    def submit_text(self, event=None):
        # move the insertion cursor to the beginning of the widget
        self.text_box.see("1.0")
    
        text = self.text_box.get("1.0", "end-1c")
        print(text, self.bot_game_sum.read(),self.game)
        self.text_box.delete('1.0', tk.END)
        self.text_box.focus_set()

    def conversation_mode(self): #TODO this needs merged into the submit_text function
        possible_player_numbers = [2,3,4,5,6,7,8,9,10]
        if "living_players" in self.game:
            possible_player_numbers = list(self.game["living_players"])
            possible_player_numbers.remove(1)
        while True:        
            conversation_input = input("CONVERSATION MODE(enter to switch): Enter your player number, followed by your comment: ")
            player_number = conversation_input.split()[0] if len(conversation_input.split()) > 1 else ""
            if conversation_input == "":
                clear_console_lines(1)
                break
            elif player_number.isdigit() and int(player_number) in possible_player_numbers:
                bot_response = ask_bot("p"+player_number+" says: "+conversation_input.split(None, 1)[1])
                make_bot_response(bot_response)
                input("Press Enter to continue...")
                clear_console_lines(3)
            else:
                clear_console_lines(1)


    def randomly_offer_to_let_bot_talk(self):
        self.check_if_bot_wants_to_talk()
        self.master.after(random.randint(1000, 5000), self.update_label)

    def check_if_bot_wants_to_talk(self):
        if "player_roles" in self.game:
            bot_wants_to_talk_response = self.ask_bot("Is there anything you would like to say or ask? answer with a single word, Yes or No.")
            if bot_wants_to_talk_response.lower().startswith(('y', 'j')) or 'yes' in bot_wants_to_talk_response.lower():  
                bot_comment = self.ask_bot("What would you like to say?")
                self.make_bot_response(bot_comment)
                #print(bot_wants_to_talk_response)  
                self.bot_talks(bot_wants_to_talk_response)
        # set the label text to the given text

    def bot_talks(self, text):
        self.label.config(text=text)

if __name__ == '__main__':
    root = tk.Tk()
    app = BotTalkBox(root)
    root.mainloop()

