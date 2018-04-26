# DropboxROS


### Virtual Machine (Client)
```sh
$ nano ~/.bashrc
# Add the following lines to .bashrc (Replace ***CLIENT_IP*** and ***SERVER_IP***
export MY_IP=***CLIENT_IP***
export ROS_MASTER_URI=http://***SERVER_IP***:11311
export ROS_HOSTNAME="$MY_IP"
export ROS_IP="$MY_IP"
```





### Local Machine (server)
```sh
$ roscd dropboxros/server_folder
$ rosrun dropboxros filenames_server.py
```
