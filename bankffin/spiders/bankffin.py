import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankffin.items import Article


class bankffinSpider(scrapy.Spider):
    name = 'bankffin'
    start_urls = ['https://bankffin.kz/ru/articles?year=2000&month=1']

    def parse(self, response):
        now = datetime.now()
        current_year = int(now.strftime("%Y"))
        year = 2000
        month = 1
        while year < current_year:
            while month <= 12:
                link = f'https://bankffin.kz/ru/articles?year={year}&month={month}'
                yield response.follow(link, self.parse_month)
                month += 1
            year += 1
            month = 1


    def parse_month(self, response):
        links = response.xpath('//h3/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//section[@class="article"]/h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="date"]/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//section[@class="article"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content[2:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
