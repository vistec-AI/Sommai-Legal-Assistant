ORDINAL_WORDS = [
    "ทวิ", "ตรี", "จัตวา", "เบญจ", "ฉ", "สัตต", "อัฏฐ", "นว", "ทศ", "เอกาทศ", "ทวาทศ", "เตรส", 
    "จตุทศ", "ปัณรส", "โสฬส", "สัตตรส", "อัฏฐารส", "เอกูนวีสติ"
]
ORDINAL_PATTERN = "|".join(ORDINAL_WORDS)

THAI_TO_ARABIC = {
        "๐": "0", "๑": "1", "๒": "2", "๓": "3", "๔": "4",
        "๕": "5", "๖": "6", "๗": "7", "๘": "8", "๙": "9"
    }

THAI_TO_NUM = {
        "แรก": "1",
        "หนึ่ง": "1",
        "สอง": "2",
        "สาม": "3",
        "สี่": "4",
        "ห้า": "5",
        "หก": "6",
        "เจ็ด": "7",
        "แปด": "8",
        "เก้า": "9",
        "สิบ": "10",
        "ท้าย": "-1"
    }

LAWTYPE_LIST = ["รัฐธรรมนูญ",
                    "พระราชบัญญัติประกอบรัฐธรรมนูญ",
                    "พระราชบัญญัติ",
                    "พระราชกำหนด",
                    "ประมวลกฎหมาย",
                    "กฎมณเฑียรบาล",
                    "พระบรมราชโองการ",
                    "พระราชกฤษฎีกา",
                    "กฎกระทรวง",
                    ]

SECTION_TYPE_ID_MAPPER = {
    "3": "คำปรารภ",
    "4": "มาตรา",
    "5": "บรรพ",
    "6": "ภาค",
    "7": "ลักษณะ",
    "8": "หมวด",
    "9": "ส่วน",
    "13": "บทเฉพาะกาล",
    "14": "ผู้รับสนองพระบรมราชโองการ",
    "15": "หมายเหตุ",
    "16": "เบ็ดเตล็ด"
}

PREFACE_ID = "3"
SECTION_ID = "4"
BOOK_ID = "5"
SUBBOOK_ID = "6"
TITLE_ID = "7"
CHAPTER_ID = "8"
DIVISION_ID = "9"
PROVISION_ID = "13"
RESPONDENT_ID = "14"
FOOTNOTE_ID = "15"
MISCELLANEOUS_ID = "16"


LAWUNIT_DIR = "../parser/data/"