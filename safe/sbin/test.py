#!/usr/bin/python
import website

#test_site = website.website("test6.appcenter123.com")
#test_site.setup()
#test_site.start()
websites = website.get_all_websites()
for website in websites:
    try:
        website.start()
    except:
        print "Website", website.get_url(), "failed to start."
