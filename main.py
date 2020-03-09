import datetime
import json
from shutil import copyfile

import requests
from tld import get_tld

from config.app import STORAGE_LOGS_PATH, QUERY_START_PATH, CLUSTER_DATA_PATH
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

DONE - 3. Take screenshot of DataUrl from that query
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


"""
General URL format:
<domain_name>.<tld>


Domain edge cases:
Case one: <domain_name>.<tld> - count = 1
Case two: <subdomain_name>.<domain_name>.<tld> - count = 2
Case three: <subdomain_name>.<domain_name>.<tld>.<geo> - count = 3
Case four: <domain_name>.<tld>.<geo> - count = 2

If count is only one, then the domain can be stored under that key in some array using array element 0.
If count is two, check for presence of TLD; if TLD is of last array element, then subdomain exists; else sort by domain name
If count is three, subdomain-domain

"""


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

    """
    Unique identification process:
    1. Run preliminary check; if the length of the values attached to the key is equal to one, then add that to unique domains, and move on to next element
    2. If the length of the values is greater than 1, run image similarity check
        - Start at element of index 0 in the values. Compare that to element index + 1, and continue doing that.
          If their similarity threshold is less than 10-15, keep the element with the higher ranking (site_id). Remove other element from array.
          Move to next elements.
          Continue through the elements until either there are no more similarities through image algo or until one element remains.
    """
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
        log.write(f"Domain {domain}")
        site = session.query(Site).filter_by(host=domain).first()
        screenshot = session.query(Screenshot).filter_by(type=ScreenshotEnum.GREYSCALE,
                                                         site_id=site.id).first()
        copyfile(screenshot.path, f"{CLUSTER_DATA_PATH}/{site.name}.png")
        print(f"Copied greyscale screenshot to {CLUSTER_DATA_PATH}/{site.name}.png")
        log.write(f"Copied greyscale screenshot to {CLUSTER_DATA_PATH}/{site.name}.png")
    f.close()
    print("Finished copying screenshots")
    log.write("Finished copying screenshots")
    log.close()


"""
To create a site object:
fields(name, host)

Given a parsed response in the form of fields(url):
  - Split up the URL by it's root and subdomain, as well as TLD
  - Use the root domain for base name, and use subdomain with replaced period delimiter as hyphen (ex. status.romansorin.com becomes name=status-romansorin)
  - Figure out an efficient way to sort and search the root domains
  - If root domain is equal to another root domain, flag it; eventually compare the screenshot of two sites; if they are below some threshold of similarity (such as 10) then only use the response that is ranked higher
  - set url = host
  
  
  Comparison is only necessary when a key in the delimited list has a count of two or more
"""

"""
Screenshot

- Go to failed and exceeded jobs; take manual shots if necessary

Then run RGB->greyscale conversion
Then run image similarity algorithm
^^ Processing checks
"""

"""
For screenshots:
: foreach sites as site :
  - Navigate to site.host
  - Take screenshot (fullpage)
  - Convert to greyscale rgb
  - Make any comparisons as necessary
"""

# Next step: Parse unique domains log, foreach domain copy greyscale image (do a join) to cluster_data folder
# Also import clustering

if __name__ == "__main__":
    copy_unique_screenshots()
