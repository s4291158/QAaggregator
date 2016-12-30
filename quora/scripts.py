from .scrapers import Quora, bs
import time
import json


class CheckInvalidLinks(Quora):
    def determine_valid_topic(self, url):
        soup = bs(self.session.get(url).text)
        containers = soup.select('.QuestionText')
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


class Loop:
    interval = 600

    def loop(self, function):
        print('Loop interval set at {} seconds.'.format(self.interval))
        while True:
            try:
                function()
            except Exception as e:
                print(str(e))
            time.sleep(self.interval)


class Main(Loop, Quora):
    def collect(self):
        print('Collecting... ', end='', flush=True)
        data = self.get_all_topics_data()
        print('Ok. ', end='', flush=True)
        filename = 'quora/data/{}.json'.format(time.strftime('%Y-%m-%d_%H:%M:%S'))
        with open(filename, 'w', encoding='utf8') as fp:
            json.dump(data, fp, sort_keys=True, indent=2)
        print('File saved: {}'.format(filename))
        return filename

    def run_collect(self):
        self.loop(self.collect)

    def find_winners(self, stream=True):
        self.stream = stream
        self.winners = []
        topics = self.get_top_50_topics_2015()
        print('Scraping {} topics: '.format(len(topics)), end='', flush=True)
        if stream:
            print('')
        for topic_name, topic_link in topics.items():
            self.get_questions_data_on_topic(topic_link)
            if not stream:
                print('█', end='', flush=True)
        print('\n{} questions scored above requirement.'.format(len(self.winners)))
        if not stream:
            input("Press Enter to show results.")
            print(self.winners)
