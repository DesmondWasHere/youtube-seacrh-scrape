change = False
def get_data(id, secret_key):
    if change:
        secret_key = "AIzaSyDosYWs2HvR7NZ2c1SOW-4EiY0mm3AdT-g"
    url = f'https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&id={id}&key={secret_key}'
    response = requests.get(url)
    try:
        viewCount = response.json()['items'][0]['statistics']['viewCount'] 
        uploadDate = response.json()['items'][0]['snippet']['publishedAt'] 
        return [viewCount, uploadDate]
    except Exception as e:
        print(e)
        print("Backup Key called")
        change = True
        return ["",""]
        
def main_function(df, secret_key):
    import requests
    import pandas as pd
    cols = ["Video Title","Video URL","Channel Name","Channel URL","Number of views","Upload Date"]
    youtube_data = []

    # df = pd.read_excel('test.xlsx')

    count = 0
    for i in range(0, len(df)):
        count = count + 1
        print(f'Working on {count}/{len(df)}')
        link = df.loc[i]['Video URL'][32:]
        result = get_data(link, secret_key)
        youtube_data.append([
            df.loc[i]['Video Title'],
            df.loc[i]['Video URL'],
            df.loc[i]['Channel Name'],
            df.loc[i]['Channel ID'],
            result[0],
            result[1]
        ])
    df = pd.DataFrame(youtube_data, columns=cols) 
    writer = pd.ExcelWriter('final_output.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='sheet1', index=False)
    writer.save()
    from google.colab import files
    files.download('final_output.xlsx') 
