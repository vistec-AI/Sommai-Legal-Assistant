import json
import os
import re

from openai import OpenAI
from core.hierarchical_parser.schema import LawTree
from core.hierarchical_parser.utils import law_unit_to_dict
from tqdm import tqdm
from typing import Union, List

ORDINAL_WORDS = [
    "ทวิ", "ตรี", "จัตวา", "เบญจ", "ฉัพพีสติ", "ฉ", "สัตตรส", "สัตต", "อัฏฐารส", "อัฏฐ", "นว", "ทศ", "เอกาทศ", "ทวาทศ", "เตรส", 
    "จตุทศ", "ปัณรส", "โสฬส", "เอกูนวีสติ", "วีสติ", "เอกวีสติ", "ทวาวีสติ", "เตวีสติ", "จตุวีสติ", "ปัญจวีสติ"
]
ORDINAL_PATTERN = "|".join(ORDINAL_WORDS)

EXCLUDED_LAW_NAMES = [
    "พระราชบัญญัติหลักทรัพย์และตลาดหลักทรัพย์ พ.ศ. 2535 ซึ่งแก้ไขเพิ่มเติมโดยพระราชบัญญัติหลักทรัพย์และตลาดหลักทรัพย์ (ฉบับที่ 4) พ.ศ. 2551",
    "พระราชบัญญัติหลักทรัพย์และตลาดหลักทรัพย์ พ.ศ. 2535 และแก้ไขเพิ่มเติมโดยพระราชบัญญัติหลักทรัพย์และตลาดหลักทรัพย์ (ฉบับที่ 5) พ.ศ. 2559",
    "พระราชบัญญัติหลักทรัพย์และตลาดหลักทรัพย์ พ.ศ. 2535 ซึ่งแก้ไขเพิ่มเติมโดยพระราชบัญญัติหลักทรัพย์และตลาดหลักทรัพย์ (ฉบับที่ 5) พ.ศ. 2559",
    "พระราชบัญญัติวิธีการงบประมาณ พ.ศ. 2502 ซึ่งแก้ไขเพิ่มเติมโดยพระราชบัญญัติวิธีการงบประมาณ (ฉบับที่ 2) พ.ศ. 2503",
]

STEM_LAW_DICT = {
    "รัฐธรรมนูญแห่งราชอาณาจักรไทย": "รัฐธรรมนูญ",
    "ประมวลรัษฎากร พ.ศ. 2477": "ประมวลรัษฎากร",
    "พระราชบัญญัติยกเลิกพระราชบัญญัติการซื้อขายสินค้าเกษตรล่วงหน้า พ.ศ. 2558": "พระราชบัญญัติยกเลิกพระราชบัญญัติการซื้อขายสินค้าเกษตรล่วงหน้า พ.ศ. 2542 พ.ศ. 2558",
}

TH_SYSTEM_PROMPT_SUBSECTION_STR = (
    ""
    # "คุณเป็นผู้ช่วยทางกฎหมายที่ชื่อว่า สมหมาย คุณเชี่ยวชาญในการระบุข้อกฎหมายและมาตราที่ถูกอ้างอิง"
    # "ตอนตอบคำถามคุณจะต้องทำตามขั้นตอนดังนี้"
    # "1. ระบุชื่อเลขมาตราที่ถูกอ้างอิงทั้งหมดจากข้อความที่ได้รับ โดยเลขมาตรามักจะมีคำว่า 'มาตรา' นำหน้า"
    # "1.1. ในกรณีที่เลขมาตรามีอนุมาตราต่อท้าย ให้ระบุเลขมาตรารวมกับอนุมาตรา เช่น ข้อความระบุว่า 'มาตรา 1 (13)' ให้ระบุเลขมาตราเป็น '1 (13)'"
    # "1.2. ในกรณีที่เลขมาตรามี 'วรรค' ต่อท้าย ให้ระบุเฉพาะเลขมาตราเท่านั้น เช่น ข้อความระบุว่า 'มาตรา 1 วรรคหนึ่ง' ให้ระบุเลขมาตราเป็น '1'"
    # "1.3. ในกรณีที่มีการอ้างอิงเป็นช่วงให้ระบุเลขมาตราทั้งหมดในช่วงนั้น เช่น ข้อความระบุว่า 'ตามมาตรา 1 ถึง มาตรา 3' ให้ระบุเลขมาตราเป็น '1', '2', '3'"
    # "1.4. ในกรณีที่มีการยกเลิกมาตรากฎมหาย ไม่ต้องระบุมาตราเหล่านั้น เช่น 'มาตรา 130 ถึง มาตรา 143 (ยกเลิก)' และ 'มาตรา 130 (ยกเลิก)' "
    # "2. หาชื่อกฎหมายของแต่ละมาตราที่ถูกอ้างอิงทั้งหมด"
    # "2.1. ในกรณีที่ชื่อกฎหมายมีเลขปี พ.ศ. ต่อท้ายให้นำเลขปี พ.ศ. มาด้วย"
    # "2.2. ในกรณีที่ชื่อกฎหมายมีการแก้ไขเพิ่มเติมให้นำส่วนที่แก้ไขเพิ่มเติมมาด้วย "
    # "3. ตอบในรูปแบบของ JSON ดังนี้ {'results': [{'sectionNo': 'ชื่อมาตราที่ถูกอ้างอิง', 'lawName': 'ชื่อกฎหมายที่ถูกอ้างอิง'}]}"
)

