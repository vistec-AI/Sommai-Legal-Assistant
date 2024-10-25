LLAMA_3_PROMPT_TEMPLATE = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"""

QUERY_GEN_PROMPT_STR = (
    "You are a helpful assistant that generates multiple search queries based on a "
    "single input query. Generate {num_queries} search queries, one on each line, "
    "related to the following input query:\n"
    "Query: {query}\n"
    "Queries:\n"
    )

EN_SYSTEM_PROMPT_STR = (
    "You are a legal assistant named Sommai (สมหมาย in Thai), you provide legal advice to users in a friendly and understandable manner."
    "When answering questions, you specifically reference the law sections relevant to the query, "
    "including the name of the act or code they originated from, an explanation of what those sections entail, "
    "and any associated punishments or fees. Your tone is approachable and informal yet polite, "
    "making users feel as if they are seeking advice from a friend. "
    "If a question arises that does not match the information you possess, "
    "you must acknowledge your current limitations by stating this exactly sentence: 'สมหมายไม่สามารถตอบคำถามนี้ได้ครับ' ."
    "You will not fabricate information but rather guide users based on actual law sections relevant to their situation. "
    "Additionally, you offer practical advice on next steps, such as gathering required documents, seeking medical attention, "
    "or visiting a police station, as applicable. "
    "If inquired about past Supreme Court judgments, you must reply that you do not have information on those judgments yet."
)
TH_SYSTEM_PROMPT_STR = (
    "คุณเป็นผู้ช่วยทางกฎหมายที่ชื่อว่า สมหมาย คุณจะให้คำปรึกษาทางกฎหมายแก่ผู้ใช้งานด้วยความเป็นมิตรและใช้ภาษาที่เข้าใจง่ายในการตอบคำถาม "
    "ตอนตอบคำถาม คุณจะต้อวอ้างอิงถึงมาตราของกฎหมายที่เกี่ยวข้องกับคำถาม รวมถึงชื่อของกฎหมายของมาตราเหล่านั้น"
    "อธิบายว่ามาตราเหล่านี้ครอบคลุมเรื่องอะไร รวมถึงโทษหรือค่าปรับหากทำความผิดตามมาตรานั้น "
    "โดยคุณต้องมีความเป็นกันเองและไม่เป็นทางการ แต่ยังคงสุภาพในการตอบคำถาม ทำให้ผู้ใช้รู้สึกเหมือนกำลังขอคำปรึกษาจากเพื่อน "
    "หากคำถามจากผู้ใช้งานที่ไม่ตรงกับข้อมูลที่แนบไป, คุณต้องตอบกลับผู้ใช้งานไปด้วยประโยค 'สมหมายไม่สามารถตอบคำถามนี้ได้ครับ' เท่านั้น"
    "คุณต้องให้คำแนะนำที่เป็นประโยชน์เกี่ยวกับการดำเนินการให้กับผู้ใช้งานต่อไป เช่น การเตรียมเอกสารที่จำเป็น, การขอความช่วยเหลือทางการแพทย์, "
    "หรือการไปที่สถานีตำรวจ ตามที่เหมาะสม "
    "หากถูกถามเกี่ยวกับคำตัดสินของศาลฎีกาในอดีต, คุณต้องตอบว่า ยังไม่มีข้อมูลเกี่ยวกับคำตัดสินเหล่านั้นในตอนนี้ "
)

EN_TEXT_QA_TEMPLATE_STR = """Given the user's query in the context of Thai legal matters, the RAG system retrieves the top_n related documents. From these documents, it's crucial to identify and utilize only the most relevant ones to craft an accurate and informative response.

Context information is below.
---------------------
Context: Thai legal domain
Query: {query_str}
Retrieved Documents:
{context_str}
---------------------

Using the provided context information and the list of retrieved documents, you will focus on selecting the documents that are most relevant to the user's query. This selection process involves evaluating the content of each document for its pertinency to the query, ensuring that the response is based on accurate and contextually appropriate information.
Based on the selected documents, you will synthesize a response that addresses the user's query, drawing directly from the content of these documents to provide a precise, legally informed answer.
You must answer in Thai.
Answer:
"""

TH_TEXT_QA_TEMPLATE_STR = """จากคำถามของผู้ใข้งาน ได้มีการดึงข้อกฎหมายที่เกี่ยวข้องมาดังนี้

---------------------
คำถาม: {query_str}
ข้อกฎหมายที่เกี่ยวข้อง:
{context_str}
---------------------

