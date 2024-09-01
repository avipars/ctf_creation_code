Things I never used in the final CTF or couldn't find another place for them


## PyInstaller and Alternative Data Streams

I tried using pyinstaller prior to nuitka, but it has some downsides. Notably, it only compiles for the OS of where the script is ran (for me = windows) and how easy it is to reverse engineer and get back python code. 

```
REM pyinstaller --onefile --optimize 2 --clean --nowindowed --add-data C:\server\ascii_cola.txt:ascii_cola.txt socket_server.py 
REM this doesn't obfuscate code too much, also leaves a nice pyc file whcih can give you back source code
REM so nukita seems like a better option

REM OBFUSCATION ONLY
REM python -OO -m py_compile C:\\server\socket_server.py
```

I also played around with Alternative Data Streams in Windows. It was easy enough to use on my local machine, but as soon as I tried to upload a file with ADS on git or to copy to another location (even on my computer)... it wouldn't keep the data stream intact. 