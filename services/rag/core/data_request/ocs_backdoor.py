import requests
import uuid
import time
from random import randint
import re

from typing import Dict
from .const import LAW_CATEGORY_MAPPER, THAI_ALPHABET

def generate_years():
    """Generates a list of integers representing years from 1900 to 2024 in descending order."""
    years = []
    for year in range(2024, 1900, -1):
        years.append(year)
    years.append(0)
    return years

def get_ocs_law(category: str, alphabet: str = "ก") -> Dict[str, object]:
    assert category in LAW_CATEGORY_MAPPER, f"Invalid category: {category}. We only support {LAW_CATEGORY_MAPPER}."
    
    if "," in category:
        api_url = "https://www.ocs.go.th/ocs-api/public/browse/searchByCharCate"
        service_name = "searchPublicByCharCate"
        query = {
                'categories': category,
                'charCategory': alphabet,
                'indexAndLawCategoryIds': [],
                }
    else:
        api_url = "https://www.ocs.go.th/ocs-api/public/browse/searchByYear"
        service_name = "searchPublicByYear"
        query = {
                'categories': category,
                "years":generate_years(),
                'indexAndLawCategoryIds': [],
                }

    cookies = {
        'acceptCookie': 'Y',
        'GUEST_LANGUAGE_ID': 'en_US',
        '_gid': 'GA1.3.1473032187.1714029339',
        '_ga': 'GA1.1.489217970.1704361137',
        '_ga_EC2H0L05D5': f'GS1.1.1714034051.33.1.{int(time.time())}.0.0.0',
        '_ga_L1JHZPNWY6': f'GS1.1.1714034051.33.1.{int(time.time())}.0.0.0',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://www.ocs.go.th',
        'Referer': 'https://www.ocs.go.th/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
    }

    json_data = {
        'reqHeader': {
            'reqId': str(int(time.time() * 1000)),
            'reqChannel': 'WEB',
            'reqDtm': f'{time.strftime("%Y-%m-%d %H:%M:%S.")}{randint(100,999)}', #2024-04-25 15:40:19.890
            'reqBy': 'unknow',
            'serviceName': service_name,
            'uuid': str(uuid.uuid4()),
            'sessionId': str(uuid.uuid4()),
        },
        'reqBody': {
            'pagination': {
                'currentPage': 1,
                'pageSize': 999,
            },
            'orderResult': [
                {
                    'orderBy': 'indexNameTh',
                    'orderDir': 'asc',
                },
                {
                    'orderBy': 'lawCategoryNameTh',
                    'orderDir': 'asc',
                },
                {
                    'orderBy': 'lawNameTh',
                    'orderDir': 'asc',
                },
            ],
        },
    }
    
    json_data["reqBody"]["query"] = query
    
    response = requests.post(
        api_url,
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    
    text = response.text
    text = re.sub("false", "False", text)
    text = re.sub("true", "True", text)
    jsonfile = eval(text)
    
    assert isinstance(jsonfile, dict), f"Invalid response type: {type(jsonfile)}."
    return jsonfile