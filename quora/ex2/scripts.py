import json
import time

from quora.scrapers import Quora


class Ex2(Quora):
    interval = 600

    def loop(self, function):
        print('Loop interval set at {} seconds.'.format(self.interval))
        while True:
            try:
                function()
            except Exception as e:
                print(str(e))
            time.sleep(self.interval)

    def collect(self):
        print('Collecting... ', end='', flush=True)
        data = self.get_all_topics_data()
        print('Ok. ', end='', flush=True)
        filename = 'quora/ex2/data/{}.json'.format(time.strftime('%Y-%m-%d_%H:%M:%S'))
        with open(filename, 'w', encoding='utf8') as fp:
            json.dump(data, fp, sort_keys=True, indent=2)
        print('File saved: {}'.format(filename))
        return filename

    def run_collect(self):
        self.loop(self.collect)
