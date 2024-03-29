import os
import json
import random
cwd = os.getcwd()

def get_random_voice():
    voices = ["com.au", "us", "co.uk", "co.in"]
    return voices[random.randint(0, len(voices)-1)]

class BotGameSummary:
    def __init__(self, debugging, index, summary=None):
        self.debugging = debugging
        self.index = index
        self.voice = get_random_voice()
        if summary is None:
            self.summary = []
        else:
            self.summary = summary
   
    def read(self):        
        if self.debugging:
            print("append", self.summary)
        return self.summary

    def append(self, new_entry):
        self.summary.append({"role": new_entry[0], "content": new_entry[1]})
        #save a backup of self to a file
        self.save_to_file()
        if self.debugging:
            print("append", self.summary)        

    def append_to_last_user(self, new_entry):
        if self.debugging:
            print('index', self.index)
            print('summary', self.summary)
        if self.summary[-1]["role"] == "user":
            self.summary[-1]["content"] += "\n"+new_entry
        else:
            self.summary.append({"role": "user", "content": new_entry})
        self.save_to_file()
        if self.debugging:
            print("append_to_last_user", self.summary)

    # def save_to_file(self):
    #     with open(cwd+'/backups/game_summary_backup.json', 'w') as file:
    #         json.dump(self, file)

    def save_to_file(self):
        with open(cwd+'/backups/game_summary_backup'+str(self.index)+'.json', 'w') as file:
            json.dump(self.summary, file)

    def load_from_file(self):
        try:
            with open(cwd+'/backups/game_summary_backup'+str(self.index)+'.json', 'r') as file:
                data = json.load(file)
            self.summary = data
        except FileNotFoundError:
            print('Backup file not found.')