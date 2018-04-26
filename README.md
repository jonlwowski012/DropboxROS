# DropboxROS


### Virtual Machine (Client)
```sh
$ nano ~/.bashrc
# Add the following lines to .bashrc
export MY_IP=`ifconfig | grep -A1 enp0 | grep inet | awk -F" " {'print $2'} | a$
export ROS_MASTER_URI=http://$MY_IP:11311
export ROS_HOSTNAME="$MY_IP"
export ROS_IP="$MY_IP"
```





### Local Machine (server)
```sh
$ roscd dropboxros/server_folder
$ rosrun dropboxros filenames_server.py
```