จากข้อกฎหมายที่เกี่ยวข้อง คุณจะต้องเลือกเอกสารที่เกี่ยวข้องกับคำถามของผู้ใข้งาน เพื่อนำมาประกอบเป็นคำตอบที่เหมาะสม
โดยจะต้องอธิบายข้อกฎหมายที่ถูกต้องโดยละเอียด และตอบคำถามที่ผู้ใช้งานอยากรู้ด้วย
คำตอบ:
"""

EN_REFINE_REFERENCE_TEMPLATE_STR = """
---------------------
Retrieved Documents:
{context_str}
References:
{reference_str}
---------------------
"""

TH_REFINE_REFERENCE_TEMPLATE_STR = """
---------------------
ข้อกฎหมายที่เกี่ยวข้อง:
{context_str}
ข้อกฎหมายที่ถูกอ้างอิง:
{reference_str}
---------------------
"""

EN_DEFAULT_REFERENCE_TEMPLATE_STR = """
---------------------
Retrieved Documents:
{context_str}
---------------------
References:
{reference_str}
---------------------
"""

TH_DEFAULT_REFERENCE_TEMPLATE_STR = """
---------------------
ข้อกฎหมายที่เกี่ยวข้อง:
{context_str}
---------------------
ข้อกฎหมายที่ถูกอ้างอิง:
{reference_str}
---------------------
"""


EN_REFERENCE_QA_TEMPLATE_STR = """Given the user's query in the context of Thai legal matters, the RAG system retrieves the top_n related documents. From these documents, it's crucial to identify and utilize only the most relevant ones to craft an accurate and informative response.
Each retrieved document might be accompanied by its reference section, which could be helpful to add more context for answering.

Context information is below.
---------------------
Context: Thai legal domain
Query: {query_str}
{context_str}


Using the provided context information and the list of retrieved documents, you will focus on selecting the documents that are most relevant to the user's query. This selection process involves evaluating the content of each document for its pertinency to the query, ensuring that the response is based on accurate and contextually appropriate information.
Based on the selected documents, you will synthesize a response that addresses the user's query, drawing directly from the content of these documents to provide a precise, legally informed answer.
You must answer in Thai.
Answer:
"""

TH_REFERENCE_QA_TEMPLATE_STR = """จากคำถามของผู้ใข้งานเกี่ยวกับกฎหมายไทย คุณจะต้องเลือกใช้ข้อกฎหมายที่เกี่ยวข้องที่เราแนบไว้ให้ ในการตอบคำถามของผู้ใช้งาน
โดยในแต่ละข้อกฎหมายที่เกี่ยวข้อง อาจมีการอ้างอิงถึงข้อกฎหมายอื่นๆ ซึ่งจะถูกแนบประกอบไปในส่วน ข้อกฎหมายที่ถูกอ้างอิง เพื่อใช้เป็นเนื้อหาเสริมประกอบการตอบคำถาม แต่ใจความหลักในการตอบคำถาม ต้องมาจาก ข้อกฎหมายที่เกี่ยวข้อง เท่านั้น
จากคำถามของผู้ใช้งาน ได้มีการดึงข้อกฎหมายที่เกี่ยวข้องมาดังนี้

---------------------
บริบท: กฎหมายไทย
คำถาม: {query_str}
{context_str}


จากข้อกฎหมายที่เกี่ยวข้อง คุณจะต้องเลือกเอกสารที่เกี่ยวข้องกับคำถามของผู้ใข้งาน เพื่อนำมาประกอบเป็นคำตอบที่เหมาะสม
โดยจะต้องอธิบายข้อกฎหมายที่ถูกต้องโดยละเอียด และตอบคำถามที่ผู้ใช้งานอยากรู้ด้วย
คำตอบ:
"""

EN_REFINE_TEMPLATE_STR = """The original question is as follows: {query_str}
We have provided an existing answer: {existing_answer}

Given new context or additional documents retrieved, there is an opportunity to refine the existing answer to enhance its accuracy and relevance to Thai legal matters.

------------
New Context and Retrieved Documents:
Context: Thai legal domain
Query: {query_str}
Retrieved Documents: {context_str}
------------

Using the new context, the list of retrieved documents, and your own expertise, evaluate the existing answer. Identify if and how it can be improved or clarified. Consider the relevance and legal accuracy of the information provided in the context of Thai law.

Selection Criteria for Document Utilization: Ensure that the documents selected for refining the answer are highly relevant to the query, contain specific legal references applicable to the question, and offer clarity or additional insight into the matter at hand.
If the documents are not relevant, return the original existing answer.

Refined Answer:
"""

TH_REFINE_TEMPLATE_STR = """คำถามจากผู้ใช้: {query_str}
คำตอบที่มีอยู่: {existing_answer}

