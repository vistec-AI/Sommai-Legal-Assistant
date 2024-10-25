"""Warning: This is an experimental feature used for parsing ประมวลกฎหมายแพ่งและพานิชย์ only"""
import logging
import re
import os
from pathlib import Path
from tqdm.auto import tqdm
from typing import List, Union

from .const import (
    ORDINAL_PATTERN,
    THAI_TO_ARABIC,
    THAI_TO_NUM,
    LAWTYPE_LIST,
)

from ..hierarchical_parser.schema import LawTree

from ..data_request.const import THAI_ALPHABET

def strip_newline(text):
    """strip lines"""
    text = re.sub(r"\n+", "\n", text)
    return '\n'.join([normalize_space(t.strip()) for t in text.splitlines() if t.strip()])

def clean_footnote(text):
    """remove footer from sections"""
    return re.sub(r'\[\d+\]', ' ', text)

def clean_reference(text: str) -> str:
    return re.sub(r'\[\*มาตรา.+\]', '', text)

def clean_bracket(text: str) -> str:
    return re.sub(r'\[.*\]', '', text)
    
def convert_thai_index(text):
    """convert Thai numbers to Arabic"""

    pattern = re.compile('|'.join(THAI_TO_ARABIC.keys()))
    result = pattern.sub(lambda x: THAI_TO_ARABIC[x.group()], text)
    return result

def convert_thai_num(text):
    """convert Thai number words to arabic number"""

    pattern = re.compile('|'.join(THAI_TO_NUM.keys()))
    result = pattern.sub(lambda x: THAI_TO_NUM[x.group()], text)
    return result

def find_last_before_restart(sequence):
    """Get total numbers of each level by excluding table of contents"""
    last_before_restart = None

    for i, num in enumerate(sequence):
        if isinstance(num, str):
            num = int(num)
        if num == 1:
            if i > 0:
                last_before_restart = sequence[i - 1]
    # if not last_before_restart:
    #     if last_before_restart % 2 != 0:
    #         print('Warning: section is not even number')
    return int(last_before_restart)


def normalize_space(text) -> str:
    """replace multiple spaces with one space"""
    return re.sub(r' +', ' ', text)

def refine_subsection_reference(text) -> str:
    """Pattern to match "มาตรา xx (" with optional spaces before the '(' """
    pattern = r"(มาตรา \d+) \("

    # Replacement pattern
    replacement = r"\1("  # \1 refers to the first captured group (มาตรา xx) followed by "(" without space

    # Using re.sub to find the pattern and replace it
    return re.sub(pattern, replacement, text)

def get_law_header(text: str) -> str | str:
    """get law header from text. Return law_type and law_name"""
    law_type, law_name = [head.strip() for head in text.splitlines()[:2]]
    if "ประมวลกฎหมาย" in law_name:
        name = re.findall(r"(ประมวล.+)", law_name)[0].strip()
        return "ประมวลกฎหมาย", name
    for type in LAWTYPE_LIST:
        if law_type == type:
            return type, f"{law_type}{law_name}"

