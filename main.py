from __future__ import print_function
import datetime
import json
import os
from shutil import copyfile
import numpy as np
import cv2
import requests
import math
from tld import get_tld

from config.app import STORAGE_LOGS_PATH, QUERY_START_PATH, CLUSTER_DATA_PATH, CLUSTER_OUTPUT_PATH
from config.aws import HEADERS
from config.openai import IMAGE_SIMILARITY_API_KEY, SIMILARITY_THRESHOLD
from migrations.ParsedResponse import ParsedResponse
from migrations.Response import Response
from migrations.Screenshot import Screenshot
from migrations.Site import Site
from models.Base import Base, Session, engine
from models.Driver import Driver
from models.Screenshot import ScreenshotEnum, to_greyscale


def migrate_fresh():
    """
    Drop and create all database tables as defined by imported migrations

    :return: None
    """
    Base.metadata.drop_all(engine)
    print("Dropped tables")
    Base.metadata.create_all(engine)
    print("Created tables")


def query_api_url(count, start):
    """
    Queries the Alexa API for top sites with a global scope

    :param count: Number of sites to return in a response
    :param start: Index of site to start from according to the Alexa API
    :return: json
    """
    return f'https://ats.api.alexa.com/api?Action=Topsites&Count={count}&ResponseGroup=Country&Start={start}&Output=json'


def parse_response(data):
    """
    Parse response and return json array of sites + associated data

    :param data: json data returned by Alexa API, such as that returned in fn(query_api_url)
    :return: json
    """
    return data['Ats']['Results']['Result']['Alexa']['TopSites']['Country']['Sites']['Site']


def make_api_request(url):
    """AWS request helper function

    :param url: URL to query from Alexa
    :return: response
    """
    return requests.get(url, headers=HEADERS)


def log_query_response(data):
    """
    Write query response from Alexa to log file
    :param data: json data (response) from request
    :return: None
    """
    filename = f"query_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(json.dumps(data))
    f.close()


def file_safe_timestamp():
    """
    Get the current timestamp that can be written as part of a file name

    :return: str
    """
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
        log_query_response(aws_res.json())
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


def __determine_image_sim__(path_one, path_two):
    r = requests.post(
        "https://api.deepai.org/api/image-similarity",
        files={
            'image1': open(path_one, 'rb'),
            'image2': open(path_two, 'rb')
        },
        headers={'api-key': IMAGE_SIMILARITY_API_KEY}
    )
    return r.json()


def process_sites():
    session = Session()

    sites = session.query(Site).filter_by(processed=False)

    for site in sites:
        log_filename = f"screenshot_{file_safe_timestamp()}.log"
        driver = Driver(log_filename)
        driver.run(site, session)
        driver.quit()

    session.close()


def reprocess_failed_sites():
    session = Session()

    failed_sites = session.query(Screenshot).filter_by(failed=True)
    for site in failed_sites:
        site = session.query(Site).get(site.site_id)
        log_filename = f"screenshot_{file_safe_timestamp()}.log"
        driver = Driver(log_filename)
        driver.run(site, session)
        driver.quit()

    session.close()


def convert_site_colorspace():
    filename = f"convert_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")

    session = Session()
    screenshots = session.query(Screenshot).filter_by(type=ScreenshotEnum.RGB)
    for screenshot in screenshots:
        sc_check = session.query(Screenshot).filter_by(site_id=screenshot.site_id)
        flag = False
        for sc in sc_check:
            if sc.type == ScreenshotEnum.GREYSCALE:
                print('Found greyscale version of screenshot.')
                f.write(f"Found greyscale version of screenshot. Skipping (id={sc.id})\n\n")

                flag = True
        if flag:
            pass
        else:
            site_name = session.query(Site).get(screenshot.site_id).name

            print(f"Converting screenshot of site {site_name} from RGB to GREYSCALE")
            f.write(f"Converting screenshot of site {site_name} from RGB to GREYSCALE \n")

            path = to_greyscale(screenshot.path, site_name)
            greyscale_screenshot = Screenshot(site_id=screenshot.site_id, type=ScreenshotEnum.GREYSCALE, path=path)
            session.add(greyscale_screenshot)
            session.commit()

            print(f"Finished conversion of {site_name} from RGB to GREYSCALE")
            f.write(f"Finished conversion of {site_name} from RGB to GREYSCALE \n\n")

    session.close()


