import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup
from robobrowser import RoboBrowser

from local_settings import M_S


class Quora:
    URL = 'https://www.quora.com/'
    session = requests.session()
    winners = []

    def __init__(self, login=True):
        if login:
            self.cookie_login()
            assert self.is_logged_in()
            print('log in successful')
        else:
            print('no attempts to login')

    def get_url(self, *args):
        return self.URL + '/'.join(args)

    def cookie_login(self):
        self.session.cookies['m-s'] = M_S

    def is_logged_in(self):
        response = self.session.get(self.get_url('api', 'logged_in_user'))
        if response.status_code == 200 and len(response.text) > 9:
            return True
        return False

    def get_question_data1(self, url):
        soup = BeautifulSoup(self.session.get(url).text, 'lxml')

        follow_dom = soup.select('.secondary_action')[0]
        follow_count = int(follow_dom.find('span', {'class': 'count'}).text)

        try:
            comment_dom = soup.select('.view_comments')[0]
            comment_count = int(comment_dom.find('span', {'class': 'count'}).text.replace('+', ''))
        except (AttributeError, IndexError):
            comment_count = 0

        try:
            answer_dom = soup.select('.answer_count')[0]
            answer_count = int(answer_dom.text.split(' ')[0])
        except (AttributeError, IndexError):
            answer_count = 0

        question_dom = soup.select('.question_qtext')[0]
        question = question_dom.find('span', {'class': 'rendered_qtext'}).text

        detail_dom = soup.select('.question_details')[0]
        detail = detail_dom.find('span', {'class': 'rendered_qtext'}).text

        view_dom = soup.select('.ViewsRow')[0]
        view_count = int(view_dom.text.replace(',', '').split(' ')[0])

        last_asked_dom = soup.select('.AskedRow')[0]
        last_asked_time = last_asked_dom.text.replace('Last Asked ', '')

        data = {
            'follow_count': follow_count,
            'comment_count': comment_count,
            'answer_count': answer_count,
            'view_count': view_count,
            'question': question,
            'detail': detail,
            'last_asked': last_asked_time,
            'url': url
        }
        data['score'] = self.calculate_score(data)
        return data

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
        soup = BeautifulSoup(self.session.get(url).text, 'lxml')
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

    def get_all_questions_on_topic(self, url, commit=True):
        soup = BeautifulSoup(self.session.get(url + '/top_questions').text, 'lxml')
        containers = soup.select('.feed_item')
        if not containers:
            return False

        if commit:
            for container in containers:
                link = container.find('a', {'class': 'question_link'}).get('href')
                self.get_question_data1(self.get_url(link))
        return True

    def calculate_score(self, data):
        score = data['follow_count'] / (data['answer_count'] + 1)
        if score >= 5:
            self.winners.append(data)
        return score

    def check_invalid_links_in_topic(self):
        topics = self.get_top_50_topics_2015()
        invalid_topics = []
        print('Checking {} topics for invalid links: '.format(len(topics)), end='', flush=True)
        for topic_name, topic_link in topics.items():
            if not self.get_all_questions_on_topic(topic_link, False):
                invalid_topics.append(topic_name)
            print('█', end='', flush=True)
        print('\nFollowing topic links are invalid: {}'.format(invalid_topics))

    def script(self):
        topics = self.get_top_50_topics_2015()
        print('Scraping {} topics: '.format(len(topics)), end='', flush=True)
        for topic_name, topic_link in topics.items():
            self.get_all_questions_on_topic(topic_link)
            print('█', end='', flush=True)
        print('\n{} questions scored above requirement.'.format(len(self.winners)))
        input("Press Enter to show results.")
        pprint(self.winners)
