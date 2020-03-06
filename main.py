import datetime
import json

import requests

from config.app import STORAGE_LOGS_PATH, QUERY_START_PATH
from config.aws import HEADERS
from migrations.ParsedResponse import ParsedResponse
from migrations.Response import Response
from migrations.Site import Site
from models.Driver import Driver
from models.Base import Base, Session, engine


# TODO: Flag sites that have a scroll height of over 30000 (arbitrary)
# TODO: On site screenshot, record time elapsed, scroll height, flag status, screenshot path, sitename, url, etc.
# TODO: Possibly check amt of white space in screenshot?
# TODO: Possibly switch to regular screenshot method instead of height extension if scroll height > 30000 or flag?


def migrate_fresh():
    Base.metadata.drop_all(engine)
    print("Dropped tables")
    Base.metadata.create_all(engine)
    print("Created tables")


"""
DONE - 1. Query AWS API
 - Add response to database
 - Update start variable (found in plaintext txt)

DONE - 2. SELECT response FROM responses
 - Clean up each result: structure: Ats->Results->Result->Alexa->TopSites->Country->Sites->Site[Object]
 - Mark that query as parsed
 - Create a Site object from that

3. Take screenshot of DataUrl from that query
 - Create Screenshot object linked to that site
 - Run RGB Screenshot object into greyscale conversion
"""

"""
https://github.com/rohanbaisantry/image-clustering
https://github.com/asselinpaul/ImageSeg-KMeans
https://github.com/abhijeet3922/Image-compression-with-Kmeans-clustering
https://shirinsplayground.netlify.com/2018/10/keras_fruits_cluster/
https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
https://keras.io/applications/
https://stackoverflow.com/questions/39123421/image-clustering-by-its-similarity-in-python
https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_ml/py_kmeans/py_kmeans_opencv/py_kmeans_opencv.html
https://github.com/eriklindernoren/ML-From-Scratch
https://github.com/zegami/image-similarity-clustering
https://github.com/Wrinth/Image-Compression-with-K-Means-Clustering
https://github.com/elcorto/imagecluster
https://github.com/beleidy/unsupervised-image-clustering
"""

"""

- extract name of site from exploded url

for cases where domain names are the same:
- keep subdomains even if root domain is same
- two options for handling duplicates root domains, but different tlds:
    1. keep organizational tld, filter/pop geographical tlds
    2. run another hidden layer / image processing step for image similarity; if 95%+ similar
"""


# TODO: Add method documentation

def query_api_url(count, start):
    return f'https://ats.api.alexa.com/api?Action=Topsites&Count={count}&ResponseGroup=Country&Start={start}&Output=json'


def parse_response(data):
    return data['Ats']['Results']['Result']['Alexa']['TopSites']['Country']['Sites']['Site']


def make_api_request(url):
    return requests.get(url, headers=HEADERS)


def log_response(data):
    filename = f"query_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(json.dumps(data))
    f.close()


def file_safe_timestamp():
    return str(datetime.datetime.now()).replace(" ", "_").replace(".", "-").replace(":", "-")


def collect_aws_data():
    session = Session()
    limit = 1001
    lower = 1
    interval = 100

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

    filename = f"parsed_response_{file_safe_timestamp()}.log"
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


def convert_parsed_to_site():
    session = Session()
    data = session.query(ParsedResponse).all()

    filename = f"parsed_to_sites_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")

    for response in data:
        print(f"Beginning response {response.id}")
        f.write(f"Beginning response {response.id}: \n")
        split_url = response.url.split(".")
        site = Site(name='_'.join(split_url), host=response.url)
        print(f"Parsing site {'_'.join(split_url)} at host {response.url}")
        f.write(f"Parsing site {'_'.join(split_url)} at host {response.url} \n\n")
        session.add(site)
        session.commit()
        print(f"Finished parsing response number {response.id}")
        f.write(f"Finished parsing response number {response.id} \n\n")

    session.close()

def __image_sim__():
    r = requests.post(
        "https://api.deepai.org/api/image-similarity",
        data={
            'image1': 'https://i.ibb.co/9skSC62/download-3.png',
            'image2': 'https://i.ibb.co/NnTFz5Y/download-4.png',
        },
        headers={'api-key': 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'}
    )
    print(r.json())

"""
To create a site object:
fields(name, host)

Given a parsed response in the form of fields(url):
  - Split up the URL by it's root and subdomain, as well as TLD
  - Use the root domain for base name, and use subdomain with replaced period delimiter as hyphen (ex. status.romansorin.com becomes name=status-romansorin)
  - Figure out an efficient way to sort and search the root domains
  - If root domain is equal to another root domain, flag it; eventually compare the screenshot of two sites; if they are below some threshold of similarity (such as 10) then only use the response that is ranked higher
  - set url = host
"""

"""
For screenshots:
: foreach sites as site :
  - Navigate to site.host
  - Take screenshot (fullpage)
  - Convert to greyscale rgb
  - Make any comparisons as necessary
"""

if __name__ == "__main__":
    log_filename = f"screenshot_{file_safe_timestamp()}.log"
    driver = Driver(log_filename)
    sites = [
        {
            'name': 'romansorin',
            'url': 'https://romansorin.com'
        }
    ]

    for site in sites:
        driver.run(site)
    driver.quit()
