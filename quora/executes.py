from pprint import pprint

from .scrapers import Quora, bs


class CheckInvalidLinks(Quora):
    def determine_valid_topic(self, url):
        soup = bs(self.session.get(url + '/top_questions').text)
        containers = soup.select('.feed_item')
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
