# tiktok-bulk-downloader
TikTok videos bulk downloader with or without watermark by username. 

# prerequisites 
```
pip -q install pycryptodome pycryptodomex fake-useragent
```

# usage
At first, you should run the script with "generate" option. This will generate and save json file that conatins all user posts data.
```
python tiktok_dl.py --username [target username] --generate
```
You can after that download the videos without watermark from the latest saved json file you generate.
```
python tiktok_dl.py --download
```
Use "watermark" argument in case you want to download the videos with watermark.
```
python tiktok_dl.py --download --watermark
```
You can take a shortcut and do it all in one command.
```
python tiktok_dl.py --username [target username] --download --watermark
```
<br><br><br><br><br><br><br>
*Feel free to write any suggestions you think about.*