def __set_domain_keys__(delimited_list):
    domains = {}
    for site in delimited_list[1]:
        domains.update({site.split('.')[0]: []})

    for site in delimited_list[2]:
        tld = get_tld(site, fix_protocol=True)
        if len(tld.split('.')) == 2:
            domains.update({site.split('.')[0]: []})
        else:
            subdomain = site.split('.')[0]
            domain = site.split('.')[1]
            key = '.'.join([subdomain, domain])
            domains.update({key: []})

    for site in delimited_list[3]:
        subdomain = site.split('.')[0]
        domain = site.split('.')[1]
        key = '.'.join([subdomain, domain])
        domains.update({key: []})

    return domains


def find_dimension_constraints():
    height = 50000
    width = 50000
    filename = f"crop_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(f"Initializing constraints using dimensions [height: {height}] and [width: {width}]\n")
    for image in os.listdir(CLUSTER_DATA_PATH):
        if image.endswith('.png'):
            image_name = image
            f.write(f"Checking screenshot {image_name}\n")
            image = cv2.imread(f"{CLUSTER_DATA_PATH}/{image_name}")

            h = image.shape[0]
            w = image.shape[1]
            f.write(f"Height: {h}, width: {w}\n")
            if h < height:
                f.write(
                    f"{image_name} height is smaller than maximum constraint {height}, setting new constraint to {h}\n")
                height = h
            if w < width:
                f.write(
                    f"{image_name} height is smaller than maximum constraint {width}, setting new constraint to {w}\n")
                width = w

    print(height, width)
    f.write(f"Height: {height}, width: {height}")
    f.close()


def set_image_dimensions():
    height = 1440
    width = 2560
    filename = f"crop_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(f"Using dimensions [height: {height}] and [width: {width}]\n")
    for image in os.listdir(CLUSTER_DATA_PATH):
        if image.endswith('.png'):
            image_name = image
            f.write(f"Checking screenshot {image_name}")
            image = cv2.imread(f"{CLUSTER_DATA_PATH}/{image_name}")
            if image.shape[0] > height:
                f.write(f"{image_name} exceeds height, cropping\n")
                image = image[0:height, 0:image.shape[1]]
            if image.shape[1] > width:
                f.write(f"{image_name} exceeds width, cropping\n")
                image = image[0:image.shape[0], 0:width]

            cv2.imwrite(f"{CLUSTER_DATA_PATH}/{image_name}", image)
            f.write(f"Finished {image_name} \n\n")
    f.close()


def __set_domain_values__(domains, delimited_list):
    for site in delimited_list[1]:
        domains[site.split('.')[0]].append(site)

    for site in delimited_list[2]:
        tld = get_tld(site, fix_protocol=True)
        if len(tld.split('.')) == 2:
            domains[site.split('.')[0]].append(site)
        else:
            domains['.'.join([site.split('.')[0], site.split('.')[1]])].append(site)

    for site in delimited_list[3]:
        domains['.'.join([site.split('.')[0], site.split('.')[1]])].append(site)

    return domains


def insertion_sort(arr):
    for i in range(len(arr)):
        cursor = arr[i]
        pos = i

        while pos > 0 and arr[pos - 1] > cursor:
            # Swap the number down the list
            arr[pos] = arr[pos - 1]
            pos = pos - 1
        # Break and do the final swap
        arr[pos] = cursor

    return arr


