from fastapi import HTTPException
from lxml import etree

from src.cache import cache
from src.dependencies import fetch
from src.models import Index


@cache(expire=15, market_closed_expire=3600)
async def scrape_indices() -> list[Index]:
    """
    Scrape the major world indices from investing.com

    :raises HTTPException: with status code 500 if an error occurs while scraping
    """
    url = 'https://www.investing.com/indices/major-indices'

    html = await fetch(url=url)
    return await get_indices(html)


async def get_indices(html) -> list[Index]:
    """
    Parse the HTML content and return a list of Index objects
    :param html: the HTML content

    :raises HTTPException: with status code 500 if an error occurs while parsing
    """
    try:
        tree = etree.HTML(html)
        table_xpath = './/tbody'
        row_xpath = './/tr'
        name_xpath = './/td[2]//span[@dir="ltr"]/text()'
        value_xpath = './/td[3]/span/text()'
        change_xpath = './/td[6]/text()'
        percent_change_xpath = './/td[7]/text()'
        table = tree.xpath(table_xpath)[0]
        rows = table.xpath(row_xpath)
        indices = []
        for row in rows:
            name = row.xpath(name_xpath)[0].strip()
            value = float(row.xpath(value_xpath)[0].replace(',', ''))
            change = row.xpath(change_xpath)[0].strip()
            percent_change = row.xpath(percent_change_xpath)[0].strip()

            index_data = Index(
                name=name,
                value=value,
                change=change,
                percent_change=percent_change,
            )
            indices.append(index_data)

        return indices
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse indices: {str(e)}")
