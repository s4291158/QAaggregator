import json

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from ..parsers import int_parser
from ..scrapers import Quora, bs


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

    def developing_questions(self):
        topics = self.get_top_50_topics_2015()
        data_set = []
        print('Scraping {} topics: '.format(len(topics)), end='', flush=True)
        for topic_name, topic_link in topics.items():
            soup = bs(self.session.get(topic_link + '/top_questions').text)
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
        with open('quora/ex1/p2/data_set.json', 'w', encoding='utf8') as fp:
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

    def get_x_y_from_dataset(self, data_set):
        x = []
        y = []
        for data in data_set:
            x.append(self.calculate_entry_score(data))
            y.append(int_parser(data.get('view_count')))
        return np.array(x), np.array(y)

    def calculate_r(self):
        data_set = self.get_dataset()
        x, y = self.get_x_y_from_dataset(data_set)
        return stats.pearsonr(x, y)[0]

    def get_dataset(self):
        raise NotImplementedError('get_dataset is an abstract method')


class P1(Ex1):
    def get_dataset(self):
        with open('quora/ex1/p1/data_set.json', 'r') as fp:
            data_set = json.load(fp)
        return data_set

    def plot_from_file(self):
        data_set = self.get_dataset()
        x, y = self.get_x_y_from_dataset(data_set)
        plt.scatter(x, y)
        plt.show()


class P2(Ex1):
    def get_dataset(self):
        with open('quora/ex1/p2/data_set.json', 'r') as fp:
            data_set = json.load(fp)
        return data_set
