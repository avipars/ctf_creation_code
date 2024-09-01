## Build Scripts



#### Compilation
Compile the .py script to C and then to a binary executable, works cross-platform.
I wanted to shrink and obfuscate the code as much as possible. 
Adding an external file required an additional flag as well, so I ended up with a bunch of flags (maybe too many)


```
python -m nuitka --onefile --windows-console-mode=force --warn-implicit-exceptions --warn-unusual-code --show-anti-bloat-changes --noinclude-default-mode=error --prefer-source-code --noinclude-custom-mode=setuptools:error --no-pyi-file --lto=yes  --nofollow-imports  --plugin-enable=anti-bloat,implicit-imports,data-files,pylint-warnings --include-data-files=cola.whatever=cola.whatever --python-flag=nosite,-OO --report=compilation-report.xml socket_server.py --output-dir=dist --output-filename=blah.exe
```

#### Compression

Compresses the exe as much as possible (level 9) (can install upx via winget)
```
upx --ultra-brute -9 blah.exe
```