def extract_main_text(text) -> str:
    """get main text from act/code
    2 cases
        1. Deep hierarchical structure
            mostly start from ประเภทกฎหมาย -> ภาค -> ลักษณะ -> หมวด -> มาตรา -> อนุมาตรา
            mostly ends with หมายเหตุ
            easiest way is to define by ภาค
            and it must have มาตรา 1 two times or more, we can extract main text by start from the second มาตรา 1
        2. Shallow hierarchical structure
            mostly start from หมวด -> มาตรา -> อนุมาตรา
            mostly มาตรา 1 occurs once
            mostly ends with ผู้รับสนองพระบรมราชโองการ
            no need to preprocess อนุมาตรา in มาตรา before starting หมวด
    we focus on มาตรา in หมวด โทษ | ความผิด | กำหนดโทษ | ลงโทษ
    but other details will be stored for data solidity
    
    we need to identify the type of code(ประเภทกฎหมาย) case
    using counting มาตรา 1 method
    """
    # convert Thai number
    # text = convert_thai_num(text)
    text = convert_thai_index(text)
    
    # clean footnote
    text = clean_footnote(text)
    text = clean_bracket(text)
    
    # remove section reference note
    text = clean_reference(text)
    
     # clean by strip each line
    text = strip_newline(text)
    
    # get code type and name
    law_type, name = get_law_header(text)
    
    # hard code to get body
    detail = "\n".join(text.splitlines()[2:])
    
    # # classify code case
    # multi_first_section = len(re.findall(r'\nมาตรา 1\s', text)) > 1
    
    # if multi_first_section:
    #     # drop footer
    #     detail = text.split('หมายเหตุ', maxsplit = 1)[0]
    #     # drop header
    #     digits_list = re.findall(r'\nภาค\s\d+', detail)
    #     digits_list = [''.join(re.findall(r'\d', string)) for string in digits_list]

    #     total_section = find_last_before_restart(digits_list)
    #     detail = re.split(r'\nภาค', detail)
    #     detail = ['ภาค' + text for text in detail]

    #     detail = '\n'.join(detail[len(detail) - total_section:])
    
    # else:
    #     # drop footer
    #     detail = text.split('ผู้รับสนองพระบรมราชโองการ', maxsplit = 1)[0]
    #     # drop header
    #     detail = re.split(r'\nมาตรา 1\s', detail)
    #     assert len(detail) == 2
    #     # get main text
    #     detail = detail[-1]
    #     detail = 'คำปรารภ\nมาตรา 1 ' + detail
        
    # transform subsection reference
    # detail = refine_subsection_reference(detail)
    return law_type, name, detail
    
def get_preface(text) -> list:
    """get preface if exists"""
    if text.startswith('ข้อความเบื้องต้น'):
        for level in ['บรรพ', 'ภาค', 'ลักษณะ', 'หมวด', 'ส่วน']:
            first_level = re.findall(fr'\n{level}', text)
            if first_level:
                preface_text = text.split(f'\n{level}', maxsplit = 1)[0]
                preface_text = '\n'.join(preface_text.splitlines()[1:]).strip()
                remain_text = '\n'.join(text.split(f'\n{level}', maxsplit = 1)[1:])
                remain_text = f'{level}{remain_text}'
                
                return 'ข้อความเบื้องต้น', preface_text, remain_text
    else:
        return None, None, None
            
def split_hierarchical(text: str, hierarchical_word: str) -> List[str]:
    """split text into hierarchical chunks"""
    # add newlines to prevent bug
    text = '\n' + text + '\n'        
    # split text to each chunk
    if hierarchical_word == 'บุริมสิทธิ':
        pattern = re.compile(rf'\n\d+\.\s+(.+)')
        chunk_pattern = re.compile(rf'\n\d+\.\s+.+')
    elif hierarchical_word == 'บุริมสิทธิเหนือ':
        pattern = re.compile(rf'\n\([ก-ฮ]\)\s+({hierarchical_word}.+)')
        chunk_pattern = re.compile(rf'\n\([ก-ฮ]\)\s+{hierarchical_word}.+')
    elif hierarchical_word == 'ส่วน':
        pattern = re.compile(rf'\n{hierarchical_word}ที่\s\d+\n+(.+)')
        chunk_pattern = re.compile(rf'\n{hierarchical_word}ที่\s\d+\n+.+')
    else:
        pattern = re.compile(rf'\n{hierarchical_word}\s\d+\n+(.+)')
        chunk_pattern = re.compile(rf'\n{hierarchical_word}\s\d+\n+.+')
    indexes = pattern.findall(text)
    if not indexes:
        return None, None, None
    initial_section = re.findall(r"^\nมาตรา", text)
    initial_section_chunk = ""
    if initial_section:
        initial_section_chunk = chunk_pattern.split(text)[0]
        text = text.replace(initial_section_chunk, "").strip()
    hierarchical_chunks = chunk_pattern.split(text)
    hierarchical_chunks = [chunk.strip() for chunk in hierarchical_chunks if chunk.strip()]
    
    return indexes, hierarchical_chunks, initial_section_chunk

