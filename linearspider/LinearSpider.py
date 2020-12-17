#!/usr/bin/env python3

import argparse
import validators
import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
import time
import os
from datetime import datetime
import signal
import sys
import urllib3
from base64 import b64encode

from requests.packages.urllib3.exceptions import InsecureRequestWarning

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC = '\033[0m'


class LinearSpider(object):

    def __init__(self):

        parser = argparse.ArgumentParser(description='Linear Spider')
        parser.add_argument('-H', '--header', action='append', nargs='*', help='send this HTTP header '
                                                                               '(you can specify several)')
        parser.add_argument('--debug', action="store_true")
        parser.add_argument('-C', '--credentials', help='provide credentials for basic authentication (user:pass)')
        parser.add_argument('url', help='Checked site')
        args = parser.parse_args()

        self.debug = False
        self.results = {}
        self.queue = 0
        self.checked = 0
        self.status_r = {}
        self.now = datetime.today().strftime('%Y-%m-%d_%H')
        self.url = args.url
        self.base_url = args.url
        self.headers = {}

        # set debug
        self.debug = args.debug

        # set headers
        if args.header:
            for h in args.header:
                n=h[0].split(':')
                if len(n) == 2:
                    k = n[0].strip()
                    if n[0].lower().strip() == 'user-agent':    # overwrite if needed
                        k = 'User-Agent'
                    v = n[1].strip()

                    self.headers[k] = v
                    if self.debug:
                        print('DEBUG: setting header: "%s: %s"' % (k, v))

        # set default user-agent
        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = 'Mozilla/5.0 (X11; U; Linux i686; pl; rv:1.8.1.4) Gecko/20070705 ' \
                                         'Firefox/2.0.0.4 (linear)'

        # set credentials
        if args.credentials:
            credentials = args.credentials.split(':')
            if len(credentials) == 2:
                user_pass = b64encode(args.credentials.encode('utf-8')).decode("ascii")
                self.headers['Authorization'] = 'Basic %s' % user_pass
                if self.debug:
                    print('DEBUG: setting header "Authorization: Basic %s"' % user_pass)

        # check url
        self.validate_url(self.url)

        signal.signal(signal.SIGINT, self.signal_handler)

        u = urllib3.util.parse_url(self.url)
        self.workdir = os.getenv("HOME") + "/.linear-spider/" + u.netloc + "/" + self.now + "/"

        # first run
        if len(self.results) == 0:
            self.results[self.url] = {'code': 0, 'time': 0}
            self.queue = 1

        while self.queue > 0:
            for url in list(self.results):
                if self.results[url]['code'] == 0:
                    self.search_links(url)

        self.save_report(info=False, summary=True)

    def test(self,t):
        print(t)

    def validate_url(self, url):
        if not validators.url(url):
            print(bcolors.FAIL + "Error: url is not valid." + bcolors.ENDC)
            exit(1)

    def save_report(self, info=False, summary=False):

        if info:
            print("INFO: all results: {0}, checked: {1}, queue: {2}" .format(str(len(self.results)), str(self.checked),
                                                                             str(self.queue)))

        # make directories
        report_txt = self.workdir + "report.txt"
        if not os.path.exists(self.workdir):
            os.makedirs(self.workdir)

        # save report
        f = open(report_txt,'w')
        f.write("Performance report:\n")
        f.write("-------------------\n\n")
        f.write("Site: " + self.base_url + "\n\n")
        f.write("All pages: " + str(len(self.results)) + "\n")
        f.write("Checked: " + str(self.checked) + "\n")
        f.write("Queue: " + str(self.queue) + "\n")
        f.write("Http codes:\n")

        # all codes
        for key in sorted(self.status_r):
            f.write( "- " + str(key) + ": " + str(self.status_r[key]) + "\n")

        # detailed wrong codes
        header = 0
        for key in self.status_r:
            if int(key) >= 400:

                if header == 0:
                    f.write( "\nWrong http codes:\n")
                    header = 1

                # show link
                for k in self.results:
                    if self.results[k]['code']:
                        if int(self.results[k]['code']) == key:
                            f.write("- " + str(k) + " " + str(self.results[k]['code']) + "\n")

        # slow responses
        header = 0
        for k in self.results:
            if self.results[k]['time'] >= 1 and self.results[k]['time'] < 2:
                if header == 0:
                    f.write( "\nSlow responses (1-2s):\n")
                    header = 1
                f.write("- " + str(k) + " " + str(self.results[k]['time']) + "s\n")

        # critical responses
        header = 0
        for k in self.results:
            if self.results[k]['time'] > 2:
                if header == 0:
                    f.write( "\nVery slow responses (more than 2s):\n")
                    header = 1
                f.write("- " + str(k) + " " + str(self.results[k]['time']) + "s\n")
        f.flush()
        f.close()

        if summary:
            file = open(report_txt, "r")
            print(file.read())
            print(report_txt)

        if self.debug:
            print("DEBUG: results: {0} , queue: {1}" .format(str(len(self.results)), str(sys.getsizeof(self.results))))

    def search_links(self, url):
        self.queue = self.queue - 1
        self.checked = self.checked + 1

        stime = time.time()
        if validators.url(url) and self.results[url]['code'] == 0:
            start_rtime = time.time()

        u = urllib3.util.parse_url(url)
        host = u.scheme + "://" + u.netloc
        try:
            start_time = time.time()
            s = requests.Session()
            r = s.get(url, headers=self.headers, verify=False, timeout=5)
            exec_time = round(time.time()-start_time,2)

        except Exception as e:
            print(bcolors.FAIL + "Error: can't fetch " + url + bcolors.ENDC)
            if 598 not in self.status_r:
                self.status_r[598] = 1
            else:
                self.status_r[598] = self.status_r[598] + 1

            self.results[url] = {'code': '598', 'time': 0, 'message': str(e)}
            return False

        request_time = round(time.time()-start_rtime,4)

        # set color
        if exec_time < 1:
            color = bcolors.ENDC
        elif exec_time >= 1 and exec_time < 2:
            color = bcolors.WARNING
        else:
            color = bcolors.FAIL

        # show message
        print(color + "+ {0} {1} {2}s" . format(url, r.status_code, exec_time) + bcolors.ENDC)

        start_stime = time.time()
        if r.status_code not in self.status_r:
            self.status_r[r.status_code] = 1
        else:
            self.status_r[r.status_code] = self.status_r[r.status_code] + 1

        html_page = r.text

        self.results[url] = {'time': round(time.time()-start_time, 2), 'code': r.status_code, 'header': r.headers }
        status_time = round(time.time()-start_stime, 4)

        start_soup_time = time.time()
        strainer = SoupStrainer('a')
        soup = BeautifulSoup(html_page.encode('ascii', 'ignore'), 'html.parser', parse_only=strainer)
        soup_time_2 = round(time.time()-start_soup_time, 4)

        for link_r in soup.findAll('a'):
            link = link_r.get('href')
            search = False
            start_soup_search_time = time.time()
            try:
                if re.search(r'^'+url,str(link)):
                    search = True
                elif re.search(r'^//',str(link)):
                    search = False
                elif re.search(r'^/',str(link)):
                    search = True
                    link = host + link
                else:
                    search = False
            except Exception as e:
                print(bcolors.WARNING + "Warning: " + str(e) + bcolors.ENDC)
                search = False

            soup_search_time = round(time.time()-start_soup_search_time,4)

            # add to queue
            start_soup_queue_time = time.time()
            if search is True:
                if link not in self.results:

                    if validators.url(link):
                        self.results[link] = {'code': 0, 'time': 0}
                        self.queue += 1

                    soup_queue_append_time = round(time.time()-start_soup_queue_time,4)
                    if self.debug:
                        print("DEBUG: link: " + str(link) + " soup_queue_append_time " +  str(soup_queue_append_time) + " " + str(search))

            soup_queue_time = round(time.time()-start_soup_queue_time,4)

        del soup
        del html_page

        soup_time = round(time.time()-start_soup_time, 4)

        # save after x requests
        if self.checked%100 == 0:
            self.save_report(info=True)

        function_time = round(time.time()-stime, 4)
        if self.debug:
            print("DEBUG: function time: {0}" . format(function_time))
            print("DEBUG: request time: {0}" . format(request_time))
            print("DEBUG: status time: {0}" . format(status_time))
            print("DEBUG: soup time: {0}" . format(soup_time))
            print("DEBUG: soup time 2: {0}" . format(soup_time_2))
            print("\n")

    def signal_handler(self, signal, frame):
        self.save_report(summary=True)
        sys.exit(0)


if __name__ == "__main__":
    spider = LinearSpider()
