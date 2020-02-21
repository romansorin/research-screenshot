import requests
import json
from models.Database import drop, migrate, Session
from migrations.Response import Response
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from config.database import conn_string
alexa_url = 'https://ats.api.alexa.com/api?Action=Topsites&Count=10&ResponseGroup=Country&Start=1&Output=json'
api_key = 'xcBVFF7Ypf1E4CXbIkOnctD1vl4drcw5ZJZEPYC0'
headers = {'x-api-key': api_key}

a = [{'Ats': {'OperationRequest': {'RequestId': '0c7cf045-1e12-4dc0-839d-ea9549bb3c3c'}, 'Results': {'Result': {'Alexa': {'Request': {'Arguments': {'Argument': [{'Name': 'countrycode', 'Value': 'Global'}, {'Name': 'start', 'Value': '1'}, {'Name': 'count', 'Value': '10'}, {'Name': 'responsegroup', 'Value': 'Country'}]}}, 'TopSites': {'Country': {'CountryName': 'GLOBAL', 'CountryCode': '*', 'TotalSites': '104520', 'Sites': {'Site': [{'DataUrl': 'google.com', 'Country': {'Rank': '1', 'Reach': {'PerMillion': '592500'}, 'PageViews': {'PerMillion': '245220', 'PerUser': '14.77'}}, 'Global': {'Rank': '1'}}, {'DataUrl': 'youtube.com', 'Country': {'Rank': '2', 'Reach': {'PerMillion': '324100'}, 'PageViews': {'PerMillion': '64028', 'PerUser': '7.05'}}, 'Global': {'Rank': '2'}}, {'DataUrl': 'tmall.com', 'Country': {'Rank': '3', 'Reach': {'PerMillion': '115400'}, 'PageViews': {'PerMillion': '9215', 'PerUser': '2.85'}}, 'Global': {'Rank': '3'}}, {'DataUrl': 'facebook.com', 'Country': {'Rank': '4', 'Reach': {'PerMillion': '68340'}, 'PageViews': {'PerMillion': '15000', 'PerUser': '7.84'}}, 'Global': {'Rank': '4'}}, {'DataUrl': 'baidu.com', 'Country': {'Rank': '5', 'Reach': {'PerMillion': '77700'}, 'PageViews': {'PerMillion': '9294', 'PerUser': '4.27'}}, 'Global': {'Rank': '5'}}, {'DataUrl': 'qq.com', 'Country': {'Rank': '6', 'Reach': {'PerMillion': '76900'}, 'PageViews': {'PerMillion': '8652', 'PerUser': '4.01'}}, 'Global': {'Rank': '6'}}, {'DataUrl': 'sohu.com', 'Country': {'Rank': '7', 'Reach': {'PerMillion': '71600'}, 'PageViews': {'PerMillion': '9360', 'PerUser': '4.67'}}, 'Global': {'Rank': '7'}}, {'DataUrl': 'login.tmall.com', 'Country': {'Rank': '8', 'Reach': {'PerMillion': '105000'}, 'PageViews': {'PerMillion': '2941', 'PerUser': '1'}}, 'Global': {'Rank': '8'}}, {'DataUrl': 'taobao.com', 'Country': {'Rank': '9', 'Reach': {'PerMillion': '60700'}, 'PageViews': {'PerMillion': '5928', 'PerUser': '3.49'}}, 'Global': {'Rank': '9'}}, {'DataUrl': '360.cn', 'Country': {'Rank': '10', 'Reach': {'PerMillion': '53300'}, 'PageViews': {'PerMillion': '5850', 'PerUser': '3.92'}}, 'Global': {'Rank': '10'}}]}}}}}, 'ResponseStatus': {'StatusCode': '200'}}}}]

b = {
    'test': 1,
    'test2': 2
}


from models.Base import Base, Session, engine

Base.metadata.create_all(engine)




"""
NOTE: THINGS ARE INCREDIBLY, INCREDIBLY BROKEN.
"""
print(json.dumps(b))
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine

if __name__ == "__main__":
    session = Session()

    response = Response(content=5)

    session.add(response)
    session.commit()
    session.close()
    # Database.drop()
    # Database.migrate()
    # # print(a)
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