def identify_layout_duplicates():
    filename = f"id_layout_duplicates_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")
    f.write(
        f"Layout duplication identification function, using threshold {SIMILARITY_THRESHOLD} for distance in image similarity")
    session = Session()

    sites = session.query(Site).order_by(Site.host)

    list_by_delimiters = {
        1: [],
        2: [],
        3: []
    }
    f.write(f"Initialize list by delimiters: {list_by_delimiters}\n\n")

    for site in sites:
        delimiter_count = site.host.count('.')
        list_by_delimiters[delimiter_count].append(site.host)
    f.write(f"Updated list by delimiters: {list_by_delimiters}\n\n")

    domains = __set_domain_keys__(list_by_delimiters)
    f.write(f"Domains by keys: {domains}\n\n")
    domains = __set_domain_values__(domains, list_by_delimiters)
    f.write(f"Domains with values: {domains}\n\n")

    unique_domains = []

    pre_filter_count = 0
    for domains in domains.values():
        pre_filter_count += len(domains)
        if len(domains) == 1:
            print(f"Unique domain {domains[0]}")
            f.write(f"Unique domain {domains[0]}\n")
            unique_domains.append(domains[0])
        elif len(domains) == 0:
            print("No domain found, skipping")
            f.write("No domain found, skipping\n")
        else:
            filtered_domains = []
            for domain in domains:
                filtered_domains.append(session.query(Site).filter_by(host=domain).first().id)

            # Make sure that the filtered domains are sorted
            filtered_domains = insertion_sort(filtered_domains)
            unique_domains.append(session.query(Site).filter_by(id=filtered_domains[0]).first().host)
            base_domain = filtered_domains[0]
            print(f"Base domain {base_domain}\n")
            f.write(f"Base domain {base_domain}\n")
            base_domain_path = session.query(Screenshot).filter_by(site_id=base_domain).first().path
            for i in range(1, len(filtered_domains)):
                response = __determine_image_sim__(base_domain_path, session.query(Screenshot).filter_by(
                    site_id=filtered_domains[i]).first().path)
                parsed = json.loads(json.dumps(response))
                distance = parsed['output']['distance']
                print(f"Similarity distance: {distance}\n")
                f.write(f"Similarity distance: {distance}\n")
                if int(distance) < int(SIMILARITY_THRESHOLD):
                    pass
                else:
                    host = session.query(Site).filter_by(id=filtered_domains[i]).first().host
                    print(f"Appending host {host}\n")
                    f.write(f"Appending host {host}\n")
                    unique_domains.append(host)

    post_filter_count = len(unique_domains)
    print(f"Pre filter count: {pre_filter_count}\n")
    f.write(f"Pre filter count: {pre_filter_count}\n")
    print(f"Post filter count: {post_filter_count}\n")
    f.write(f"Post filter count: {post_filter_count}\n")
    session.close()
    f.close()

    filename = f"unique_domains_{file_safe_timestamp()}.log"
    f = open(f"{STORAGE_LOGS_PATH}/{filename}", "x")
    f.write(str(datetime.datetime.now()) + "\n\n")
    for d in unique_domains:
        f.write(f"{d}\n")
    print(unique_domains)
    f.close()
    return unique_domains


def verify_db_integrity():
    session = Session()
    sites = session.query(Site).all()
    for site in sites:
        result = session.query(Screenshot).filter_by(site_id=site.id).first()
        if not result:
            print(site.id)

    screenshots = session.query(Screenshot).filter_by(type=ScreenshotEnum.GREYSCALE)
    for screenshot in screenshots:
        result = session.query(Site).filter_by(id=screenshot.site_id).first()
        if not result:
            print(screenshot.id)


