# -*- coding: utf-8 -*-
import json
import logging
import re

from bs4 import Comment

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class YukiNovelCrawler(Crawler):
    base_url = 'https://yukinovel.id/'

    def initialize(self):
        self.home_url = 'https://yukinovel.id/'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url.replace(
            'https://yukinovel.me', 'https://yukinovel.id')
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = "Translated by Yukinovel"
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.lightnovel-thumb img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select('div.lightnovel-episode ul li a')

        chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.entry-content.cl')

        for d in contents.findAll('div'):
            d.extract()
        # end for

        for comment in contents.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()
        # end for

        if contents.findAll('p')[0].text.strip().startswith('Bab'):
            chapter['title'] = contents.findAll('p')[0].text.strip()
            contents.findAll('p')[0].extract()
        else:
            chapter['title'] = chapter['title']
        # end if

        logger.debug(chapter['title'])

        return str(contents)
    # end def
# end class
