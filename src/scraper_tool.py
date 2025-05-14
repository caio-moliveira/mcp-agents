from fastmcp import FastMCP
from bs4 import BeautifulSoup
import requests
import time

mcp = FastMCP("scraper-server")


def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    product_name = soup.find("h1", class_="ui-pdp-title").get_text(strip=True)
    prices = soup.find_all("span", class_="andes-money-amount__fraction")
    old_price = int(prices[0].get_text(strip=True).replace(".", ""))
    new_price = int(prices[1].get_text(strip=True).replace(".", ""))
    installment_price = int(prices[2].get_text(strip=True).replace(".", ""))

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "product_name": product_name,
        "old_price": old_price,
        "new_price": new_price,
        "installment_price": installment_price,
        "timestamp": timestamp,
    }


@mcp.tool()
def check_price(url: str) -> dict:
    html = requests.get(url).text
    return parse_page(html)


if __name__ == "__main__":
    mcp.run()
