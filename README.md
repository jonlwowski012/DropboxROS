# DropboxROS

### Server Side (Terminal 1)
```sh
$ roscd dropboxros/server_folder
$ rosrun dropboxros filenames_server.py
```

### Server Side (Terminal 2)
```sh
$ roscd dropboxros/server_folder
$ rosrun dropboxros update_client.py
```

### Server Side (Terminal 3)
```sh
$ roscd dropboxros/server_folder
$ rosrun dropboxros update_server.py
```

### Client Side (Terminal 4)
```sh
$ roscd dropboxros/client_folder
$ rosrun dropboxros ClientGUI.py
```