TH_SYSTEM_PROMPT_SECTION_STR = (
    "คุณเป็นผู้ช่วยทางกฎหมายที่ชื่อว่า สมหมาย คุณเชี่ยวชาญในการระบุข้อกฎหมายและมาตราที่ถูกอ้างอิง "
    "ตอนตอบคำถามคุณจะต้องทำตามขั้นตอนดังนี้ "
    "1. ระบุชื่อเลขมาตราที่ถูกอ้างอิงทั้งหมดจากข้อความที่ได้รับ โดยเลขมาตรามักจะมีคำว่า 'มาตรา' นำหน้า "
    "1.1. ในกรณีที่เลขมาตรามีอนุมาตราต่อท้าย ให้ระบุเฉพาะเลขมาตราเท่านั้น เช่น ข้อความระบุว่า 'มาตรา 1 (13)' ให้ระบุเลขมาตราเป็น '1' "
    "1.2. ในกรณีที่เลขมาตรามี '/' และตามด้วยตัวเลขต่อท้าย ให้ระบุเฉพาะเลขมาตรารวม '/' และตัวเลขต่อท้ายด้วยเท่านั้น เช่น 'มาตรา 193/14' ให้ระบุเลขมาตราเป็น '193/14' "
    "1.3. ในกรณีที่เลขมาตรามี 'วรรค' ต่อท้าย ให้ระบุเฉพาะเลขมาตราเท่านั้น เช่น ข้อความระบุว่า 'มาตรา 1 วรรคหนึ่ง' ให้ระบุเลขมาตราเป็น '1' "
    "1.4. ในกรณีที่มีการอ้างอิงเป็นช่วง ให้ถือว่าการระบุเป็นช่วงคือ 'ชื่อมาตราที่ถูกอ้างอิง' เช่น 'มาตรา 1 ถึงมาตรา 3' ให้ถือว่า'ชื่อมาตราที่ถูกอ้างอิง' คือ 'มาตรา 1 ถึงมาตรา 3' "
    "1.5. ในกรณีที่มีการยกเลิกมาตรากฎมหาย ไม่ต้องระบุมาตราเหล่านั้น เช่น 'มาตรา 130 ถึง มาตรา 143 (ยกเลิก)' และ 'มาตรา 130 (ยกเลิก)' "
    "2. หาชื่อกฎหมายของแต่ละมาตราที่ถูกอ้างอิงทั้งหมด "
    "2.1. ในกรณีที่ชื่อกฎหมายมีเลขปี พ.ศ. ต่อท้ายให้นำเลขปี พ.ศ. มาด้วย "
    "2.2. ในกรณีที่ชื่อกฎหมายมีการแก้ไขเพิ่มเติมให้นำส่วนที่แก้ไขเพิ่มเติมมาด้วย "
    "3. ตอบในรูปแบบของ JSON ดังนี้ {'results': [{'sectionNo': 'ชื่อมาตราที่ถูกอ้างอิง', 'lawName': 'ชื่อกฎหมายที่ถูกอ้างอิง'}]} "
)


def send_query_to_openai(client, openai_model_name, node, level="section"):
    content = node.sectionContent.replace(node.sectionLabel, node.nameTh)

    if level == "section":
        system_prompt = TH_SYSTEM_PROMPT_SECTION_STR
    else:
        system_prompt = TH_SYSTEM_PROMPT_SUBSECTION_STR

    response = client.chat.completions.create(
        model=openai_model_name,
        temperature=0,
        seed=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
    )

    return json.loads(response.choices[0].message.content)["results"]


def is_included(law_section_ref, included_law_names, excluded_law_names=[]):
    for law_section_ref_i in law_section_ref:
        law_name = law_section_ref_i["lawName"]
        law_section_ref_i["sectionNo"] = clean_section_name(law_section_ref_i["sectionNo"])

        if law_name.replace(" ", "") in excluded_law_names:
            law_section_ref_i["include"] = False
        elif clean_included_law_name(law_name) in included_law_names:
            law_section_ref_i["include"] = True
        else:
            law_section_ref_i["include"] = False

    # remove duplicate value.
    law_section_ref = [dict(t) for t in {tuple(d.items()) for d in law_section_ref}]
    
    return law_section_ref


def stem(name: str):
    if name in STEM_LAW_DICT.keys():
        name = STEM_LAW_DICT[name]

    return name


def clean_included_law_name(name: str):
    # stem
    name = stem(name)

    # remove พ.ศ.
    name = re.sub("พ\.ศ.*$", "", name)

    name = name.replace("ํา", "ำ")

    name = name.strip()

    return name


def clean_section_name(name: str):
    name = re.sub("วรรค.*$", "", name)
    name = re.sub("มาตรา|อนุมาตรา", "", name)
    name = name.replace(" ", "")

    return name


