# crea una nuova finesta multipane per lanciare comandi per pepper E per sensori simulati
# https://tmuxcheatsheet.com/
# https://arcolinux.com/everthing-you-need-to-know-about-tmux-panes/
# https://tmuxguide.readthedocs.io/en/latest/tmux/tmux.html

tmux new-window -t $SESSION:3 -n 'multipane'
tmux send-keys -t $SESSION:3 "cd ~/playground" C-m
tmux split-window -t $SESSION:3 -v -p 25
tmux send-keys -t $SESSION:3 "cd ~/src/pepper_tools" C-m
tmux send-keys -t $SESSION:3 "alias say='python asr/human_say.py --sentence'" C-m
tmux send-keys -t $SESSION:3 "alias tap='python touch/touch_sim.py --sensor'" C-m