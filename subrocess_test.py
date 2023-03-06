import os

# Create a new tmux session with two panes
os.system('tmux new-session -d -s mysession -n main "bash"')
os.system('tmux split-window -h -t mysession:0 "bash"')

# Connect the panes
os.system('tmux pipe-pane -t mysession:0.0 -o "cat >> ~/temp"')
os.system('tmux pipe-pane -t mysession:0.1 -o "cat >> ~/temp"')
os.system('tmux pipe-pane -t mysession:0.0 -o "cat ~/temp"')

# Attach the session
os.system('tmux attach-session -t mysession')