def get_sections(text) -> list:
    """split text into sections"""
    # add newline at the end to prevent bug when extracting section via regex
    text = '\n' + text + '\n'
    pattern = r'(มาตรา \d+.*?)(?=\nมาตรา \d+|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    matched_list = [match.strip() for match in matches]
    
    # add double newline between section and detail
    matched_list = [re.sub(r'(^มาตรา\s+\d+/?\d*\s*)(' + ORDINAL_PATTERN + ')?\s+(.+)', r'\1\2\n\3', section) for section in matched_list]
    # transform_sections = [parse_and_transform_sections(section) for section in matched_list]
    # flatten
    # transform_sections = [section for sections in transform_sections for section in sections]
    clause_sections = [section.split('\n') for section in matched_list]
    # clause_sections = {clause[0]: clause for clause in clause_sections}
    
    return matched_list, clause_sections

def get_subsections(self, text: str, label: str) -> Union[List[str], List[List[str]]]:
    """
    Get subsections from a given section

    Each subsection is a string and the return value is a list of strings.
    If there are no subsections, return (None, None).

    Args:
        text (str): Section text
        label (str): Section label

    Returns:
        Union[List[str], List[List[str]]]: Subsections and their corresponding clauses
    """
    transformed_sections, subsection_index = self.parse_and_transform_sections(text, label)
    if transformed_sections:
        clause_sections = [section.splitlines() for section in transformed_sections]
        transformed_sections = [re.sub(r"\s+", " ", section) for section in transformed_sections]
        return transformed_sections, clause_sections, subsection_index
    else:
        return None, None, None

def parse_and_transform_sections(self, text: str, label: str) -> Union[List[str], None]:
    """
    Transform section into subsections if exist.
    Return a list of transformed sections if subsections exist, otherwise return None.

    The transformation is done by identifying subsections using regular expression.
    If no subsection is found, return None.

    If subsections are found, the transformed sections are constructed by:
    1. First section is the concatenation of all intro lines (lines that are not empty and not subsections)
    2. Second section is the concatenation of subsection index, space and subsection details
    3. Third section is the concatenation of all outro lines (lines that are not empty and not subsections)

    Args:
        text (str): Text of the section to be transformed
        label (str): Section label

    Returns:
        Any[List[str], None]: List of transformed sections or None if no subsections found
    """
    
    # Regular expression to identify subsections
    subsection_pattern = re.compile(r"^\(\d+/?\d*\)")
    subsubsection_pattern = re.compile(r"^\([ก-๙]+\)")
    
    # Split the text into lines and filter out empty lines
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Initialize containers for different parts of the text
    intro, outro, subsections, subsubsections = [], [], [], []
    # Flags to indicate parsing state
    in_subsection = False
    subsubsections_list = []
    for line in lines:
        if subsection_pattern.match(line):
            # Entering a subsection
            in_subsection = True
            subsections.append(line)
            if outro:
                subsubsections_list.append("\n".join(outro))
                outro = []
            subsubsections.append("\n".join(subsubsections_list))
            subsubsections_list = []
        elif subsubsection_pattern.match(line):
            subsubsections_list.append(line)
            # if subsections:
            #     subsections[-1] = "\n".join([subsections[-1], line])
            # else:
            #     intro.append(line)
        elif in_subsection:
            # Outro begins after subsections
            outro.append(line)
        else:
            # Intro before any subsection
            intro.append(line)
    subsubsections.append("\n".join(subsubsections_list))
    # pop first as dummy
    if subsubsections:
        subsubsections.pop(0)
        assert len(subsections) == len(subsubsections), f"{subsections} {subsubsections}"
        for subsection_index in range(len(subsections)):
            subsections[subsection_index] = "\n".join([subsections[subsection_index], subsubsections[subsection_index]]).strip()
            
    if not subsections:
        return None, None
    
    # check bug from source api
    # if not outro:
    #     last_chunk = subsections[-1]
    #     if all("ต้องระวาง" in sub for sub in subsections):
    #         pass
    #     elif "ต้องระวาง" in last_chunk:
    #         sub, fine = last_chunk.split("ต้องระวาง")
    #         subsections = subsections[:-1] + [sub]
    #         outro.append(f"ต้องระวาง{fine}")
    
    # Construct the transformed sections
    transformed_sections = []
    subsection_index = []
    # index_bug = []
    for sub in subsections:
        # if index_bug:
        #     index_bug.append(sub)
        #     index, sub_detail = index_bug
        #     index_bug = []
        # try:
        #     index, sub_detail = sub.split(" ", 1)
        # except:
        #     index_bug.append(sub)
        #     continue
        index, sub_detail = sub.split(" ", 1)
        sub_detail = re.sub(r"หรือ$", "", sub_detail.strip()).strip()
        # Replace label with subsection label
        section_header = intro[0].replace(label, f"{label} อนุมาตรา {index}", 1)
        section_body = "\n".join([section_header] + intro[1:] + [sub_detail] + outro)
        transformed_sections.append(section_body)
        subsection_index.append(index)
    assert len(transformed_sections) == len(subsection_index)
    return transformed_sections, subsection_index
        
