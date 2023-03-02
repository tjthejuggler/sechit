class GameSummary:
    def __init__(self, summary=None):
        if summary is None:
            self.summary = []
        else:
            self.summary = summary
    
    def read(self):
        return self.summary
    
    def append(self, new_entry):
        self.summary.append({"role": new_entry[0], "content": new_entry[1]})

    def append_to_last_user(self, new_entry):
        if self.summary[-1]["role"] == "user":
            self.summary[-1]["content"] += new_entry
        else:
            self.summary.append({"role": "user", "content": new_entry})