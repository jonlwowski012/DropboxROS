roscore &
sleep 3
rosrun dropboxros login_server.py &
rosrun dropboxros update_server.py &
rosrun dropboxros update_client.py &
rosrun dropboxros filenames_server.py &
rosrun dropboxros share_file_server.py &
rosrun dropboxros get_key_server.py &
rosrun dropboxros delete_file_server.py &
