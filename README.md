# DropboxROS

### Install ROS Kinetic on Server and Client
http://wiki.ros.org/kinetic/Installation

### Virtual Machine (Jonathan Clients)
```sh
$ nano ~/.bashrc
# Add the following lines to .bashrc (Replace ***CLIENT_IP*** and ***SERVER_IP***)
export MY_IP=***CLIENT_IP***
export ROS_MASTER_URI=http://***SERVER_IP***:11311
export ROS_HOSTNAME="$MY_IP"
export ROS_IP="$MY_IP"

$ roscd dropboxros/jonathan_folder
$ rosrun dropboxros ClientGUI.py
```

### Virtual Machine (Taylor Clients)
```sh
$ nano ~/.bashrc
# Add the following lines to .bashrc (Replace ***CLIENT_IP*** and ***SERVER_IP***)
export MY_IP=***CLIENT_IP***
export ROS_MASTER_URI=http://***SERVER_IP***:11311
export ROS_HOSTNAME="$MY_IP"
export ROS_IP="$MY_IP"

$ roscd dropboxros/taylor_folder
$ rosrun dropboxros ClientGUI.py
```

### Local Machine (server)
```sh
$ nano ~/.bashrc
# Add the following lines to .bashrc (Replace ***SERVER_IP***)
export MY_IP=***SERVER_IP***
export ROS_MASTER_URI=http://***SERVER_IP***:11311
export ROS_HOSTNAME="$MY_IP"
export ROS_IP="$MY_IP"

$ roscd dropboxros/server_folder
$ sh ../src/start_server.sh
```
