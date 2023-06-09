import argparse
import requests
from abc import ABC
import fitz
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, filename='parser_log.log', filemode='w',
                    format='%(asctime)s %(levelname)s %(message)s')


class UrlAnalyzer(ABC):
    def __init__(self, links):
        self._links = links

    def analyze(self):
        for link_url in self._links:
            try:
                link_response = requests.get(link_url)
                if link_response.status_code == 200:
                    self.__handle_valid_link(link_url)
                else:
                    self.__handle_invalid_link(link_url)
            except Exception:
                self.__handle_invalid_link(link_url)

    @staticmethod
    def __handle_valid_link(link_url):
        with open('correct_links.txt', "a") as valid_file:
            valid_file.write(f"{link_url}\n")
            logging.info(f'The valid link {link_url} was added to the correct_links.txt file.')

    @staticmethod
    def __handle_invalid_link(link_url):
        with open('broken_links.txt', "a") as broken_file:
            broken_file.write(f"{link_url}\n")
            logging.warning(f'The broken link {link_url} was added to the broken_links.txt file.')


class HtmlUrlAnalyzer(UrlAnalyzer):

    def __init__(self, url=None):
        if url:
            self.url = url
        super().__init__(self.__extract_links_from_page(self.url))

    def __normalize_href_attribute(self, link):
        target_url = link.get('href')
        if target_url.startswith("/"):
            target_url = self.url + target_url
        return target_url

    def __extract_links_from_page(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')
            page_links = list(soup.find_all('a'))
            return list(map(self.__normalize_href_attribute, page_links))
        else:
            logging.error(f'Cannot open the page. Status code:{response.status_code}')
            return []


class PdfUrlAnalyzer(UrlAnalyzer):

    def __init__(self, file_path=None):
        if file_path:
            self.file_path = file_path
        super().__init__(self.__extract_links_from_file(self.file_path))

    @staticmethod
    def __extract_links_from_file(file_path):
        links = []
        pdf = fitz.open(file_path)
        for page in pdf:
            page_links = page.get_links()
            for link in page_links:
                if link["uri"]:
                    links.append(link["uri"])
        pdf.close()
        return links


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str, default=None, help='set URL')
    parser.add_argument('--pdf', type=str, default=None, help='set PDF file')
    args = parser.parse_args()

    if args.url:
        url_analyzer = HtmlUrlAnalyzer(args.url)
        url_analyzer.analyze()
    elif args.pdf:
        pdf_analyzer = PdfUrlAnalyzer(args.pdf)
        pdf_analyzer.analyze()
    else:
        path = input('Set URL or PDF path for parsing: ')
        if path.endswith(".pdf"):
            pdf_analyzer = PdfUrlAnalyzer(path)
            pdf_analyzer.analyze()
        else:
            url_analyzer = HtmlUrlAnalyzer(path)
            url_analyzer.analyze()
