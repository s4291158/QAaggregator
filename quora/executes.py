from pprint import pprint

from .parsers import int_parser
from .scrapers import Quora, bs
import matplotlib.pyplot as plt
import json
import matplotlib.patches as mpatches
from scipy import stats
import math
import numpy as np


class CheckInvalidLinks(Quora):
    def determine_valid_topic(self, url):
        self.soup = bs(self.session.get(url + '/top_questions').text)
        containers = self.soup.select('.feed_item')
        if not containers:
            return False
        return True

    def check_invalid_links_in_topic(self):
        topics = self.get_top_50_topics_2015()
        invalid_topics = []
        print('Checking {} topics for invalid links: '.format(len(topics)), end='', flush=True)
        for topic_name, topic_link in topics.items():
            if not self.determine_valid_topic(topic_link):
                invalid_topics.append(topic_name)
            print('█', end='', flush=True)
        print('\nFollowing topic links are invalid: {}'.format(invalid_topics))


class Main(Quora):
    def execute(self):
        self.winners = []
        topics = self.get_top_50_topics_2015()
        print('Scraping {} topics: '.format(len(topics)), end='', flush=True)
        for topic_name, topic_link in topics.items():
            self.get_questions_on_topic(topic_link)
            print('█', end='', flush=True)
        print('\n{} questions scored above requirement.'.format(len(self.winners)))
        input("Press Enter to show results.")
        pprint(self.winners)


class Ex1(Quora):
    def get_answers_on_question(self, url):
        soup = bs(self.session.get(url).text)
        containers = soup.select('.Answer.AnswerBase')
        view_data = []
        for container in containers:
            try:
                view_count = container.find('span', class_='meta_num').text
            except AttributeError:
                view_data.append('0')
            else:
                view_data.append(view_count)
        data = self.get_question_data(url, soup)
        data['present_answer_count'] = len(containers)
        data['present_answer_view_count'] = view_data
        return data

    def execute(self):
        topics = self.get_top_50_topics_2015()
        data_set = []
        print('Scraping {} topics: '.format(len(topics)), end='', flush=True)
        for topic_name, topic_link in topics.items():
            soup = bs(self.session.get(topic_link).text)
            containers = soup.select('.QuestionText')
            for container in containers:
                try:
                    link = container.find('a', class_='question_link').get('href')
                except AttributeError:
                    print(container)
                else:
                    q_data = self.get_answers_on_question(self.get_url(link))
                    data_set.append(q_data)
            print('█', end='', flush=True)
        print('\n')
        with open('quora/ex1/p1/data_set.json', 'w', encoding='utf8') as fp:
            json.dump(data_set, fp, sort_keys=True, indent=2)
        return data_set

    @staticmethod
    def calculate_entry_score(data):
        pa_data = data.get('present_answer_view_count')
        pa_count = data.get('present_answer_count')
        if pa_count:
            return sum([int_parser(i) for i in pa_data]) / pa_count
        return 0

    @staticmethod
    def sort_key(data):
        return int_parser(data.get('view_count'))

    @staticmethod
    def normalise(data_set):
        return [data / max(data_set) for data in data_set]

    def get_x_y_dataset(self):
        with open('quora/ex1/p1/data_set.json', 'r') as fp:
            data_set = json.load(fp)
        x = []
        y = []
        for data in data_set:
            x.append(self.calculate_entry_score(data))
            y.append(int_parser(data.get('view_count')))
        return np.array(x), np.array(y), data_set

    def plot_from_file(self):
        x, y, data_set = self.get_x_y_dataset()
        plt.scatter(x, y)
        plt.show()

    def calculate_p_value(self):
        x, y, data_set = self.get_x_y_dataset()
        correlation, _ = stats.pearsonr(x, y)
        return correlation
