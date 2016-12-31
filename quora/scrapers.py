import json
import os
from urllib import parse

import requests
from bs4 import BeautifulSoup

from local_settings import M_S


def _find(function, default):
    try:
        return function()
    except Exception:
        return default


def bs(text):
    return BeautifulSoup(text, 'lxml')


class URLMixin:
    URL = 'https://www.quora.com/'

    def get_url(self, *args):
        return parse.urljoin(self.URL, os.path.join(*args))


class Top50in2015(URLMixin):
    def get_top_50_topics_2015(self):
        with open('quora/topics.json', 'r') as fp:
            return json.load(fp)

    def scrape_top_50_topics_2015(self):
        unusual_links = {
            "Dating and Relationships": "https://www.quora.com/topic/Dating-and-Relationships-1",
            "Google (company)": "https://www.quora.com/topic/Google-company-5",
            "Fashion and Style": "https://www.quora.com/topic/Fashion-and-Style-1",
        }
        topics = {}
        url = 'https://www.quora.com/What-were-the-most-followed-topics-on-Quora-in-2015'
        soup = bs(requests.get(url).text)
        containers = soup.select('.qlink_container')[2:]
        for container in containers:
            topic_name = container.find('a').text.strip()
            if topic_name in unusual_links:
                topic_link = unusual_links[topic_name]
            else:
                topic_link = self.get_url('topic', topic_name.replace(' ', '-').replace('(', '').replace(')', ''))
            topics[topic_name] = topic_link
        with open('quora/topics.json', 'w', encoding='utf8') as fp:
            json.dump(topics, fp, sort_keys=True, indent=2)


class Login(URLMixin):
    session = requests.session()

    def __init__(self, login=True):
        if login:
            self.cookie_login()
            assert self.is_logged_in()
            print('Log in successful')
        else:
            print('No attempts to login')

    def cookie_login(self):
        self.session.cookies['m-s'] = M_S

    def is_logged_in(self):
        response = self.session.get(self.get_url('api', 'logged_in_user'))
        if response.status_code == 200 and len(response.text) > 9:
            return True
        return False


class AnswerData:
    @staticmethod
    def get_answer_view_count(container):
        return _find(
            lambda: container.find('span', class_='meta_num').text,
            '0'
        )

    @staticmethod
    def get_answer_upvote_count(container):
        return _find(
            lambda: container.find('a', class_='Upvote').find('span', class_='count').text,
            '0'
        )

    @staticmethod
    def get_answer_comment_count(container):
        return _find(
            lambda: container.find('a', class_='view_comments').find('span', class_='count').text,
            '0'
        )

    @staticmethod
    def get_answer_timestamp(container):
        return _find(
            lambda: container.find('div', class_='CredibilityFacts').find('a', class_='answer_permalink').text,
            ''
        )

    @staticmethod
    def get_answer_user(container):
        return _find(
            lambda: container.find('a', class_='user').text,
            'Anonymous'
        )


class QuestionData(Login, AnswerData):
    @staticmethod
    def get_follow_count(soup):
        return _find(
            lambda: soup.find('a', class_='secondary_action').find('span', class_='count').text,
            '0'
        )

    @staticmethod
    def get_comment_count(soup):
        return _find(
            lambda: soup.select('.view_comments')[0].find('span', class_='count').text,
            '0'
        )

    @staticmethod
    def get_answer_count(soup):
        return _find(
            lambda: soup.select('.answer_count')[0].answer_dom.text.split(' ')[0],
            '0'
        )

    @staticmethod
    def get_title(soup):
        return _find(
            lambda: soup.select('.question_text_edit')[0].find('span', class_='rendered_qtext').text,
            'Undefined title'
        )

    @staticmethod
    def get_detail(soup):
        return _find(
            lambda: soup.select('.question_details')[0].find('span', class_='rendered_qtext').text,
            ''
        )

    @staticmethod
    def get_view_count(soup):
        return _find(
            lambda: soup.select('.ViewsRow')[0].view_dom.text.split(' ')[0],
            '0'
        )

    @staticmethod
    def get_timestamp(soup):
        return _find(
            lambda: soup.select('.AskedRow')[0].text.replace('Last Asked ', ''),
            ''
        )

    def get_answers_data(self, soup):
        containers = soup.select('.Answer.AnswerBase')
        view_data = []
        for container in containers:
            data = {
                'view_count': self.get_answer_view_count(container),
                'upvote_count': self.get_answer_upvote_count(container),
                'comment_count': self.get_answer_comment_count(container),
                'timestamp': self.get_answer_timestamp(container),
                'user': self.get_answer_user(container)
            }
            view_data.append(data)
        return view_data

    def get_question_data(self, url, soup=None):
        soup = soup or bs(self.session.get(url).text)
        try:
            data = {
                'follow_count': self.get_follow_count(soup),
                'comment_count': self.get_comment_count(soup),
                'answer_count': self.get_answer_count(soup),
                'view_count': self.get_view_count(soup),
                'title': self.get_title(soup),
                'detail': self.get_detail(soup),
                'timestamp': self.get_timestamp(soup),
                'top_answers': self.get_answers_data(soup),
                'url': url
            }
        except Exception as e:
            print(url)
            raise e
        return data


class Quora(QuestionData, Top50in2015, URLMixin):
    winners = []
    stream = False

    def get_all_topics_data(self):
        topics = self.get_top_50_topics_2015()
        topics_data = []
        for topic_name, topic_link in topics.items():
            try:
                questions_data = self.get_questions_data_on_topic(topic_link)
            except Exception:
                continue
            topics_data.extend(questions_data)
        return topics_data

    def get_questions_data_on_topic(self, url):
        soup = bs(self.session.get(url + '/top_questions').text)
        containers = soup.select('.QuestionText')
        questions_data = []
        for container in containers:
            link = container.find('a', {'class': 'question_link'}).get('href')
            try:
                data = self.get_question_data(self.get_url(link))
            except Exception:
                continue
            self.algo(data)
            questions_data.append(data)
        return questions_data

    def algo(self, data):
        # v = int_parser(data['view_count'])
        # a = int_parser(data['answer_count'])
        # if a <= 5 and v >= 5000:
        #     self.winners.append(data)
        #     if self.stream:
        #         print(data)
        return data
