import argparse


class UrlAnalyzer:

    def __new__(cls, *args, **kwargs):
        analyzer = super().__new__(cls)
        if not args and not kwargs:
            analyzer.url = cls.user_input()
        return analyzer

    def __init__(self, url =None):
        if url:
            self.url = url

    @classmethod
    def user_input(cls):
        parse = argparse.ArgumentParser()
        parse.add_argument('-url', help='set URL')
        args = parse.parse_args()
        if args.url:
            return args.url
        else:
            url = input('Set URL for parsing: ')
            return url


if __name__ == "__main__":
    url = UrlAnalyzer('https://www.google.com/')
    print(url)
    # url_1 = UrlAnalyzer()
    # print(url_1)