จากข้อกฎหมายที่เกี่ยวข้องชุดใหม่ อาจจะสามารถปรับปรุงคำตอบที่มีอยู่แล้วให้ดีขึ้นได้

------------
New Context and Retrieved Documents:
บริบท: กฎหมายไทย
คำถาม: {query_str}
กฎหมายที่เกี่ยวข้อง: {context_str}
------------

จากข้อกฎหมายที่เกี่ยวข้องชุดใหม่ คุณจะต้องพิจารณาว่าคำตอบที่มีอยู่แล้วจะสามารถปรับปรุงให้ดีขึ้นจากกฎหมายที่เกี่ยวข้องนี้ได้อย่างไรบ้าง
โดยคุณต้องพิจารณาก่อนว่ากฎหมายที่เกี่ยวข้องนี้ มีความเกี่ยวข้องกับคำถามหรือไม่ ถ้าไม่ ให้ตอบกลับโดยใช้คำตอบที่มีอยู่แล้ว
ถ้ากฎหมายที่เกี่ยวข้อง มีความเกี่ยวข้องกับคำถาม ให้คุณนำข้อมูลนี้ไปปรับปรุงให้คำตอบมีรายละเอียดครบถ้วนสมบูรณ์

คำตอบที่ปรับปรุงแล้ว:
"""

SINGLE_QA_CRAFTING_TEMPLATE_STR = """
Crafting First-Person Perspective, Law-Related Quiz Questions in a Conversational Tone

---------------------
Context Information:
{context_str}
Reference Section:
{reference_str}
---------------------

Instructions:
Using the context information provided above, which focuses on a specific section of law, your mission is to create {num_questions_per_chunk} questions for an upcoming quiz or examination.
The reference section is an extra detail for the context (if the context mentioned any other section, it will be provided, else, it will be omitted). The questions must focus on the context information.
These questions need to meet the following criteria:

- Be framed in Thai, utilizing everyday language as if narrated by an average Thai citizen recounting an incident to a police officer. The tone should be casual and conversational.
- Stem from a first-person narrative, illustrating scenarios directly related to the given law section. 
- Prompt students to discern and apply the relevant section of law based on the described scenario, all while avoiding explicit mention of the law section number or title in the question.
- Format each question to be on a separate line, clear and concise, without any additional explanations or verbose details. This is crucial for processing the output effectively.

Aim for scenarios that are relatable and varied, encouraging critical thinking about the law's application in diverse real-life situations. 

This adjusted template is designed to foster the generation of immersive, scenario-specific questions that mimic a dialogue or informal report to a police officer. This approach intends to assist students in practical legal principle application in an engaging, realistic manner.

Generated questions:
"""

MULTI_QA_CRAFTING_TEMPLATE_STR = """
Crafting First-Person Perspective, Law-Related scenario Based on Multiple Contexts

---------------------
Context Information:
{context_str}
Reference Section:
{reference_str}
---------------------

Instructions:
You are tasked with creating a scenario conversation based on the given multiple sections of law as the context information. It is crucial that you select and *explicitly use AT LEAST TWO* sections from the provided context information to construct your query. These selected sections should be able to logically coexist based on real-world scenario logic without causing conflicts. Incorporate additional sections as you see fit to enrich the scenario, but ensure no fewer than two sections are used as the foundation for your query.

The reference sections provide extra details for the context. While creating your question, avoid explicitly mentioning law section numbers or titles, but structure the scenario in such a way that students can determine and apply the relevant laws.

Your output should be in the form of a JSON dictionary with the designated structure:
{{
  'en_query': '<generated query in English>',
  'th_query': '<generated query in Thai>',
  'context_index': [<list of indexes of selected context information used in creating the query>]
}}

Be mindful of the following criteria while crafting your queries:
- ***Important*** The scenario must be based on and explicitly utilize at least two sections from the context information provided. You must use sections from the context information as many as possible.
- If you can use three or more sections to construct queries, I will tip you 20 bucks for your great performance.
- The query you create should be initially in English, followed by a Thai translation focusing on the naturalness of the language.
- ***Important*** Adopt a casual and conversational tone, as if narrated by an average Thai citizen recounting an incident to a police officer.
- Design your query to prompt students to discern and apply the relevant section of law based on the described scenario, while steering clear of directly mentioning law section numbers or titles.
- Ensure each question is clear, concise, and framed as a separate line without extraneous explanations or details.
- ***Important*** DO NOT start the query with the 'Imagine this' or 'Imagine that' phrases, but instead focus on the scenario itself.

JSON output:
"""