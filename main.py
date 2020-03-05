import datetime
import json

import requests

from config.app import STORAGE_LOGS_PATH, QUERY_START_PATH
from config.aws import HEADERS
from migrations.ParsedResponse import ParsedResponse
from migrations.Response import Response
from models.Base import Base, Session, engine


def migrate_fresh():
    Base.metadata.drop_all(engine)
    print("Dropped tables")
    Base.metadata.create_all(engine)
    print("Created tables")


"""
DONE - 1. Query AWS API
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


def make_api_request(url):
    return requests.get(url, headers=HEADERS)


def log_response(data):
    timestamp = datetime.datetime.now()
    timestamp = str(timestamp).replace(" ", "_").replace(".", "-").replace(":", "-")
    filename = f"query_{timestamp}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(json.dumps(data))
    f.close()


def collect_aws_data():
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


def parse_collected_data():
    session = Session()
    data = session.query(Response).filter_by(parsed=False)

    timestamp = datetime.datetime.now()
    timestamp = str(timestamp).replace(" ", "_").replace(".", "-").replace(":", "-")
    filename = f"parsed_response_{timestamp}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")

    for site in data:
        response_id = site.id
        print(f"Beginning response number {response_id}")
        f.write(f"Beginning response number {response_id} \n")

        for response in parse_response(site.response):
            url = response['DataUrl']
            print(f"Beginning site {url}")
            f.write(f"Beginning site {url}: ")
            rank = response['Global']['Rank']
            reach_per_million = response['Country']['Reach']['PerMillion']
            page_views_per_million = response['Country']['PageViews']['PerMillion']
            page_views_per_user = response['Country']['PageViews']['PerUser']
            f.write(
                f"Rank: {rank}, Reach/Million: {reach_per_million}, Page Views/Million: {page_views_per_million}, Page Views/User: {page_views_per_user} \n")
            parsed_response = ParsedResponse(response_id=response_id, url=url, rank=rank,
                                             reach_per_million=reach_per_million,
                                             page_views_per_million=page_views_per_million,
                                             page_views_per_user=page_views_per_user)
            session.add(parsed_response)
            session.commit()

        session.query(Response).get(response_id).parsed = True
        print(f"Finished parsing response number {response_id}")
        f.write(f"Finished parsing response number {response_id} \n\n")
        session.commit()

    session.close()
    f.close()



if __name__ == "__main__":
    parse_collected_data()
    # driver = Driver()
    # for site in sites:
    #     start_time, last_height = setup(site["name"], site["url"])
    #     last_height = scroll(last_height)
    #     rescroll(last_height)
    #     screenshot(site["name"], start_time, last_height)
    # driver.quit()
