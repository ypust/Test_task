import argparse
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()
parser.add_argument('-url', type=str, help='set URL')
args = parser.parse_args()


class UrlAnalyzer:
    def __new__(cls, *args, **kwargs):
        analyzer = super().__new__(cls)
        if not args and not kwargs:
            analyzer.url = cls.user_input()
        return analyzer

    def __init__(self, url=None):
        if url:
            self.url = url

    @classmethod
    def user_input(cls):
        if args.url:
            return args.url
        else:
            return input('Set URL for parsing: ')


url_analyzer = UrlAnalyzer()
response = requests.get(url_analyzer.url)

if response.status_code == 200:
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')

    links = soup.find_all('a')
    for link in links:
        link_url = link.get('href')
        if link_url:
            try:
                if link_url.startswith("/"):
                    link_url = url_analyzer.url + link_url

                link_response = requests.get(link_url)
                if link_response.status_code == 200:
                    with open('correct_links.txt', "a") as valid_file:
                        valid_file.write(f"{link_url}\n")
                else:
                    with open('broken_links.txt', "a") as broken_file:
                        broken_file.write(f"{link_url}\n")
            except requests.exceptions.RequestException as e:
                with open('broken_links.txt', "a") as broken_file:
                    broken_file.write(f"{link_url}\n")
        else:
            print('Cannot open the page. Status code:', response.status_code)
else:
    print('Cannot open the page. Status code:', response.status_code)
