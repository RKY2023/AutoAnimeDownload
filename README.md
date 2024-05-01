# AutoAnimeDownload
## config
### Step 1
1. pip install -r .\requirements.txt
2. add your csv location in `csv_location` variable
3. add anime name in  `anime_list` variable

## setting venv for each python project
python -m venv venv
pip install bs4 requests winotify pandas pymysql pymongo
py .\run.py
pip freeze > requirements.txt
