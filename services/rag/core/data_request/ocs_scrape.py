import os
from tqdm import tqdm
from random import randint
from typing import Dict, List, Callable

from pydantic import BaseModel

from .const import LAW_CATEGORY_MAPPER, THAI_ALPHABET
from .ocs_backdoor import get_ocs_law
from .request import LawDocumentReader
from..hierarchical_parser.const import FOOTNOTE_ID, SECTION_ID

class OcsLaw(BaseModel):
    categories: Dict[str, str] = LAW_CATEGORY_MAPPER
    alphabets: List[str] = THAI_ALPHABET
    reader: Callable = LawDocumentReader()
    
    def get_metadata(self) -> Dict[str, object]:
        metadata = []
        iterator = tqdm(self.categories, desc="Get metadata from OCS...", unit="doc", leave=True, ncols=100, colour='blue')
        for category in iterator:
            if "," in category:
                for alphabet in self.alphabets:
                    metadata.extend(get_ocs_law(category, alphabet)['respBody']['data'])
            else:
                metadata.extend(get_ocs_law(category)['respBody']['data'])
        return metadata
    
    def extract_id(self, metadata: List[Dict[str, object]]) -> List[str]:
        return [law["timelineId"] for law in metadata]
    
    def trim(self, request_law: List[Dict[str, object]]) -> Dict[str, str]:
        # cut หมายเหตุ
        for index, section in enumerate(request_law):
            if section["sectionTypeId"] == FOOTNOTE_ID:
                break
        lawSections = request_law[:index]
        
        # check footnote
        # must cutout หมายเหตุ first to prevent bugging
        for index, section in reversed(list(enumerate(lawSections))):
            if section["sectionTypeId"] == SECTION_ID:
                break
        lawSections = request_law[:index+1]
        return lawSections
    
    @classmethod
    def scrape(cls,
               save_path: str,
               trim: bool = True,
               show_progress: bool = False) -> Dict[str, object]:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        law_ids = cls().extract_id(metadata=cls().get_metadata())
        law_contents = cls().reader.get_page(urls= law_ids, show_progress= show_progress)
        iterator = tqdm(law_contents, desc="Scraping Thai Laws from OCS...", unit="doc", leave=True, ncols=100, colour='blue') if show_progress else law_contents
        for law in iterator:
            title = law["respBody"]["lawInfo"]["lawCode"]
            body = law["respBody"]["lawSections"]
            if trim:
                body = cls().trim(request_law= body)
            full_text = "\n".join([section["sectionContent"] for section in body]).strip()
            if not full_text:
                continue
            with open(f"{save_path}/{title}.txt", 'w', encoding='utf-8') as file:
                file.write(full_text)
        