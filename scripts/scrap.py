import json
import requests
from bs4 import BeautifulSoup
from pprint import pprint
from proxychange import ProxyChanger
import time


class APILogger:
    def print_log(self, msg):
        print(f"[Instagram API] {msg}")


class InstagramScraper(object):

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                          'AppleWebKit/537.11 (KHTML, like Gecko) '
                          'Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'
        }
        self.discovered_hashtags = set()
        self.already_checked = set()
        # Let's try not use any proxies
        # self.proxy_changer = ProxyChanger()
        # self.current_proxy = self.proxy_changer.actual_proxy
        self.number_of_requests = 0
        self.logger = APILogger()

    def __request_url(self, link):
        for attempt in range(10):
            try:
                if self.number_of_requests == 50:
                    self.logger.print_log(f'Did 50 requests, going to sleep for 15 secs...')
                    time.sleep(15)
                    self.number_of_requests = 0
                response = requests.get(
                    link,
                    timeout=4,
                    headers=self.headers,
                ).text
                self.number_of_requests += 1
            except requests.HTTPError:
                self.logger.print_log(f'HTTP error.')
            except requests.RequestException:
                self.logger.print_log(f'RequestException.')
            except Exception as e:
                self.logger.print_log(f'__request_url error: {e}')
            else:
                return response
        self.logger.print_log(f'ERROR! Max attempts. Raising error')
        raise

    # def __request_url_proxy(self, link):
    #     for attempt in range(10):
    #         try:
    #             if self.number_of_requests == 50:
    #                 self.proxy_changer.set_new_proxy()
    #                 self.current_proxy = self.proxy_changer.actual_proxy
    #                 self.number_of_requests = 0
    #             response = requests.get(
    #                 link,
    #                 timeout=4,
    #                 headers=self.headers,
    #                 proxies={
    #                     'http': self.current_proxy,
    #                     'https': self.current_proxy}
    #             ).text
    #             self.number_of_requests += 1
    #         except requests.HTTPError:
    #             print("HTTP error, getting new proxy")
    #             self.proxy_changer.set_new_proxy()
    #             self.current_proxy = self.proxy_changer.actual_proxy
    #         except requests.RequestException:
    #             print('RequestException, getting new proxy')
    #             self.proxy_changer.set_new_proxy()
    #             self.current_proxy = self.proxy_changer.actual_proxy
    #         except Exception as e:
    #             print("__request_url error: ", e)
    #             self.proxy_changer.set_new_proxy()
    #             self.current_proxy = self.proxy_changer.actual_proxy
    #         else:
    #             print("Got response using proxy: ", self.current_proxy)
    #             return response
    #     print("ERROR! Max attempts.")
    #     raise

    @staticmethod
    def extract_json_data(html):
        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body')
        script_tag = body.find('script')
        raw_string = script_tag.text.strip().replace(
            'window._sharedData =', '').replace(';', '')
        return json.loads(raw_string)

    def get_current_profile_info(self, username):
        try:
            link = f"https://www.instagram.com/{username}/"
            response = self.__request_url(link)
            json_data = self.extract_json_data(response)
        except Exception as e:
            raise e
        else:
            profile_page_metrics = self.profile_page_metrics(json_data)
            profile_page_recent_posts = self.profile_page_recent_posts(json_data)
            return profile_page_metrics, profile_page_recent_posts

    def profile_page_metrics(self, json_data_from_profile):
        results = {}
        metrics = json_data_from_profile['entry_data']['ProfilePage'][0]['graphql']['user']
        for key, value in metrics.items():
            if key != 'edge_owner_to_timeline_media':
                if value and isinstance(value, dict):
                    value = value['count']
                    results[key] = value
                elif value:
                    results[key] = value
        return results

    def profile_page_recent_posts(self, json_data_from_profile):
        results = []
        metrics = \
            json_data_from_profile['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media'][
                "edges"]
        for node in metrics:
            node = node.get('node')
            if node and isinstance(node, dict):
                results.append(node)
        return results

    def discover_posts(self, hashtag):
        # get id to posts. Then we can get posts and their accounts.
        results = []
        try:
            response = self.__request_url(f"https://www.instagram.com/explore/tags/{hashtag}/")
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_top_posts'][
                "edges"]
        except Exception as e:
            raise e
        else:
            for node in metrics:
                node = node.get('node')
                if node and isinstance(node, dict):
                    results.append(node['shortcode'])
        return results

    def get_account_name_from_post(self, post_id):
        try:
            response = self.__request_url(f"https://www.instagram.com/p/{post_id}/")
            json_data = self.extract_json_data(response)
            username = json_data['entry_data']['PostPage'][0]['graphql']['shortcode_media']['owner']['username']
            return username
        except Exception as e:
            raise e

    def discover_accounts_from_hashtag(self, hashtag):
        posts_ids = self.discover_posts(hashtag)
        usernames = []
        for post_id in posts_ids:
            usernames.append(self.get_account_name_from_post(post_id))
        return set(usernames)

    def __get_connected_hashtags(self, current_hashtag):
        results = []
        try:
            response = self.__request_url(f"https://www.instagram.com/explore/tags/{current_hashtag}/")
            json_data = self.extract_json_data(response)
            metrics = json_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_related_tags'][
                "edges"]
        except Exception as e:
            raise e
        else:
            for node in metrics:
                node = node.get('node')
                if node and isinstance(node, dict):
                    results.append(node['name'])
        return results

    def get_category_hashtags(self, current_hashtag, deepth):
        if deepth == 0:
            return
        if current_hashtag not in self.already_checked:
            new_hashtags = self.__get_connected_hashtags(current_hashtag)
            self.discovered_hashtags.update(new_hashtags)
            for hashtag in new_hashtags:
                self.get_category_hashtags(hashtag, deepth - 1)
                self.already_checked.update(hashtag)

    def discover_hashtags(self, firsthashtag):
        self.logger.print_log(f"Discovering hashtags from {firsthashtag}")
        self.discovered_hashtags = set()
        self.already_checked = set()
        self.get_category_hashtags(firsthashtag, 2)
        new_hashtags = list(self.discovered_hashtags)
        return new_hashtags
