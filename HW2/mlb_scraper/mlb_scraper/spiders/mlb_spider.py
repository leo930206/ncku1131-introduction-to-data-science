import scrapy

class MlbSpider(scrapy.Spider):
    name = 'mlb_spider'
    allowed_domains = ['mlb.com']
    start_urls = ['https://www.mlb.com/stats/']

    def parse(self, response):
        # 保存網頁內容到 debug.html，方便檢查
        with open("debug.html", "wb") as f:
            f.write(response.body)

        # 爬取當前頁面的所有球員數據
        players = response.css('table.stats-table tbody tr')
        for player in players:
            player_name = player.css('td[data-col="player"] a::text').get()
            avg = player.css('td[data-col="avg"]::text').get()
            hr = player.css('td[data-col="hr"]::text').get()
            rbi = player.css('td[data-col="rbi"]::text').get()

            # 打印球員名字以確認是否成功抓取
            print("Player Name:", player_name)

            yield {
                'Player': player_name,
                'AVG': avg,
                'HR': hr,
                'RBI': rbi,
                # 添加其他指標，如果需要的話
            }

        # 找到 "下一頁" 的按鈕並繼續爬取
        next_page = response.css('a.pagination-btn-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
