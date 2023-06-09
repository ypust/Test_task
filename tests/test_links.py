import logging
import pytest
import requests
from unittest.mock import patch
from fitz import fitz

from main import UrlAnalyzer, PdfUrlAnalyzer, HtmlUrlAnalyzer


class TestData:
    VALID_LINK_URL: str = 'https://makeup.com.ua'
    BROKEN_LINK_URL: str = 'https://makeup.com.ua/product/9w34/'
    MOCKED_LINKS = ['https://pypi.org/project/pytest-mock/', 'https://makeup.com.ua/categorys/202ds72/',
                    'https://www.programiz.com/']

    VALID_PDF_PATH: str = '../test_artifacts/links_example.pdf'
    INVALID_PDF_PATH: str = 'file_not_exists.pdf'
    EXPECTED_LINKS_FROM_PDF_FILE = ['https://pypi.org/project/pytest-mock/', 'https://www.programiz.com/',
                                    'https://www.programiz.com/python-programming/for-looping',
                                    'https://makeup.com.ua/categorys/202ds72/']


class TestURLAnalyzer:
    @pytest.mark.URLAnalyzer
    def test_valid_url_written_to_valid_links_file(self, mocker):
        analyzer = UrlAnalyzer([TestData.VALID_LINK_URL])
        expected_status_code_result = 200

        mock_response = requests.Response()
        mock_response.status_code = expected_status_code_result
        mocker.patch.object(requests, 'get', return_value=mock_response)

        with patch('builtins.open') as mock_file:
            analyzer.analyze()
            mock_file.assert_called_once_with('correct_links.txt', 'a')
            mock_file.return_value.__enter__.return_value.write.assert_called_once_with(f"{TestData.VALID_LINK_URL}\n")
            logging.info('test_valid_url_written_to_valid_links_file')

    @pytest.mark.URLAnalyzer
    @pytest.mark.parametrize("link, expected_status_code_result", [(TestData.BROKEN_LINK_URL, 404),
                                                                   (TestData.BROKEN_LINK_URL, 401),
                                                                   (TestData.BROKEN_LINK_URL, 500)])
    def test_broken_url_written_to_broken_links_file(self, mocker, link, expected_status_code_result):
        analyzer = UrlAnalyzer([link])

        mock_response = requests.Response()
        mock_response.status_code = expected_status_code_result
        mocker.patch.object(requests, 'get', return_value=mock_response)

        with patch('builtins.open') as mock_file:
            analyzer.analyze()
            mock_file.assert_called_once_with('broken_links.txt', 'a')
            mock_file.return_value.__enter__.return_value.write.assert_called_once_with(f"{link}\n")
            logging.info('test_broken_url_written_to_broken_links_file')

    @pytest.mark.URLAnalyzer
    @patch('builtins.open')
    def test_broken_url_not_written_to_valid_link_file(self, mock_open):
        broken_link = TestData.BROKEN_LINK_URL

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404
            analyzer = UrlAnalyzer([broken_link])
            analyzer.analyze()

        assert not mock_open.call_args.args[0] == 'correct_links.txt'
        logging.info('test_broken_url_not_written_to_valid_link_file')

    @pytest.mark.URLAnalyzer
    @patch('builtins.open')
    def test_valid_url_not_written_to_broken_link_file(self, mock_open):
        valid_link = TestData.VALID_LINK_URL

        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            analyzer = UrlAnalyzer([valid_link])
            analyzer.analyze()
        logging.info('test_broken_url_not_written_to_valid_link_file')
        assert not mock_open.call_args.args[0] == 'broken_links.txt'


class TestPDFFileLinksAnalyzer:

    @pytest.mark.PDFFileLinksAnalyzer
    # @pytest.mark.datafiles(TestData.VALID_PDF_PATH, relative=True)
    def test_extract_links_from_valid_file(self):
        analyzer = PdfUrlAnalyzer(TestData.VALID_PDF_PATH)

        extracted_links = analyzer._PdfUrlAnalyzer__extract_links_from_file(TestData.VALID_PDF_PATH)
        expected_links = TestData.EXPECTED_LINKS_FROM_PDF_FILE
        logging.info('test_extract_links_from_valid_file')

        assert extracted_links == expected_links

    @pytest.mark.PDFFileLinksAnalyzer
    def test_extract_links_from_invalid_file(self):
        invalid_file_path = TestData.INVALID_PDF_PATH

        with pytest.raises(Exception) as file_error:
            PdfUrlAnalyzer(file_path=invalid_file_path)
        logging.info('test_extract_links_from_invalid_file')
        assert file_error.type == fitz.fitz.FileNotFoundError


class TestHtmlUrlAnalyzer:

    @pytest.mark.HtmlUrlAnalyzer
    def test_extract_valid_url_links_from_page(self):
        url = TestData.VALID_LINK_URL
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = b'<a href="/link1">Link 1</a><a href="/link2">Link 2</a>'
            analyzer = HtmlUrlAnalyzer(url)
            links = analyzer._HtmlUrlAnalyzer__extract_links_from_page(url)

            logging.info('test_extract_valid_url_links_from_page')
            assert links == [url + '/link1', url + '/link2']

    @pytest.mark.HtmlUrlAnalyzer
    def test_extract_invalid_url_links_from_page(self):
        url = TestData.BROKEN_LINK_URL
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404
            analyzer = HtmlUrlAnalyzer(url)
            links = analyzer._HtmlUrlAnalyzer__extract_links_from_page(url)

            logging.info('test_extract_invalid_url_links_from_page')
            assert links == []

    @pytest.mark.HtmlUrlAnalyzer
    def test_normalize_href_attribute_relative_url(self):
        url = TestData.VALID_LINK_URL
        analyzer = HtmlUrlAnalyzer(url)
        link = {'href': '/relative-link'}
        normalized_link = analyzer._HtmlUrlAnalyzer__normalize_href_attribute(link)

        logging.info('test_normalize_href_attribute_relative_url')
        assert normalized_link == url + '/relative-link'

    @pytest.mark.HtmlUrlAnalyzer
    def test_normalize_href_attribute_absolute_url(self):
        url = TestData.VALID_LINK_URL
        analyzer = HtmlUrlAnalyzer(url)
        link = {'href': TestData.VALID_LINK_URL}
        normalized_link = analyzer._HtmlUrlAnalyzer__normalize_href_attribute(link)

        logging.info('test_normalize_href_attribute_absolute_url')
        assert normalized_link == TestData.VALID_LINK_URL