def parse_law(text: str) -> LawTree:
    """Parsing text into LawTree object"""
    law_type, name, detail = extract_main_text(text)
    # Initialize the root LawTree object
    lawInfo = {"nameTh": name,
               "nameEn": "Civil and Commercial Code",
               "lawCode": "ป0003-1D-0002",
               "lawType": law_type
               }
    law = LawTree(lawType=law_type,
                  nameTh=name,
                  lawCode="ป0003-1D-0002",
                  sectionChildren=parse_hierarchical(text=detail, lawInfo=lawInfo))
    return law

def parse_hierarchical(text: str, lawInfo: dict) -> List[LawTree]:
    """recursive function to store LawTree"""
    
    # check preface
    preface, detail, remain_text = get_preface(text)
    preface_law = []
    if preface:
        law = LawTree(sectionType=preface,
                      nameTh=lawInfo["nameTh"],
                      nameEn=lawInfo["nameEn"],
                      lawCode=lawInfo["lawCode"],
                      lawType=lawInfo["lawType"],
                      sectionName=preface,
                      sectionLabel=preface,
                      sectionChildren=parse_hierarchical(text=detail, lawInfo=lawInfo))
        preface_law.append(law)
        text = remain_text

    hierarchical_functions = [
        'บรรพ', 'ภาค', 'ลักษณะ', 'หมวด', 'ส่วน', 'บุริมสิทธิ', 'บุริมสิทธิเหนือ'
    ]
    
    for law_type in hierarchical_functions:
        index_names, details, initial_section = split_hierarchical(text, law_type)
        initial_sections = []
        if initial_section:
            initial_sections.extend(parse_hierarchical(text=initial_section, lawInfo=lawInfo))
        # if that level not exists, return None
        if index_names:
            assert len(index_names) == len(details), f"{(index_names)} == {(details)}"
            node_LawTree = []
            node_LawTree.extend(preface_law)
            for i, (index_name, detail) in enumerate(zip(index_names, details)):
                if law_type == "บุริมสิทธิ":
                    section_label = f"บุริมสิทธิ"
                    section_no = str(i+1)
                elif law_type == "บุริมสิทธิเหนือ":
                    section_label = f"บุริมสิทธิเหนือ"
                    section_no = THAI_ALPHABET[i]
                else:
                    section_label = f"{law_type}ที่ {i+1}"
                    section_no = str(i+1)
                law = LawTree(nameTh=lawInfo["nameTh"],
                                nameEn=lawInfo["nameEn"],
                                lawCode=lawInfo["lawCode"],
                                lawType=lawInfo["lawType"],
                                sectionType=law_type,
                              sectionName=index_name,
                              sectionLabel=section_label,
                              sectionNo=section_no,
                              sectionChildren= initial_sections + parse_hierarchical(text=detail, lawInfo=lawInfo))
                node_LawTree.append(law)
            return node_LawTree
        else:
            if initial_sections:
                raise ValueError

    # if all level passed, assume it is a leaf node now
    transform_sections, clause_sections = get_sections(text)
    leaf_LawTree = []
    for i, section in enumerate(transform_sections):
        # check subsection
        # subsections, subsection_clauses = get_subsections(section)
        subsection_leafs = []
        # if subsections:
        #     for sub_num, subsection in enumerate(subsections):
        #         subsection_leafs.append(LawTree(sectionType= 'อนุมาตรา', sectionNo=str(sub_num+1), sectionContent=subsection, sectionClause=subsection_clauses[sub_num]))
        section_number = section.splitlines()[0].replace("มาตรา ", "", 1).strip()
        section = f"{lawInfo['nameTh']} {section}"
        law = LawTree(sectionType= 'มาตรา',
                      nameTh=lawInfo["nameTh"],
                      nameEn=lawInfo["nameEn"],
                      lawCode=lawInfo["lawCode"],
                      lawType=lawInfo["lawType"],
                      sectionLabel=f"{lawInfo['nameTh']} มาตรา {section_number}",
                      sectionNo=section_number,
                      sectionContent=section,
                      sectionClause=section.splitlines(),
                      sectionChildren=subsection_leafs)
        leaf_LawTree.append(law)
    return leaf_LawTree

