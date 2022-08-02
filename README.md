# tiktok-bulk-downloader
TikTok videos bulk downloader with or without watermark by username. 

# prerequisites 
General requirements
```
pip -q install pycryptodome pycryptodomex
```
no watermark requirements
```
pip -q install selenium webdriver_manager
```

# usage
Script arguments
<pre>
<li> -u    --username
<li> -g    --generate
<li> -d    --download
<li> -nw   --no-watermark
</pre>

At first, you should run the script with "generate" option. This will generate and save json file that conatins all user posts data.
<br>
Note: Do not incloud "@" to the target username
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
