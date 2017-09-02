#!/usr/bin/env python

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

results={}
queue=[]
user_agent="Mozilla/5.0 (X11; U; Linux i686; pl; rv:1.8.1.4) Gecko/20070705 Firefox/2.0.0.4"
status_r={}


def validate_url(url):
    if not validators.url(url):
        print bcolors.FAIL + "Error: url is not valid." + bcolors.ENDC
        exit(1)


def save_report(info=False, summary=False):

    if info: 
        print "INFO: checked: {0}, remained: {1}" .format( str(len(results)), str(len(queue)))

    # make directories
    u = urlparse(url)
    workdir = os.getenv("HOME") + "/spider/" + u.netloc + "/" + datetime.today().strftime('%Y-%m-%d_%H') + "/"
    report_txt = workdir + "report.txt"
    if not os.path.exists(workdir):
        os.makedirs(workdir)
    
    # save report
    f = open(report_txt,'w')
    f.write("Performance report:\n")
    f.write("-------------------\n\n")
    f.write("Site: " + url + "\n\n")
    f.write("Checked: " + str(len(results)) + "\n")
    f.write("Remained: " + str(len(queue)) + "\n")
    f.write("Http codes:\n")

    # all codes
    for key in sorted(status_r):
	f.write( "- " + str(key) + ": " + str(status_r[key]) + "\n")

    # detailed wrong codes
    header = 0
    for key in status_r:
	if int(key) >= 500:

	    # show header if needed
	    if header == 0:
	       f.write( "\nWrong http codes:\n")
	       header = 1

	    # show link
	    for k in results:
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


def search_links():
    url = queue[-1]

    # main
    if url not in results and validators.url(url):

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
            queue.remove(url)
            return False
 
	# set color 
        if exec_time < 1: 
	    color = bcolors.ENDC
	elif exec_time >= 1 and exec_time < 2:
	    color = bcolors.WARNING
        else:
            color = bcolors.FAIL

	# show message
	print color + "+ {0} {1} {2}s" . format(url,r.status_code,exec_time) + bcolors.ENDC

        if r.status_code not in status_r:
            status_r[r.status_code] = 1
        else:
            status_r[r.status_code] = status_r[r.status_code] + 1
   
        html_page = r.text
    
        results[url] = { 'time': round(time.time()-start_time,2), 'code': r.status_code, 'header': r.headers }
        soup = BeautifulSoup(html_page)
        for link_r in soup.findAll('a'):
            link = link_r.get('href')
            search = False

            try:
                if re.search(r'^'+url,str(link)):
                    search = True
                    # print "DEBUG 1: " + link
                    # time.sleep(1)
                elif re.search(r'^//',str(link)):
                    search = False
                    # print "DEBUG 2: " + link
                    # time.sleep(1)
                elif re.search(r'^/',str(link)):
                    search = True
                    link = host + link
                    # print "DEBUG 3: " + link
                    # time.sleep(1)
                else:
                    search = False
            except Exception as e:
                print bcolors.WARNING + "Warning: " + str(e) + bcolors.ENDC
                search = False
   			
            # add to queue
            if search is True and link not in queue and link not in results: 

                if validators.url(link):
                    queue.append(link)
                    # print "+ {0}".format(link)
                else:
                    print bcolors.WARNING + "Warning: can't add element into list {0}". format(link) + bcolors.ENDC

        queue.remove(url)

        # save after x requests
        if len(results)%50 == 0:
            save_report(info=True)

def signal_handler(signal, frame):
    save_report(summary=True)
    sys.exit(0)

parser = argparse.ArgumentParser(description='Linear Spider')
parser.add_argument('url', help='Checked site')
args = parser.parse_args()

url = args.url
validate_url(url)
signal.signal(signal.SIGINT, signal_handler)

# first run
if len(queue)==0 and len(results)==0:
    queue.append(url)

while len(queue)>0:
    search_links()

save_report(info=False, summary=True)