def get_leaf_nodes(node, collection=None, return_as_list=False, keyword=None):
    """
    Recursively find all leaf nodes in the given LawTree structure and return them as either a list or a dictionary.

    Args:
    - node (LawTree): The current node being inspected.
    - collection: The collection used to accumulate leaf nodes, automatically determined based on return_as_list.
    - return_as_list (bool, optional): If True, returns a list of LawTree objects; otherwise, returns a dictionary.

    Returns:
    - A list or a dictionary of LawTree objects, depending on return_as_list.
    """
    if collection is None:
        collection = [] if return_as_list else {}
    
    if not node.children:
        if return_as_list:
            collection.append(node)
        else:
            collection[node.number] = node
    else:
        for child in node.children:
            if keyword:
                if keyword in child.name:
                    get_leaf_nodes(child, collection, return_as_list)
            else:
                get_leaf_nodes(child, collection, return_as_list)
    return collection
    
def get_section_and_subsection(node: LawTree, collection=None) -> LawTree:
    """
    Recursively gets all sections and subsections to process inplace reference
    """
    if collection is None:
        collection = {}
    
    if not node.children:
        collection[node.number] = node
    else:
        if node.unit_type == 'มาตรา':
            collection[node.number] = node
        for child in node.children:
            get_leaf_nodes(child, collection)
    return collection

def parse_documents(apply_reference=True, save_json=True, save_pickle=True, show_progress=True):
    """auto parse scrape documents into LawTree object"""
    filenames = os.listdir(scrape_data_dir)
    
    # Choose iterator based on show_progress flag
    iterator = tqdm(filenames) if show_progress else filenames
    
    for filename in iterator:
        print(filename)  # Printing the filename; consider doing this conditionally based on verbosity level
        with open(os.path.join(scrape_data_dir, filename), 'r', encoding='utf-8') as reader:
            text = reader.read()
            parsed_law = parse_law(text)
            if apply_reference:
                pass
        
        if save_json:
            name = Path(filename).stem
            save_path = os.path.join(LawTree_dir, f'{name}.json')
            # Convert and save to JSON
            save_to_json(parsed_law, save_path)

        if save_pickle:
            name = Path(filename).stem
            save_path = os.path.join(LawTree_dir, f'{name}.pkl')
            # Serialize and save using pickle
            save_with_pickle(parsed_law, save_path)