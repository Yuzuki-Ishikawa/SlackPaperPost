import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from Bio import Entrez
import openai
import random


openai.api_key = 'YourOpenAIToken'   # OpenAI API token
SLACK_API_TOKEN = 'YourSlackToken' # Slack API token
SLACK_CHANNEL = "#general"  # Slack channel name

MAX_RESULTS = 10            # Maximum number of paper scraped at a time
NUM_CONTENTS = 3            # Number of contents to be posted at a time (chosen randomly)

EMAIL = 'your_email@example.com'
JOURNAL_LIST = ['Nat Neurosci']
QUERY = 'fMRI'

def get_summary(result):
    """
    FUNCTION: get_summary
        This function calls chatGPT 3.5-turbo API to summarize the given paper in 
        only three points.
        Input: result (dict) - a dictionary containing the information of a paper
        Output: message (str) - a string containing the summary
    """

    # ChatGPT input
    system = """Summarize the given paper in only three points and output the results using the following format```
    Paper's Title
    ・Point 1
    ・Point 2
    ・Point 3
    ```"""
    text = f"title: {result['Title']}\nbody: {result}"

    # call chatGPT API
    response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role': 'system', 'content': system},
                    {'role': 'user', 'content': text}
                ],
                temperature=0.25,
            )
    
    # create the response message
    summary = response['choices'][0]['message']['content']
    title, *body = summary.split('\n')
    body = '\n'.join(body)
    pub_date = result['EPubDate']
    url = f"https://doi.org/{result['DOI']}"
    journal = result['FullJournalName']

    return f"*{title}*\nDate: {pub_date}\n{journal}\n{url}\n{body}\n"
  

def main():
    """
    FUNCTION: main
        This is the main function of this program.
    """

    # initialize slack API token
    client = WebClient(token=SLACK_API_TOKEN)
    Entrez.email = EMAIL 
    query = QUERY
    search_results, summary_results = [], []

    # scrape the newest [MAX_RESULTS] papers from each journal
    for journal in JOURNAL_LIST:
        handle = Entrez.esearch(db="pubmed", term=query + f" AND {journal}[journal]", sort="date", retmax=MAX_RESULTS)
        record = Entrez.read(handle)
        search_results.extend(record["IdList"])

    # randomly choose [NUM_CONTENTS] papers from the scraped papers
    random.shuffle(search_results)
    for id in search_results[:NUM_CONTENTS]:
        handle = Entrez.esummary(db="pubmed", id=id)
        record = Entrez.read(handle)
        summary_results.append(record[0])
    
    # post the summary to Slack
    response = client.chat_postMessage(
        channel=SLACK_CHANNEL,
        text='Daily Post Arrived!'
    )
    for i, result in enumerate(summary_results):
        try:
            # create summary messages
            message = f"*Paper {i+1}*\n{get_summary(result)}\n\n"
            response = client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=message
            )
            print(f"Message posted: {response['ts']}")

        except SlackApiError as e:
            print(f"Error posting message: {e}")

if __name__ == "__main__":
    main()


# python paper_post.py