def copy_unique_screenshots():
    filename = 'unique_domains.log'
    session = Session()
    f = open(f'{STORAGE_LOGS_PATH}/{filename}', 'r')
    log_filename = f"copy_unique_screenshots_{file_safe_timestamp()}.log"
    log = open(f"{STORAGE_LOGS_PATH}/{log_filename}", "x")
    log.write(str(datetime.datetime.now()) + "\n\n")
    unique_domains = f.readlines()
    for domain in unique_domains:
        if domain.endswith('\n'):
            domain = domain[0:len(domain) - 1]

        print(f"Domain {domain}")
        log.write(f"Domain {domain}\n")
        site = session.query(Site).filter_by(host=domain).first()
        screenshot = session.query(Screenshot).filter_by(type=ScreenshotEnum.GREYSCALE,
                                                         site_id=site.id).first()
        copyfile(screenshot.path, f"{CLUSTER_DATA_PATH}/{site.name}.png")
        print(f"Copied greyscale screenshot to {CLUSTER_DATA_PATH}/{site.name}.png")
        log.write(f"Copied greyscale screenshot to {CLUSTER_DATA_PATH}/{site.name}.png\n")
    f.close()
    print("Finished copying screenshots")
    log.write("Finished copying screenshots\n\n")
    log.close()


def overlay_images():
    clusters = os.listdir(CLUSTER_OUTPUT_PATH)
    i = 0
    for cluster in clusters:
        cluster_path = f"{CLUSTER_OUTPUT_PATH}/{cluster}"
        cluster_items = os.listdir(cluster_path)

        subcluster_items = subclusters(cluster_items, 50)
        j=0
        for i in subcluster_items:
            overlay(cluster_path, i, j)
            j += 1

        # overlay(cluster_path, cluster_items)


def subclusters(cluster_items, limit):
    clusters = []
    count = 0
    index = 0
    for i in range(0,  math.ceil(len(cluster_items)/limit)):
        clusters.append([])
        for j in range(index, len(cluster_items)):
            if count == limit:
                count = 0
                break

            clusters[i].append(cluster_items[index])
            index += 1
            count += 1
    return clusters


def overlay(cluster_path, cluster_items, subcluster_count):
    image = cv2.cvtColor(cv2.imread(f"{cluster_path}/{cluster_items[0]}"), cv2.COLOR_BGR2GRAY)
    for i in range(1, len(cluster_items)):
        image_0 = image
        image_1 = cv2.cvtColor(cv2.imread(f"{cluster_path}/{cluster_items[i]}"), cv2.COLOR_BGR2GRAY)

        # 0 is width, 1 is height
        image_0_dimensions = [image_0.shape[1], image_0.shape[0]]
        image_1_dimensions = [image_1.shape[1], image_1.shape[0]]

        if image_1_dimensions[1] != 1440:
            os.remove(f"{cluster_path}/{cluster_items[i]}")
        else:
            if image_0_dimensions[0] != image_1_dimensions[0]:
                if image_0_dimensions[0] < image_1_dimensions[0]:
                    image_1 = cv2.resize(image_1, (image_0_dimensions[0], image_0_dimensions[1]))
                else:
                    image_0 = cv2.resize(image_0, (image_1_dimensions[0], image_1_dimensions[1]))

            image = cv2.addWeighted(image_0, 0.5, image_1, 0.5, 0)

    cv2.imwrite(f"{cluster_path}/subcluster{subcluster_count}.png", image)
    print("Layered image finished")

def parse_results(results):
    variants = [
        {
            'identifier': '8nqXhdl3JD8u',
            'data': []
        },
        {
            'identifier': 'hwVB0eKUehxy',
            'data': []
        },
        {
            'identifier': 'vtc5qYP2r8Ut',
            'data': []
        }
    ]

    for result in results:
        for variant in variants:
            result_variant = result['variant']

            if variant['identifier'] == result_variant:
                variant['data'].append(
                    {
                        'session_start': result['session_start']['seconds'],
                        'session_end': result['session_end']['seconds'],
                        'elapsed_time': result['session_end']['seconds'] - result['session_start']['seconds']
                    }
                )

    return variants
        # session_start = result['session_start']
        # session_end = result['session_end']
        # print(session_start, session_end, variant)


if __name__ == "__main__":
    f = open('results.json', 'r')
    results = json.loads(f.read())
    f = open('parsed_results.json', 'x')
    json.dump(parse_results(results), f)
    # overlay_images()
    # Eventually write out full procedure here
