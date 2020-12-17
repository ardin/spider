# Linear spider

## Overview
Linear spider checks website, searching error pages (e.g. http 500) and reports slow loading pages.


### Getting it

To download linear-spider, either fork this github repo or simply use Pypi via pip.
```sh
$ pip3 install linear-spider
```

### Using it

<pre>
$ linear-spider -h
usage: linear-spider [-h] [-H [HEADER ...]] [--debug] [-C CREDENTIALS] url

Linear Spider

positional arguments:
  url                   Checked site

optional arguments:
  -h, --help            show this help message and exit
  -H [HEADER ...], --header [HEADER ...]
                        send this HTTP header (you can specify several)
  --debug
  -C CREDENTIALS, --credentials CREDENTIALS
                        provide credentials for basic authentication (user:pass)

</pre>

## Example output

Below is example working program (interrupted after few second).

<pre>
$ linear-spider https://www.linkedin.com
+ https://www.linkedin.com 200 0.7s
+ https://www.linkedin.com/legal/cookie-policy 200 0.4s
+ https://www.linkedin.com/?trk=guest_homepage-basic_nav-header-logo 200 0.39s
+ https://www.linkedin.com/signup/cold-join?trk=guest_homepage-basic_nav-header-join 200 0.27s
+ https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin 200 0.29s
+ https://www.linkedin.com/uas/request-password-reset?trk=homepage-basic_signin-form_forgot-password-link 200 0.21s
+ https://www.linkedin.com/jobs/engineering-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.94s
+ https://www.linkedin.com/jobs/business-development-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.89s
+ https://www.linkedin.com/jobs/finance-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.71s
+ https://www.linkedin.com/jobs/administrative-assistant-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.74s
+ https://www.linkedin.com/jobs/retail-associate-jobs-brzegi?trk=homepage-basic_suggested-search 200 1.03s
+ https://www.linkedin.com/jobs/customer-service-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.75s
+ https://www.linkedin.com/jobs/operations-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.73s
+ https://www.linkedin.com/jobs/information-technology-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.78s
+ https://www.linkedin.com/jobs/marketing-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.67s
+ https://www.linkedin.com/jobs/human-resources-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.75s
+ https://www.linkedin.com/jobs/healthcare-services-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.67s
+ https://www.linkedin.com/jobs/sales-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.85s
+ https://www.linkedin.com/jobs/program-and-project-management-jobs-brzegi?trk=homepage-basic_suggested-search 200 0.79s
^CPerformance report:
-------------------

Site: https://www.linkedin.com

All pages: 116
Checked: 20
Queue: 96
Http codes:
- 200: 19

Slow responses (1-2s):
- https://www.linkedin.com/jobs/retail-associate-jobs-brzegi?trk=homepage-basic_suggested-search 1.03s

</pre>

