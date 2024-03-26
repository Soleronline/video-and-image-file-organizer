# video-and-image-file-organizer
Video and image file organizer

1. Clone the repository
```
$ git clone https://github.com/Soleronline/video-and-image-file-organizer.git
```

2. Create a virtual environment using any of the following commands
```
$ virtualenv -p python3 venv
$ python -m venv
```

3. Activate the environment
```
$ source venv/bin/activate
```

4. Install the requirements
```
$ pip install -r requirements.txt
```

5. Everything ready to execute the command
- To obtain **information** on how many image and video files there are in a directory, execute the following command:
```
$ ./organizer_file.py info <directory>
```

- To **move** image and video files, execute the following command
```
$ ./organizer_file.py move <directory_source> <directory_destination>
```

- To **copy** the image and video files, execute the following command
```
$ ./organizer_file.py copy <directory_source> <directory_destination>
```
