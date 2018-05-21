# -*- coding: utf-8 -*-
import json
import re
import time

import scrapy


class PagesSpider(scrapy.Spider):
    name = 'pages'
    text = 'coca%20cola'

    cookies_str = 'BX=bbsjn6ldfoffj&b=3&s=pb; xb=387571; sm-news-messaging=1; ' \
                  'localization=en-us%3Bua%3Bua; ' \
                  'adCounter=7; ' \
                  'flrbp=1526911704-960290634f92df19f51f39d9a04b8e5791a8ca3c; ' \
                  'flrbs=1526911704-c782e6c934cf9a4f0c411f63d85dc5786e85835c; ' \
                  'flrbgrp=1526911704-d13f91cd536b33d7acbcf9e8a60971c504ff95bd; ' \
                  'flrbgdrp=1526911704-3585b8159be4b497dd8889134daa7a2053beb419; ' \
                  'flrbgmrp=1526911704-5b147ed16735a08d790d6b1afa1f75c943491a2c; ' \
                  'flrbcr=1526911704-bf8812540063a37bdf70c5077ef65d1cc780703f; ' \
                  'flrbrst=1526911704-814b6036a043916672f38a85281f42a8c7d60d13; ' \
                  'flrtags=1526911704-2b8a0292816221e463ebbc1f860f8f5d560fe6dc; ' \
                  'flrbrp=1526911704-87af494ed0cf134aab82e34c57c1e6236d8db447; ' \
                  'flrb=16; vp=563%2C536%2C1.600000023841858%2C15%2Csearch-photos-everyone-view%3A546'

    urlt = 'https://api.flickr.com/services/rest?sort=relevance&parse_tags=1&' \
           'content_type=7&extras=can_comment%2Ccount_comments%2Ccount_faves%2Cdescription%2C' \
           'isfavorite%2Clicense%2Cmedia%2Cneeds_interstitial%2Cowner_name%2Cpath_alias%2Crealname%2C' \
           'rotation%2Curl_c%2Curl_l%2Curl_m%2Curl_n%2Curl_q%2Curl_s%2Curl_sq%2Curl_t%2Curl_z&' \
           'per_page=25&page=1&lang=en-US&' \
           'text=' + text + '&' \
                            'viewerNSID=&method=flickr.photos.search&csrf=&' \
                            'format=json&hermes=1&hermesClient=1&reqId=19c7c50a&nojsoncallback=1'

    @staticmethod
    def parse_cookies(cookie: str) -> dict:
        cookie = cookie.split(':')[-1]
        q = {k.strip(): v for k, v in re.findall(r'(.*?)=(.*?);', cookie)}
        return q

    def start_requests(self):
        yield scrapy.Request('https://www.flickr.com/search/?text=' + self.text)

    def parse(self, response):
        html = response.body.decode('utf-8')
        a = re.search('root.YUI_config.flickr.api.site_key = "(\w+)"', html)
        api_key = a.group(1)

        print('api_key = ' + api_key)

        self.cookies = self.parse_cookies(self.cookies_str)

        t = time.time()
        while t >= 946684800:
            u = self.urlt + '&api_key=' + api_key
            # + ('&max_taken_date=%s' % t)
            t -= 3600 * 24 * 30

            yield response.follow(u, self.parse_page,
                                  cookies=self.cookies,
                                  headers={'referer': 'https://www.flickr.com/search/?text=coca%20cola'})

    def parse_page(self, response):
        js = json.loads(response.body_as_unicode())
        photos_obj = js.get('photos', {})
        pages_count = int(photos_obj.get('pages', 0))
        current_page = int(photos_obj.get('page', 0))

        photo_obj = photos_obj.get('photo', [])

        print('current page: %s/%s ' % (current_page, pages_count))
        print('total photos: %s' % photos_obj.get('total', 0))
        print('photos on page: %s ' % len(photo_obj))
        print()

        urls = ''
        for photo in photo_obj:
            url = photo.get('url_l_cdn')
            if url is None:
                url = photo.get('url_l')
            if url is None:
                url = photo.get('url_c_cdn')
            if url is None:
                url = photo.get('url_c')
            if url is None:
                url = photo.get('url_m_cdn')
            if url is None:
                url = photo.get('url_m')

            if url is None:
                continue

            urls += url + '\n'

        with open('images.list', 'a') as f:
            f.write(urls)

        for p in range(current_page, pages_count + 1):
            u = re.sub('&page=\d+', '&page=%s' % p, response.url)
            yield response.follow(u, self.parse_page)
