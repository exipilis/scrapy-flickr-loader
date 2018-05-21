# -*- coding: utf-8 -*-
from urllib.parse import urlparse

import os
import scrapy


class ImagesSpider(scrapy.Spider):
    name = 'images'

    @staticmethod
    def get_fn(image_url):
        """
        create file name from url
        all images should be stored in 'images/hostname' folder
        :param image_url: image url
        :return: file name
        """
        o = urlparse(image_url)
        fn = 'images/' + o.path.strip('/').replace('/', '_')
        return fn

    def start_requests(self):
        with open('images.list') as f:
            for url in f:
                url = url.strip()
                fn = self.get_fn(url)

                if os.path.isfile(fn):
                    continue

                d = os.path.dirname(fn)
                if not os.path.isdir(d):
                    os.makedirs(d)

                yield scrapy.Request(url, meta={'fn': fn})

    def parse(self, response):
        with open(response.meta['fn'], 'wb') as f:
            f.write(response.body)
