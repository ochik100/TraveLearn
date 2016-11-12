from scrapy.contrib.spiders import CrawlSpider
from items import StateItem, StateTopicItem, PostItem
import scrapy


class StateCrawlSpider(CrawlSpider):
    name = "forum"
    allowed_domains = ['tripadvisor.com']
    # ['https://www.tripadvisor.com/ListForums-g191-i3-United_States.html']
    start_urls = ['https://www.tripadvisor.com/ShowForum-g28926-i29-California.html']
    custom_settings = {
        'BOT_NAME': 'tripadvisor',
        'DOWNLOAD_DELAY': 5
    }
    base_url = 'https://www.tripadvisor.com{}'
    # def parse(self, response):
    #     for info in response.css("table.forumtopic tr")[1:]:
    #         # html = info.extract()
    #         # soup = BeautifulSoup(html, 'html.parser')
    #         state = StateItem()
    #         state['state'] = info.css('tr a::text').extract_first()
    #         state[
    #             'url'] = 'https://www.tripadvisor.com{}'.format(info.css('tr a::attr(href)').extract_first())
    #         state['num_topics'] = info.css('td.top::text').extract_first()
    #         state['num_posts'] = info.css('td.pos::text').extract_first()
    #         request = scrapy.Request(state['url'], callback=self.parse_state_topics)
    #         request.meta['state'] = state['state']
    #         yield request

    def parse(self, response):
        state = "California"
        for info in response.css('table.topics tr')[1:]:
            state_topic = StateTopicItem()
            state_topic['topic'] = info.css('b a::text').extract_first().strip()
            state_topic[
                'topic_url'] = self.base_url.format(info.css('b a::attr(href)').extract_first())
            # state_topic['creator'] = info.css('div.bymember a::text').extract_first()
            state_topic['state'] = state
            request = scrapy.Request(state_topic['topic_url'], callback=self.parse_posts)
            request.meta['state'] = state_topic['state']
            request.meta['topic'] = state_topic['topic']
            yield request

        next_page = response.css('div.pgLinks a::attr(href)')
        if next_page:
            url = self.base_url.format(next_page[-1].extract())
            yield scrapy.Request(url, callback=self.parse)

    def parse_posts(self, response):
        state = response.meta['state']
        topic = response.meta['topic']
        for info in response.css('div.post'):
            post = PostItem()
            post['state'] = state
            post['topic'] = topic
            # post['user'] = info.css('div.username span::text').extract_first()
            post['user'] = info.css('div.username a::attr(href)').extract_first().split('/')[-1]
            post['date_time'] = info.css('div.postDate::text').extract_first()
            post['user_location'] = info.css('div.location::text').extract_first()
            post['text'] = " ".join(info.css('div.postBody p::text').extract())
            yield post

        next_page = response.css('div.pgLinks a::attr(href)')
        if next_page:
            url = self.base_url.format(next_page[-1].extract())
            request = scrapy.Request(url, callback=self.parse_posts)
            request.meta['state'] = state
            request.meta['topic'] = topic
            yield request