def clean_reference_response(law_section_ref, fill_value):
    for ref in law_section_ref:
        # fill unknown
        if (ref["lawName"].strip() == "") or ref["lawName"].strip().startswith("ไม่"):
            ref["lawName"] = fill_value

        # clean law name
        law_name = ref["lawName"].replace("ํา", "ำ")
        law_name = law_name.replace("พุทธศักราช", "พ.ศ.")
        law_name = law_name.strip()
        law_name = stem(law_name)
        ref["lawName"] = law_name

    return law_section_ref

def reformat(law_sections):
    reformat_law_sections = []
    for law_section in law_sections:
        law_unit = dict()
        law_unit['law_name'] = law_section['nameTh'].strip()
        law_unit['section_num'] = law_section['sectionNo']
        law_unit['section_content'] = law_section['sectionContent']
        law_unit['reference'] = []
        for ref in law_section['lawSectionReference']:
            reformat_ref = {}
            reformat_ref['law_name'] = ref['lawName'].strip()
            reformat_ref['section_num'] = ref['sectionNo']
            reformat_ref['include'] = ref['include']
            law_unit['reference'].append(reformat_ref)

        reformat_law_sections.append(law_unit)

    return reformat_law_sections


def explode_range_of_sections(law_sections, law2section_num):
    section_pattern = rf'\s*\d+/?\d*\s*(?:{ORDINAL_PATTERN})?'
    range_section_pattern = rf'{section_pattern}\s*ถึง\s*{section_pattern}'

    for law_section in law_sections:
        reference = []
        if law_section['reference'] != []:
            for ref in law_section['reference']:
                ref_law_name = ref['law_name']
                ref_section_num = ref['section_num']
                range_section_str = re.findall(range_section_pattern, ref_section_num)
                if len(range_section_str) == 0:
                    reference.append(ref)
                    continue
                else:
                    range_section_str = range_section_str[0]
        
                strt_end_sections = [re.sub(r'\s+', ' ' , i).strip() for i in re.findall(section_pattern, range_section_str)]
                section_num_lst = law2section_num[ref_law_name]
                start_idx = section_num_lst.index(strt_end_sections[0])
                end_idx = section_num_lst.index(strt_end_sections[1])
                    
                for i in section_num_lst[start_idx:end_idx+1]:
                    ref_unit = {}
                    ref_unit['section_num'] = i
                    ref_unit['law_name'] = ref_law_name
                    reference.append(ref_unit)

        law_section['reference'] = reference

    return law_sections


def get_reference_law(
    law_tree: Union[LawTree, str],
    included_law_names: List[str],
    law2section_num: dict,
    save_output_dir: str = None,
    excluded_law_names: List[str] = EXCLUDED_LAW_NAMES,
    overwrite: bool = False,
    openai_model_name="gpt-4-turbo",
    level="section",
    is_reformat=True
) -> dict:
    if isinstance(law_tree, str):
        law_tree = LawTree.from_filename(law_tree)

    leaf_nodes = law_tree.get_leaf_nodes(return_as_list=True, as_reference=False)
    included_law_names = [clean_included_law_name(name) for name in included_law_names]
    excluded_law_names = [name.replace(" ", "") for name in excluded_law_names]

    # check existed file
    law_code = law_tree.lawCode
    save_file_name = f"{law_code}.json"
    if (save_file_name in os.listdir(save_output_dir)) and (not overwrite):
        save_file_path = os.path.join(save_output_dir, save_file_name)
        print(f"File already existed. load data from {save_file_path}")
        with open(save_file_path) as f:
            leaf_node_dict = json.load(f)

        return leaf_node_dict

    # call openai to get referenced law
    client = OpenAI()
    for node in tqdm(leaf_nodes):
        node.sectionContent = node.sectionContent.replace("ํา", "ำ")
        node.nameTh = node.nameTh.replace("ํา", "ำ")
        node.sectionNo = clean_section_name(node.sectionNo)

        if len(node.sectionReference) != 0 and (node.sectionNo != "(ยกเลิก)"):
            law_section_ref = send_query_to_openai(client, openai_model_name, node, level)
            law_section_ref = clean_reference_response(law_section_ref, node.nameTh)
            law_section_ref = is_included(law_section_ref, included_law_names, excluded_law_names)

            node.lawSectionReference = law_section_ref
        else:
            node.lawSectionReference = []

        # node.sectionReference = []

    leaf_node_dict = [law_unit_to_dict(node) for node in leaf_nodes]

    # reformat
    if is_reformat:
        leaf_node_dict = reformat(leaf_node_dict)

    # explode_range_of_sections
    leaf_node_dict = explode_range_of_sections(leaf_node_dict, law2section_num)

    # save output in JSON file.
    if save_output_dir is not None:
        if not os.path.exists(save_output_dir):
            os.makedirs(save_output_dir)

        save_file_path = os.path.join(save_output_dir, save_file_name)
        with open(save_file_path, "w", encoding="utf-8") as file:
            json.dump(leaf_node_dict, file, ensure_ascii=False, indent=4)

    return leaf_node_dict
