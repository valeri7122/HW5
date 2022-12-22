import platform
import aiohttp
import asyncio
from datetime import datetime, timedelta
import sys
import json

pb_site = "https://api.privatbank.ua/p24api/exchange_rates?json&date="


class CurrencyHandler:
    def __init__(self, date):
        self.date = date

    async def currencyhandler(self, result):
        list = result["exchangeRate"]
        date_currency = {}
        for el_list in list:
            if el_list["currency"] in ("USD", "EUR"):
                currency = {
                    el_list["currency"]: {
                        "sale": el_list["saleRate"],
                        "purchase": el_list["purchaseRate"],
                    }
                }
                date_currency.update(currency)
        date_data = {self.date: date_currency}
        return date_data

    async def main(self):
        http = f"{pb_site}{self.date}"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(http) as response:
                    if response.status == 200:
                        result = await response.json()
                        res = await self.currencyhandler(result)
                        return res
                    else:
                        print(f"Error status: {response.status} for {http}")
            except aiohttp.ClientConnectorError as err:
                print(f"Connection error: {http}", str(err))


class DateHandler:
    def __init__(self, max=10, size=int(sys.argv[1])):
        self.max_days_interval = max
        self.arch_size = size

    async def delta(self, date):
        currencyhandler = CurrencyHandler(date)
        currency = await currencyhandler.main()
        return currency

    async def main(self):
        current_list = []
        current_date = datetime.now().date()
        for i in range(0, self.arch_size):
            if i < self.max_days_interval:
                days_interval = timedelta(days=i)
                past_date = current_date - days_interval
                str_past_date = past_date.strftime("%d.%m.%Y")
                dt = await self.delta(str_past_date)
                current_list.append(dt)
        jsd = json.dumps(current_list, indent=4)
        with open("data.json", "w") as fh:
            fh.write(jsd)
        return jsd


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    d_handler = DateHandler()
    print(asyncio.run(d_handler.main()))
