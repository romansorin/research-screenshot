from models.Base import Base, Session, engine
from migrations.Site import Site
from migrations.Screenshot import Screenshot
from migrations.Response import Response
from migrations.ParsedResponse import ParsedResponse
from config.aws import API_KEY
import requests
import time
import json
import datetime
from config.app import STORAGE_LOGS_PATH, QUERY_START_PATH

a = {'Ats': {'OperationRequest': {'RequestId': '0c7cf045-1e12-4dc0-839d-ea9549bb3c3c'}, 'Results': {'Result': {'Alexa': {'Request': {'Arguments': {'Argument': [{'Name': 'countrycode', 'Value': 'Global'}, {'Name': 'start', 'Value': '1'}, {'Name': 'count', 'Value': '10'}, {'Name': 'responsegroup', 'Value': 'Country'}]}}, 'TopSites': {'Country': {'CountryName': 'GLOBAL', 'CountryCode': '*', 'TotalSites': '104520', 'Sites': {'Site': [{'DataUrl': 'google.com', 'Country': {'Rank': '1', 'Reach': {'PerMillion': '592500'}, 'PageViews': {'PerMillion': '245220', 'PerUser': '14.77'}}, 'Global': {'Rank': '1'}}, {'DataUrl': 'youtube.com', 'Country': {'Rank': '2', 'Reach': {'PerMillion': '324100'}, 'PageViews': {'PerMillion': '64028', 'PerUser': '7.05'}}, 'Global': {'Rank': '2'}}, {'DataUrl': 'tmall.com', 'Country': {'Rank': '3', 'Reach': {'PerMillion': '115400'}, 'PageViews': {'PerMillion': '9215', 'PerUser': '2.85'}}, 'Global': {'Rank': '3'}}, {'DataUrl': 'facebook.com', 'Country': {'Rank': '4', 'Reach': {'PerMillion': '68340'}, 'PageViews': {'PerMillion': '15000', 'PerUser': '7.84'}}, 'Global': {'Rank': '4'}}, {'DataUrl': 'baidu.com', 'Country': {'Rank': '5', 'Reach': {'PerMillion': '77700'}, 'PageViews': {'PerMillion': '9294', 'PerUser': '4.27'}}, 'Global': {'Rank': '5'}}, {'DataUrl': 'qq.com', 'Country': {'Rank': '6', 'Reach': {'PerMillion': '76900'}, 'PageViews': {'PerMillion': '8652', 'PerUser': '4.01'}}, 'Global': {'Rank': '6'}}, {'DataUrl': 'sohu.com', 'Country': {'Rank': '7', 'Reach': {'PerMillion': '71600'}, 'PageViews': {'PerMillion': '9360', 'PerUser': '4.67'}}, 'Global': {'Rank': '7'}}, {'DataUrl': 'login.tmall.com', 'Country': {'Rank': '8', 'Reach': {'PerMillion': '105000'}, 'PageViews': {'PerMillion': '2941', 'PerUser': '1'}}, 'Global': {'Rank': '8'}}, {'DataUrl': 'taobao.com', 'Country': {'Rank': '9', 'Reach': {'PerMillion': '60700'}, 'PageViews': {'PerMillion': '5928', 'PerUser': '3.49'}}, 'Global': {'Rank': '9'}}, {'DataUrl': '360.cn', 'Country': {'Rank': '10', 'Reach': {'PerMillion': '53300'}, 'PageViews': {'PerMillion': '5850', 'PerUser': '3.92'}}, 'Global': {'Rank': '10'}}]}}}}}, 'ResponseStatus': {'StatusCode': '200'}}}}


# Start

def migrate_fresh():
    Base.metadata.drop_all(engine)
    print("Dropped tables")
    Base.metadata.create_all(engine)
    print("Created tables")


"""
1. Query AWS API
 - Add response to database
 - Update start variable (found in plaintext txt)

2. SELECT response FROM responses
 - Clean up each result: structure: Ats->Results->Result->Alexa->TopSites->Country->Sites->Site[Object]
 - Mark that query as parsed
 - Create a Site object from that

3. Take screenshot of DataUrl from that query
 - Create Site object
 - Create Screenshot object linked to that site
 - Run RGB Screenshot object into greyscale conversion
"""


def query_api_url(count, start):
    return f'https://ats.api.alexa.com/api?Action=Topsites&Count={count}&ResponseGroup=Country&Start={start}&Output=json'


def parse_response(data):
    return data['Ats']['Results']['Result']['Alexa']['TopSites']['Country']['Sites']['Site']


headers = {'x-api-key': API_KEY}
def make_api_request(url):
    return requests.get(url, headers=headers)


def log_response(data):
    timestamp = datetime.datetime.now()
    timestamp = str(timestamp).replace(" ", "_").replace(".", "-").replace(":", "-")
    filename = f"query_{timestamp}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now())+ "\n\n")
    f.write(json.dumps(data))
    f.close()


if __name__ == "__main__":
    session = Session()
    limit = 3
    lower = 1
    interval = 3

    for i in range(lower, limit, interval):
        query_start = int(open(QUERY_START_PATH, 'r').readlines()[0])
        print(f"Querying sites at count {query_start}")
        if query_start >= limit:
            print("Exceeded limit")
            break
        aws_request_url = query_api_url(start=query_start, count=interval)
        aws_res = make_api_request(aws_request_url)
        log_response(aws_res.json())
        response = Response(query=aws_request_url, response=aws_res.json())
        session.add(response)
        session.commit()
        f = open(QUERY_START_PATH, 'w')
        f.write(str(query_start + interval))
        f.close()

    session.close()

    # # r = requests.get(alexa_url, headers=headers)
    # f = open("test.json", "w")
    # # print(r.json())
    # # f.write(json.dumps(a))
    # f.close()
    # driver = Driver()
    # for site in sites:
    #     start_time, last_height = setup(site["name"], site["url"])
    #     last_height = scroll(last_height)
    #     rescroll(last_height)
    #     screenshot(site["name"], start_time, last_height)
    # driver.quit()


