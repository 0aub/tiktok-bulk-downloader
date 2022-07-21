# tiktok-bulk-downloader
TikTok videos bulk downloader with or without watermark by username. 

# prerequisites 
```
pip -q install pycryptodome pycryptodomex
```
only for downloading posts without watermark:
- selenium version 2.48.0 because it support phantomjs browser
- phantomjs is required: https://bitbucket.org/ariya/phantomjs/downloads
- make sure you change the unzipped folder name to 'phantomjs'
the below steps worked fine with me
```
pip -q install selenium==2.48.0
wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2 
tar xvjf phantomjs-2.1.1-linux-x86_64.tar.bz2 
cp phantomjs-2.1.1-linux-x86_64/bin/phantomjs /usr/local/bin 
```


# usage
script arguments:
- -u   --username
- -g   --generate
- -d   --download
- -nw  --no-watermark

At first, you should run the script with "generate" option. This will generate and save json file that conatins all user posts data.
```
python tiktok_dl.py --username [target username] --generate
```
You can after that download the videos from the latest saved json file you generate.
```
python tiktok_dl.py --download
```
Use "no-watermark" argument in case you want to download the videos without watermark.
```
python tiktok_dl.py --download --no-watermark
```
You can take a shortcut and do it all in one command.
```
python tiktok_dl.py --username [target username] --download --no-watermark
```
<br><br><br><br><br><br><br>
*Feel free to write any suggestions you think about.*
