import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from Bio import Entrez
import openai
import random

#OpenAI api key
openai.api_key = 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
# Slack API token
SLACK_API_TOKEN = xoxb-5231824136707-5244594676065-t5ivsDV1umNUbsSV7dKh4x8f
# Slack channel name
SLACK_CHANNEL = "#general"
# Maximum number of paper scraping at a time
MAX_RESULTS = 100

def get_summary(result):
    system = """与えられた論文の要点を3点のみでまとめ、以下のフォーマットで日本語で出力してください。```
    タイトルの日本語訳
    ・要点1
    ・要点2
    ・要点3
    ```"""

    text = f"title: {result.title}\nbody: {result.summary}"
    response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': text}
                ],
                temperature=0.25,
            )
    summary = response['choices'][0]['message']['content']
    title_en = result.title
    title, *body = summary.split('\n')
    body = '\n'.join(body)
    date_str = result.published.strftime("%Y-%m-%d %H:%M:%S")
    message = f"発行日: {date_str}\n{result.entry_id}\n{title_en}\n{title}\n{body}\n"
    
    return message
  
def main(event, context):
    # initialize slack API token
    client = WebClient(token=SLACK_API_TOKEN)
    #queryを用意、今回は、三種類のqueryを用意
    query ='ti:%22 Deep Learning %22'

    # PubMed Entrez module
    Entrez.email = 'email@example.com'
    
    
    
    
    search = arxiv.Search(
        query=query,  # 検索クエリ（
        max_results=100,  # 取得する論文数
        sort_by=arxiv.SortCriterion.SubmittedDate,  # sort papersby submission data
        sort_order=arxiv.SortOrder.Descending,  # 新しい論文から順に取得する
    )
    #searchの結果をリストに格納
    result_list = []
    for result in search.results():
        result_list.append(result)
    #ランダムにnum_papersの数だけ選ぶ
    num_papers = 3
    results = random.sample(result_list, k=num_papers)
    
    # 論文情報をSlackに投稿する
    for i,result in enumerate(results):
        try:
            # Slackに投稿するメッセージを組み立てる
            message = "今日の論文です！ " + str(i+1) + "本目\n" + get_summary(result)
            # Slackにメッセージを投稿する
            response = client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=message
            )
            print(f"Message posted: {response['ts']}")
        except SlackApiError as e:
            print(f"Error posting message: {e}")
