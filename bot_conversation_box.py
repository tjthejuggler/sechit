import tkinter as tk
import random

class BotTalkBox:
    def __init__(self, master, index, bot_game_sum, game, ask_bot, make_bot_response):
        self.master = master
        self.index = index
        self.bot_game_sum = bot_game_sum
        self.game = game
        self.label = None
        self.text_box = None
        self.ask_bot = ask_bot
        self.make_bot_response = make_bot_response
        self.create_widgets()

    def create_widgets(self):
        self.text_box = tk.Text(self.master, height=5, width=300, font=("Arial", 14))
        self.text_box.pack()

        self.label = tk.Label(self.master, text="Bot:", font=("Arial", 14, 'bold'), justify='left', fg='blue')
        self.label.pack(anchor='w')

        # Create a submit button and bind its command to submit_text
        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit_text)
        self.submit_button.pack()

        self.randomly_offer_to_let_bot_talk()

    def submit_text(self):
        self.text_box.see("1.0")
    
        text = self.text_box.get("1.0", "end-1c")

        possible_player_numbers = [2,3,4,5,6,7,8,9,10]
        if "living_players" in self.game:
            possible_player_numbers = list(self.game["living_players"])
            possible_player_numbers.remove(1)
       
        player_number = text.split()[0] if len(text.split()) > 1 else ""
        if  player_number.isdigit() and int(player_number) in possible_player_numbers:
            bot_response = self.ask_bot(0, "p"+player_number+" says: "+text.split(None, 1)[1])
            self.make_bot_response(bot_response, 0)
            self.text_box.delete('1.0', tk.END)
            self.text_box.focus_set()

    def randomly_offer_to_let_bot_talk(self):
        self.check_if_bot_wants_to_talk()
        self.master.after(random.randint(10000, 50000), self.randomly_offer_to_let_bot_talk)

    def check_if_bot_wants_to_talk(self):
        if "player_roles" in self.game and True == False:
            bot_wants_to_talk_response = self.ask_bot(0, "Is there anything you would like to say or ask? answer with a single word, Yes or No.")
            if bot_wants_to_talk_response.lower().startswith(('y', 'j')) or 'yes' in bot_wants_to_talk_response.lower():  
                bot_comment = self.ask_bot(0, "What would you like to say?")
                self.make_bot_response(bot_comment, self.index)

    def bot_talks(self, text):
        self.label.config(text="Bot"+str(self.index)+": "+text)

if __name__ == '__main__':
    root = tk.Tk()
    app = BotTalkBox(root)
    root.mainloop()
