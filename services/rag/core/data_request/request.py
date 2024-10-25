from tqdm import tqdm
import requests
import re
from datetime import datetime
from typing import List
import logging

from .const import scrape_data_dir, config_path
from .utils import (
    convert_thai_num,
    normalize_space,
    normalize_newlines,
    replace_html_tags,
    add_space_subsection,
    delete_newline_subsection,
    clean_footnote,
    fix_newline_bug
)

class LawDocumentReader(object):
    
    def __init__(self) -> None:
        self.api_url = "https://www.ocs.go.th/ocs-api/public/doc/getLawDoc"
        
    def get_api_body(self, timeline_id: str, en: bool = False) -> dict:
        return {
            "reqHeader": {
                "reqId": round(datetime.now().timestamp()*1000),
                "reqChannel": "WEB",
                "reqDtm": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                "reqBy": "unknow",
                "serviceName": "getPublicLawDoc",
                "uuid": "2bf24529-c745-4978-81fb-8a38e2d9f70e",
                "sessionId": "ef9f249a-6ff3-4551-b3ca-9d3a84350e64"
            },
            "reqBody": {
                "isTransEng": en,
                "timelineId": timeline_id
            }
        }
        
    def process_content(self, content: str) -> str:
        # remove initial newlines from ocs
        content = re.sub(r"\n+", " ", content)
        
        # convert Thai number
        content = convert_thai_num(content)
        
        # replace initial html tag before subsection into newline
        content = re.sub(r">(\(\d+\))<", r">\n\1<", content)
        
        # hard code to format white space
        content = re.sub(r"<p style=\"text-indent:\d+(.\d+)?pt;?\">", "\n", content)
        
        # remove HTML tags
        # content = re.sub(r"<[^>]*>", "", content)
        # content = re.sub(r"<.*?>", "", content)
        
        content = replace_html_tags(content)
        
        # format special symbols
        content = re.sub(r"\“", '"', content)
        content = re.sub(r"\”", '"', content)
        
        # remove section reference note
        # content = re.sub(r"\[\*มาตรา.+\]", "", content)
        
        # clean footnote
        content = clean_footnote(content)

        # normalize space
        content = normalize_space(content)
        content = normalize_newlines(content)
        
        # prevent bug
        # content = add_space_subsection(content)
        # content = delete_newline_subsection(content)
        # content = fix_newline_bug(content)
        
        return content.strip()

    def get_page(self, url: str = '', urls: List[str] = [], en: bool = False, show_progress = False) -> List[dict]:
        
        
        # Use tqdm if show_progress is True; otherwise, iterate normally
        if url:
            urls = [url]
        iterator = tqdm(urls, desc="Requesting URLs", unit="doc", leave=True, ncols=100, colour='blue') if show_progress else urls

        responses = []
        for url in iterator:
            logging.info(f"get page from {url}")
            timeline_id = url.split("/")[-1].replace("%3D", "=")
            
            response = requests.post(
                self.api_url, 
                json=self.get_api_body(
                    timeline_id=timeline_id,
                    en=en
                )
            )
            
            if response.status_code != 200:
                raise ConnectionError(response.text)
            
            response = response.json()
            
            # clean content
            for section in response["respBody"]["lawSections"]:
                section["sectionContent"] = self.process_content(section["sectionContent"])
            
            responses.append(response)
            
        return responses
    
    def get_url_title(self, url: str, en: bool = False) -> str:
        timeline_id = url.split("/")[-1].replace("%3D", "=")
        
        response = requests.post(
            self.api_url, 
            json=self.get_api_body(
                timeline_id=timeline_id,
                en=en
            )
        )
        
        if response.status_code != 200:
            raise ConnectionError(response.text)
        
        response = response.json()
        title = response["respBody"]["lawInfo"]["lawNameTh"]
        return title