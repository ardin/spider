#!/usr/bin/env python

# author: piotr@wasilewski.org.pl

import argparse
import validators
import requests
from BeautifulSoup import BeautifulSoup
from  urlparse import urlparse
import re
import time
import os
from datetime import datetime
import signal
import sys

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

requests.packages.urllib3.disable_warnings()

debug=False
results={}
queue=0
checked=0
user_agent="Mozilla/5.0 (X11; U; Linux i686; pl; rv:1.8.1.4) Gecko/20070705 Firefox/2.0.0.4"
status_r={}
now=datetime.today().strftime('%Y-%m-%d_%H')

def validate_url(url):
    if not validators.url(url):
        print bcolors.FAIL + "Error: url is not valid." + bcolors.ENDC
        exit(1)


def save_report(info=False, summary=False):

    if info:
        print "INFO: all results: {0}, checked: {1}, queue: {2}" .format( str(len(results)), str(checked), str(queue))

    # make directories
    report_txt = workdir + "report.txt"
    if not os.path.exists(workdir):
        os.makedirs(workdir)

    # save report
    f = open(report_txt,'w')
    f.write("Performance report:\n")
    f.write("-------------------\n\n")
    f.write("Site: " + url + "\n\n")
    f.write("All pages: " + str(len(results)) + "\n")
    f.write("Checked: " + str(checked) + "\n")
    f.write("Queue: " + str(queue) + "\n")
    f.write("Http codes:\n")

    # all codes
    for key in sorted(status_r):
	f.write( "- " + str(key) + ": " + str(status_r[key]) + "\n")

    # detailed wrong codes
    header = 0
    for key in status_r:
        if int(key) >= 400:

            if header == 0:
                f.write( "\nWrong http codes:\n")
                header = 1

            # show link
            for k in results:
                if results[k]['code']:
                    if int(results[k]['code']) == key:
                        f.write("- " + str(k) + " " + str(results[k]['code']) + "\n")

    # slow responces
    header = 0
    for k in results:
        if results[k]['time'] >= 1 and results[k]['time'] < 2:
            if header == 0:
                f.write( "\nSlow responces (1-2s):\n")                                                                                  
                header = 1
            f.write("- " + str(k) + " " + str(results[k]['time']) + "s\n")

    # critical responces
    header = 0
    for k in results:
        if results[k]['time'] > 2:
            if header == 0:
                f.write( "\nVery slow responces (more than 2s):\n")
                header = 1
            f.write("- " + str(k) + " " + str(results[k]['time']) + "s\n")

    f.flush()
    f.close()

    if summary:
        file = open(report_txt, "r")
        print file.read()
        print report_txt

    if debug:
        print "DEBUG: results: {0} , queue: {1}" .format( str(len(results)), str(sys.getsizeof(results) ) )


def search_links(url):

    global queue
    global checked
    queue = queue - 1
    checked = checked + 1

    stime = time.time()
    if validators.url(url) and results[url]['code']==0:

        start_rtime = time.time()

	u = urlparse(url)
	host = u.scheme + "://" + u.netloc
        headers = {'user-agent': user_agent}
        try:
            start_time = time.time()
            s = requests.Session()
            r = s.get(url, headers=headers, verify=False, timeout=5)
            exec_time = round(time.time()-start_time,2)

        except Exception as e:
            print bcolors.FAIL + "Error: can't fetch " + url + bcolors.ENDC
            if 598 not in status_r:
                status_r[598] = 1
            else:
                status_r[598] = status_r[598] + 1

            results[url] = { 'code': '598', 'time': 0, 'message': str(e) }
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
	print color + "+ {0} {1} {2}s" . format(url,r.status_code,exec_time) + bcolors.ENDC

        start_stime = time.time()
        if r.status_code not in status_r:
            status_r[r.status_code] = 1
        else:
            status_r[r.status_code] = status_r[r.status_code] + 1

        html_page = r.text

        results[url] = { 'time': round(time.time()-start_time,2), 'code': r.status_code, 'header': r.headers }
        status_time = round(time.time()-start_stime,4)

        start_soup_time = time.time()
        soup = BeautifulSoup(html_page.encode('ascii','ignore'))
        soup_time_2 = round(time.time()-start_soup_time,4)

        for link_r in soup.findAll('a'):

            start_soup_getlink_time = time.time()
            link = link_r.get('href')
            soup_getlink_time = round(time.time()-start_soup_getlink_time,4)

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
                print bcolors.WARNING + "Warning: " + str(e) + bcolors.ENDC
                search = False

            soup_search_time = round(time.time()-start_soup_search_time,4)

            # add to queue
            start_soup_queue_time = time.time()
            if search is True:
                if link not in results:

                    if validators.url(link):
                        results[link] = { 'code': 0, 'time': 0 }
                        queue+=1

                    soup_queue_append_time = round(time.time()-start_soup_queue_time,4)
                    if debug:
                        print "DEBUG: link: " + str(link) + " soup_queue_append_time " +  str(soup_queue_append_time) + " " + str(search)

            soup_queue_time = round(time.time()-start_soup_queue_time,4)

        del soup
        del html_page

        soup_time = round(time.time()-start_soup_time,4)

        # save after x requests
        if checked%100 == 0:
            save_report(info=True)

        function_time = round(time.time()-stime,4)
        if debug:
          print "DEBUG: function time: {0}" . format(function_time)
          print "DEBUG: request time: {0}" . format(request_time)
          print "DEBUG: status time: {0}" . format(status_time)
          print "DEBUG: soup time: {0}" . format(soup_time)
          print "DEBUG: soup time 2: {0}" . format(soup_time_2)
          print "\n"

def signal_handler(signal, frame):
    save_report(summary=True)
    sys.exit(0)

parser = argparse.ArgumentParser(description='Linear Spider')
parser.add_argument('url', help='Checked site')
args = parser.parse_args()

url = args.url
validate_url(url)
signal.signal(signal.SIGINT, signal_handler)

u = urlparse(url)
workdir = os.getenv("HOME") + "/spider/" + u.netloc + "/" + now + "/"

# first run
if len(results)==0:
    results[url] = { 'code': 0, 'time': 0 }
    queue=1

while queue>0:
  for url in results.keys():
    if results[url]['code']==0:
      search_links(url)

save_report(info=False, summary=True)

