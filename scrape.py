def main_code(search_tag, secret_key):  
  import time
  import xlwt
  import json, time
  import pandas as pd
  from xlwt import Workbook
  from selenium import webdriver
  from IPython.display import Image, display

  options = webdriver.ChromeOptions()
  options.add_argument('-headless')
  options.add_argument('-no-sandbox')
  options.add_argument('-disable-dev-shm-usage')
  cols = ["Video Title","Video URL","Channel Name","Channel ID","Number of views","Upload Date"]

  driver = webdriver.Chrome('chromedriver',options=options)
  def get_video_results():
      start = time.time()
      global results
      url = 'https://www.youtube.com/results?search_query='
      driver.get(url+search_tag)
      print(driver.current_url)

      last_limit = 100
      while True:
        try:
          end_result = driver.find_element_by_css_selector('#message').is_displayed()
          driver.execute_script("var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;")
          results = driver.find_elements_by_css_selector('.text-wrapper.style-scope.ytd-video-renderer')
          if (len(results)>= last_limit):
              last_limit = last_limit+100
              end = time.time()
              print(f'Extracting results {len(results)} found')
              print(f"Runtime of the program is {end - start}")
          if end_result == True or len(results) >= 100000:
              end = time.time()
              print(f"Runtime of the program is {end - start}")
              driver.save_screenshot("image.png")
              break
        except:
          end = time.time()
          print(f"Runtime of the program is {end - start}")
          driver.save_screenshot("image.png")
  get_video_results()
  end = time.time()

  youtube_data = []
  youtube_name = set()
  for result in results:
      title = result.find_element_by_css_selector('.title-and-badge.style-scope.ytd-video-renderer').text
      link = result.find_element_by_css_selector('.title-and-badge.style-scope.ytd-video-renderer a').get_attribute('href')
      channel_name = result.find_element_by_css_selector('.long-byline').text
      channel_link = result.find_element_by_css_selector('#text > a').get_attribute('href')
      views = result.find_element_by_css_selector('.style-scope ytd-video-meta-block').text.split('\n')[0]

      try:
          time_published = result.find_element_by_css_selector('.style-scope ytd-video-meta-block').text.split('\n')[1]
      except:
          time_published = None

      try:
          snippet = result.find_element_by_css_selector('.metadata-snippet-container').text
      except:
          snippet = None

      try:
          if result.find_element_by_css_selector('#channel-name .ytd-badge-supported-renderer') is not None:
              verified_badge = True
          else:
              verified_badge = False
      except:
          verified_badge = None

      try:
          extensions = result.find_element_by_css_selector('#badges .ytd-badge-supported-renderer').text
      except:
          extensions = None
      index = results.index(result)
      print(f'Working on index {index+1}/{len(results)}',end = '')

      if title not in youtube_name:
          youtube_name.add(title)
          youtube_data.append([title,link,channel_name,channel_link,views,time_published])

  df = pd.DataFrame(youtube_data, columns=cols)
  writer = pd.ExcelWriter('test.xlsx', engine='xlsxwriter')
  df.to_excel(writer, sheet_name='sheet1', index=False)
  writer.save()
  driver.quit()

  import os
  import googleapiclient.discovery

  def main(string_list):
      global secret_key
      os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
      api_service_name = "youtube"
      api_version = "v3"
      DEVELOPER_KEY = secret_key

      youtube = googleapiclient.discovery.build(
          api_service_name, api_version, developerKey = DEVELOPER_KEY)

      request = youtube.videos().list(
          part="snippet,contentDetails,statistics",
          id=string_list
      )
      response = request.execute()

      return (response)

  new_youtube_data = []
  global response
  string_list = ''
  count = 0
  for i in df['Video URL']:
    string_list = string_list+ (f'{i[32:]},')
    count = count+1
    if count%49 ==0:
      try:
        response = main(string_list)
        for i in response['items']:
          title = i['snippet']['title'] #title
          video_url = 'https://www.youtube.com/watch?v=' + i['id'] #url
          channel_title = i['snippet']['channelTitle']
          channel_id = i['snippet']['channelId']
          views = i['statistics']['viewCount']
          upload = i['snippet']['publishedAt']
          new_youtube_data.append([title, video_url, channel_title, channel_id, views, upload])
        string_list = ''
      except:
        print("API LIMIT IS EXCEEDED")
        string_list = ''
        continue

  df = pd.DataFrame(new_youtube_data, columns=cols)
  writer = pd.ExcelWriter('final_output.xlsx', engine='xlsxwriter')
  df.to_excel(writer, sheet_name='sheet1', index=False)
  writer.save()

  from google.colab import files
  files.download('final_output.xlsx') 
  files.download('test.xlsx')
