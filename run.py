import AutoAnimeDownloader

def run():
  print('Running')
  AutoAnimeDownloader.initialize_json()
  AutoAnimeDownloader.getUrlLinkCSV()
  AutoAnimeDownloader.checkAndUpdate()
  
if __name__ == '__main__':
  run()