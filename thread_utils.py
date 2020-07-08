'''
PartsGenie (c) GeneGenie Bioinformatics Ltd. 2020

All rights reserved.

@author:  neilswainston
'''
# pylint: disable=too-few-public-methods
from threading import Thread
from utils import job_utils


class AbstractThread(job_utils.JobThread):
    '''An AbstractThread base class.'''

    def __init__(self, query):
        job_utils.JobThread.__init__(self)

        self._query = query
        self._results = []

    def _fire_designs_event(self, status, iteration, message=''):
        '''Fires an event.'''
        event = {'update': {'status': status,
                            'message': message,
                            'progress': float(iteration) /
                            len(self._query['designs']) * 100,
                            'iteration': iteration,
                            'max_iter': len(self._query['designs'])},
                 'query': self._query
                 }

        if status == 'finished':
            event['result'] = self._results

        self._fire_event(event)


class ThreadPool(Thread):
    '''Basic class to run job Threads sequentially.'''

    def __init__(self, threads):
        self.__threads = threads
        Thread.__init__(self)

    def run(self):
        for thread in self.__threads:
            thread.start()
            thread.join()
