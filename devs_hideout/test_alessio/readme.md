in terminal:
cd ~/hri_software/docker
./run.bash
docker exec -it pepperhri tmux a

in tmux:

cd /opt/Aldebaran/naoqi-sdk-2.5.5.5-linux64
./naoqi

In choreographe:
edit-->preferences--> Virtual Robot  and check port (42693)

in terminal:
export PEPPER_IP=127.0.0.1:port
