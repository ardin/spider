# Linear spider

## Overview
Linear spider checks website, searching error pages (e.g. http 500) and reports slow loading pages.


### Getting it

To download linear-spider, either fork this github repo or simply use Pypi via pip.
```sh
$ pip install linear-spider
```

### Using it

<pre>
$ linear-spider -h
usage: linear-spider [-h] url

Linear Spider

positional arguments:
  url         Checked site

optional arguments:
  -h, --help  show this help message and exit
</pre>

## Example output

Below is example working program (interrupted after few second).

<pre>
$ linear-spider https://www.linkedin.com
+ https://www.linkedin.com 200 0.62s
+ https://www.linkedin.com/psettings/guest-controls?trk=uno-reg-guest-home-guest-controls 200 0.73s
+ https://www.linkedin.com/psettings/guest-email-unsubscribe?trk=hb_ft_gunsub 200 0.54s
+ https://www.linkedin.com/pulse/discover?trk=hb_ft_influencers 200 0.95s
+ https://www.linkedin.com/secure/settings 404 0.53s
+ https://www.linkedin.com/advertising?src=en-all-el-li-hb_ft_ads&trk=hb_ft_ads 200 1.63s
+ https://www.linkedin.com/sitemap 404 0.46s
+ https://www.linkedin.com/marketing-solutions/targeting 404 0.48s
+ https://www.linkedin.com/marketing-solutions/financial-services-marketing 404 0.41s
+ https://www.linkedin.com/marketing-solutions/campaigns-and-advocacy 404 0.42s
+ https://www.linkedin.com/marketing-solutions/higher-education 404 0.44s
+ https://www.linkedin.com/marketing-solutions/technology-marketing 404 0.6s
+ https://www.linkedin.com/marketing-solutions/marketing-strategy?u=0#webinars 404 0.54s
+ https://www.linkedin.com/marketing-solutions/advertising-faqs 404 0.42s
+ https://www.linkedin.com/marketing-solutions/sophisticated-marketers-sessions 404 0.49s
+ https://www.linkedin.com/marketing-solutions/company-pages/showcase-pages 404 0.56s
+ https://www.linkedin.com/talent-solutions/company-career-pages 404 0.48s
+ https://www.linkedin.com/marketing-solutions/company-pages/best-practices 404 0.49s
+ https://www.linkedin.com/marketing-solutions/certified-marketing-partners 404 0.49s
+ https://www.linkedin.com/marketing-solutions/marketing-agencies 404 0.51s
^CPerformance report:
-------------------

Site: https://www.linkedin.com

Checked: 20
Remained: 75
Http codes:
- 200: 5
- 404: 15

Slow responces (1-2s):
- https://www.linkedin.com/advertising?src=en-all-el-li-hb_ft_ads&trk=hb_ft_ads 1.63s

</pre>

