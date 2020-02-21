from models.Base import Base, Session, engine
from config.aws import API_KEY, API_URL
import json

headers = {'x-api-key': API_KEY}
a = {'Ats': {'OperationRequest': {'RequestId': '0c7cf045-1e12-4dc0-839d-ea9549bb3c3c'}, 'Results': {'Result': {'Alexa': {'Request': {'Arguments': {'Argument': [{'Name': 'countrycode', 'Value': 'Global'}, {'Name': 'start', 'Value': '1'}, {'Name': 'count', 'Value': '10'}, {'Name': 'responsegroup', 'Value': 'Country'}]}}, 'TopSites': {'Country': {'CountryName': 'GLOBAL', 'CountryCode': '*', 'TotalSites': '104520', 'Sites': {'Site': [{'DataUrl': 'google.com', 'Country': {'Rank': '1', 'Reach': {'PerMillion': '592500'}, 'PageViews': {'PerMillion': '245220', 'PerUser': '14.77'}}, 'Global': {'Rank': '1'}}, {'DataUrl': 'youtube.com', 'Country': {'Rank': '2', 'Reach': {'PerMillion': '324100'}, 'PageViews': {'PerMillion': '64028', 'PerUser': '7.05'}}, 'Global': {'Rank': '2'}}, {'DataUrl': 'tmall.com', 'Country': {'Rank': '3', 'Reach': {'PerMillion': '115400'}, 'PageViews': {'PerMillion': '9215', 'PerUser': '2.85'}}, 'Global': {'Rank': '3'}}, {'DataUrl': 'facebook.com', 'Country': {'Rank': '4', 'Reach': {'PerMillion': '68340'}, 'PageViews': {'PerMillion': '15000', 'PerUser': '7.84'}}, 'Global': {'Rank': '4'}}, {'DataUrl': 'baidu.com', 'Country': {'Rank': '5', 'Reach': {'PerMillion': '77700'}, 'PageViews': {'PerMillion': '9294', 'PerUser': '4.27'}}, 'Global': {'Rank': '5'}}, {'DataUrl': 'qq.com', 'Country': {'Rank': '6', 'Reach': {'PerMillion': '76900'}, 'PageViews': {'PerMillion': '8652', 'PerUser': '4.01'}}, 'Global': {'Rank': '6'}}, {'DataUrl': 'sohu.com', 'Country': {'Rank': '7', 'Reach': {'PerMillion': '71600'}, 'PageViews': {'PerMillion': '9360', 'PerUser': '4.67'}}, 'Global': {'Rank': '7'}}, {'DataUrl': 'login.tmall.com', 'Country': {'Rank': '8', 'Reach': {'PerMillion': '105000'}, 'PageViews': {'PerMillion': '2941', 'PerUser': '1'}}, 'Global': {'Rank': '8'}}, {'DataUrl': 'taobao.com', 'Country': {'Rank': '9', 'Reach': {'PerMillion': '60700'}, 'PageViews': {'PerMillion': '5928', 'PerUser': '3.49'}}, 'Global': {'Rank': '9'}}, {'DataUrl': '360.cn', 'Country': {'Rank': '10', 'Reach': {'PerMillion': '53300'}, 'PageViews': {'PerMillion': '5850', 'PerUser': '3.92'}}, 'Global': {'Rank': '10'}}]}}}}}, 'ResponseStatus': {'StatusCode': '200'}}}}
API_URL='https://ats.api.alexa.com/api?Action=Topsites&Count=10&ResponseGroup=Country&Start=1&Output=json'



# Count
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

"""


def query_api_url(count, start):
    return f'https://ats.api.alexa.com/api?Action=Topsites&Count={count}&ResponseGroup=Country&Start={start}&Output=json'


def parse_response(data):
    return data['Ats']['Results']['Result']['Alexa']['TopSites']['Country']['Sites']['Site']


with open('test.json') as f:
    data = json.load(f)



if __name__ == "__main__":
    val = int(open('./storage/query_start.txt', 'r').readlines()[0])

    ff = open('./storage/query_start.txt', 'w')

    ff.write(str(val + 11))

    # b = json.dumps(a)
    for site in parse_response(data):
        print(site)
    # f = open("test.json", "w")
    # f.write(b)
    # f.close()
    # limit = 10001
    # lower = 1
    # interval = 100

    # # Find ranges given limit and interval
    # for i in range(lower, limit, interval):
    #     intervals = [i, i + interval - 1]

    #     query_api(intervals[0], interval)

    # migrate_fresh()
    # session = Session()

    # response = Response(content=a)

    # session.add(response)
    # session.commit()
    # session.close()


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


