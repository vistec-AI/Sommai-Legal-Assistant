import re

def postprocess_qa_pairs(query: str) -> str:
    query = re.sub("อย่างไร", "ยังไง", query)
    query = re.sub("ต้องรับโทษ", "โดนโทษ", query)
    query = re.sub("เจอกับโทษ", "โดนโทษ", query)
    query = re.sub("ถูกดำเนินคดี", "โดนคดี", query)
    query = re.sub("ถูกลงโทษ", "โดนโทษ", query)
    query = re.sub("รุนแรง", "แรง", query)
    query = re.sub("ไหมครับ", "มั้ยครับ", query)
    query = re.sub("เขา", "เค้า", query)
    query = re.sub("สุรา", "เหล้า", query)
    
    return query