import requests
from bs4 import BeautifulSoup
import csv
import json
#from itertools import chain'

main_page = 'Repository URL'
page_url = 'Webpage to scrape'
bs_parser = 'lxml'
headers = ['dc.description.uri', 'dc.contributor.advisor', 'dc.contributor.author', 'dc.date.available', 'dc.date.issued', 'dc.title']
keys = ['URL', 'advisor', 'author', 'published_at', 'created_at', 'title']

def get_page(page):
    try:
        response = requests.get(page)
        if response.status_code == 200:
            return BeautifulSoup(response.text, bs_parser)
    except Exception as e:
        pass
    return None

def extract_artifacts_metadata(artifacts_links):
    artifact_information = []
    for artifact_link in artifacts_links:
        soup = get_page(artifact_link)
        metadata = {'url' : artifact_link}
        if soup:
            advisors = soup.find_all('meta', {'name': 'DC.contributor'})
            if advisors:
                if len(advisors) > 1:
                    metadata['advisor'] = '|'.join([advisor['content'].strip() for advisor in advisors])
                else:
                    metadata['advisor'] = soup.find('meta', {'name': 'DC.contributor'})['content'].strip()
            else:
                metadata['advisor'] = ''
            authors = soup.find_all('meta', {'name': 'DC.creator'})
            if len(authors) > 1:
                metadata['author'] = '|'.join([author['content'].strip() for author in authors])
            else:
                metadata['author'] = soup.find('meta', {'name': 'DC.creator'})['content'].strip()
            metadata['published_at'] = soup.find('meta', {'name': 'DCTERMS.available'})['content']
            metadata['created_at'] = soup.find('meta', {'name': 'DCTERMS.issued'})['content']
            metadata['title'] = soup.find('meta', {'name': 'DC.title'})['content'].strip()
            artifact_information.append(metadata)
    return artifact_information

def extract_artifacts_links(page):
    links = []
    while page:
        print(page)
        soup = get_page(page)
        if soup:
            ul = soup.find('ul', class_='ds-artifact-list')
            if not ul:
                return links
            for li in ul.find_all('li'):
                a = li.find('a', href=True)
                if a:
                    artifact_link = main_page + a['href']
                    links.append(artifact_link)
            if not soup.find('li', class_='next'):
                break
            next_page = soup.find('li', class_='next')
            if next_page:
                a = next_page.find('a', href=True)
                if a['href'] != '':
                    offset = a['href'].find('?')
                    page = page_url + a['href'][offset:]
                else:
                    break
    return links

def write_artifacts_to_csv(filename, headers, rows):
    with open(filename, 'w', newline='') as csvFile:
        data_writer = csv.writer(csvFile)
        data_writer.writerow(headers)
        for row in rows:
            data_writer.writerow([row['url'], row['advisor'], row['author'], row['published_at'], row['created_at'], row['title']])

def write_artifacts_to_json(filename, keys, rows):
    with open(filename, 'w', encoding='utf8') as jsonFile:
        json.dump(rows, jsonFile, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    from time import time
    start = time()

    artifacts_links = extract_artifacts_links(page_url)
    print(len(artifacts_links), ' artifacts links found.')

    artifacts_metadata = extract_artifacts_metadata(artifacts_links)
    #print(len(list(chain(*artifacts_metadata))), ' artifacts metadata found.')
    print(artifacts_metadata)

    filename = 'metadata.csv'
    write_artifacts_to_csv(filename, headers, artifacts_metadata)
    #write_artifacts_to_json(filename, keys, artifacts_metadata)

    print('Finished in ', time() - start, ' seconds.')
