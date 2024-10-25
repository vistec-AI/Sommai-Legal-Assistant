import logging
import re
import yaml
from tqdm import tqdm
from typing import List, Union, Optional, Tuple

from .schema import (
    LawTree,
    LawCollection
)

from ..data_request.request import (
    LawDocumentReader
)

from .const import (
    ORDINAL_WORDS,
    ORDINAL_PATTERN,
    LAWUNIT_DIR,
    LAWTYPE_LIST,
    SECTION_TYPE_ID_MAPPER
)

class LawParser:
            
    def __init__(self, 
                 config_path: str = "",
                 txt_path: str = "",
                 deepest_subsection: bool = False,
                 SECTION_TYPE_ID_MAPPER: dict = SECTION_TYPE_ID_MAPPER,
                 documents: list = None,
                 urls: list = None,
                 LAWUNIT_DIR: str = LAWUNIT_DIR) -> None:
        """
        Init function for LawParser class

        Args:
            SECTION_TYPE_ID_MAPPER (dict, optional): mapping of section type id to section type name. Defaults to SECTION_TYPE_ID_MAPPER.
            config_path (str, optional): path to config file. Defaults to "config.yaml".
            txt_path (str, optional): path to text file. Defaults to "config.txt".
            documents (list, optional): list of documents value from config file. Defaults to None.
            urls (list, optional): list of urls. Defaults to None.
            LAWUNIT_DIR (str, optional): directory to save law units. Defaults to LAWUNIT_DIR.

        Raises:
            ValueError: if urls is not provided
        """
        self.deepest_subsection = deepest_subsection
        self.SECTION_TYPE_ID_MAPPER = SECTION_TYPE_ID_MAPPER
        self.law_request = LawDocumentReader()
        self.dynamic_law_splitter = DynamicLawSplitter(SECTION_TYPE_ID_MAPPER = self.SECTION_TYPE_ID_MAPPER,
                                                       get_sections_func = self.get_sections)
        
        self.config_path = config_path
        self.txt_path = txt_path
        self.LAWUNIT_DIR = LAWUNIT_DIR
        self.documents = documents
        if documents:
            self.urls = [law["url"] for law in self.documents]
        else:
            self.urls = urls
            
        if not self.urls:
            raise ValueError("missing argument: urls: list of urls")

    @classmethod
    def from_config(cls, config_path: str) -> "LawParser":
        """
        Create a LawParser object from a configuration file

        The configuration file is a YAML file with the following format:
            documents:
                - url: <url of document 1>
                  title: <title of document 1>
                - url: <url of document 2>
                  title: <title of document 2>
                - ...

        Args:
            config_path (str): path to configuration file

        Returns:
            LawTree: law unit representing all documents in the configuration file
        """
        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            documents = data.get('documents', [])

        return cls(config_path=config_path,
                   documents=documents)

    
    @classmethod
    def from_txt(cls, txt_path: str) -> "LawParser":
        """
        Create a LawParser object from a text file

        The text file should contain one URL per line.

        Args:
            txt_path (str): path to text file

        Returns:
            LawTree: law unit representing all documents in the text file
        """
        with open(txt_path, 'r', encoding='utf-8') as file:
            data = file.read()
            urls = data.splitlines()

        return cls(txt_path=txt_path,
                   urls=urls)
    
    @classmethod
    def generate_from_config(cls,
                             config_path: str,
                             deepest_subsection: bool = False,
                             show_progress: bool = False,
                             update_config: bool = False,) -> LawCollection:
        """
        Create a LawTree from a configuration file

        The configuration file is a YAML file with the following format:
            documents:
                - url: <url of document 1>
                  title: <title of document 1>
                - url: <url of document 2>
                  title: <title of document 2>
                - ...

        Args:
            config_path (str): path to configuration file
            show_progress (bool): whether to show progress bar or not

        Returns:
            LawTree: law unit representing all documents in the configuration file
        """
        with open(config_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            documents = data.get('documents', [])

        law_parser = cls(config_path=config_path,
                         documents=documents,
                         deepest_subsection=deepest_subsection)

        parsed_law = law_parser.request_law(show_progress=show_progress)
        parsed_law = law_parser.generate_lawunit(parsed_law,
                                                 show_progress=show_progress)
        
        if update_config:
            law_parser.update_config_file()

        return LawCollection(parsed_law)

    
    @classmethod
    def generate_from_txt(cls,
                          txt_path: str,
                          deepest_subsection: bool = False,
                          show_progress: bool = False,
                          config_output_path: str = None) -> LawCollection:
        """
        Create a LawTree from a text file

        The text file should contain one URL per line.

        Args:
            txt_path (str): path to text file
            show_progress (bool): whether to show progress bar or not

        Returns:
            LawTree: law unit representing all documents in the text file
        """
        with open(txt_path, 'r', encoding='utf-8') as file:
            data = file.read()
            urls = data.splitlines()

        law_parser = cls(txt_path=txt_path,
                         urls=urls,
                         deepest_subsection=deepest_subsection)

        parsed_law = law_parser.request_law(show_progress=show_progress)
        parsed_law = law_parser.generate_lawunit(parsed_law,
                                                 show_progress=show_progress)
        
        if config_output_path:
            law_parser.update_config_file(output_path=config_output_path)

        return LawCollection(parsed_law)
        
    def update_config_file(self, output_path: str = None) -> None:
        """
        Update the config file with the title of each URL

        If config_path is not None, it will update the existing config file with the
        title of each URL. If output_path is not None, it will write the updated data to
        that path, otherwise it will write the updated data to the config_path.

        If config_path is None, it will create a new config file with the data from
        the txt file.

        Args:
            output_path (str): path to save updated config file to (optional)
        """
        # update from existing config file
        if self.config_path:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                documents = data.get('documents', [])

            for doc in documents:
                title = self.law_request.get_url_title(doc["url"])
                # Update the YAML file with the title if necessary
                if 'title' not in doc or doc['title'] != title:
                    doc['title'] = title

            # Write back the updated data to the YAML file
            logging.info("Updating config...")
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as file:
                    yaml.dump(data, file, allow_unicode=True)
            else:
                with open(self.config_path, 'w', encoding='utf-8') as file:
                    yaml.dump(data, file, allow_unicode=True)
        # create new config file
        else:
            logging.info("Creating config from txt...")
            data = {"documents" : [{"url" : url} for url in self.urls]}
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as file:
                    yaml.dump(data, file, allow_unicode=True)
            else:
                raise ValueError("Please provide output_path")
                    
    def request_law(self,
                    show_progress: bool = False) -> List[dict]:
        """Request law object from Official Council State (OCS).

        Args:
            show_progress (bool, optional): Whether to show a progress bar during
                the request. Defaults to False.

        Returns:
            List[dict]: List of dictionaries containing the law text.
        """
        return self.law_request.get_page(urls=self.urls, show_progress=show_progress)
        
    def generate_lawunit(self,
                         request_laws: List[dict],
                         show_progress: bool = False) -> List[LawTree]:
        """
        Generate law unit from request law object

        Args:
            request_laws (List[dict]): List of request law objects
            show_progress (bool, optional): Whether to show a progress bar during
                the parsing process. Defaults to False.

        Returns:
            List[LawTree]: List of law unit objects
        """
        def get_law_type(nameTh: str) -> str:
            """
            Determine law type based on Thai name

            Args:
                nameTh (str): Thai name of the law

            Returns:
                str: law type
            """
            lawType = ""
            for nameType in LAWTYPE_LIST:
                if nameType in nameTh:
                    lawType = nameType
            return lawType
            
        parsed_law = []
        iterator = tqdm(request_laws, desc="Generating LawTree...", unit="doc",
                        leave=True, ncols=100, colour='blue') if show_progress else request_laws
        for request_law in iterator:
            request_law = request_law["respBody"]
            
            assert request_law["hasSection"], "No data, check url path..."
            
            lawInfo = request_law["lawInfo"]
            lawInfo["lawType"] = get_law_type(lawInfo["lawNameTh"])
            nameEn = lawInfo["lawNameEn"]
            nameTh = lawInfo["lawNameTh"]
            lawCode = lawInfo["lawCode"]
            lawType = lawInfo["lawType"]
            
            # cut หมายเหตุ
            for index, section in enumerate(request_law["lawSections"]):
                if section["sectionTypeId"] == self.dynamic_law_splitter.footnote_id:
                    break
            lawSections = request_law["lawSections"][:index]
            
            # check footnote
            # must cutout หมายเหตุ first to prevent bugging
            for index, section in reversed(list(enumerate(lawSections))):
                if section["sectionTypeId"] == self.dynamic_law_splitter.section_id:
                    break
            lawSections = request_law["lawSections"][:index+1]
            
            # get preface
            preface, lawSections = self.dynamic_law_splitter.get_preface(lawSections,lawInfo=lawInfo)
            # get provision
            provision, lawSections = self.dynamic_law_splitter.get_provision(lawSections, lawInfo=lawInfo)
            law = LawTree(lawType=lawType.strip(),
                          nameTh=nameTh.strip(),
                          nameEn=nameEn.strip(),
                          lawCode=lawCode.strip(),
                        sectionChildren=self.parse_hierarchical(lawSections, lawInfo=lawInfo))
            if preface:
                law.sectionChildren = [preface] + law.sectionChildren
            if provision:
                law.sectionChildren.append(provision)
            parsed_law.append(law)
        
        return parsed_law

    def parse_hierarchical(self, lawSections: List[dict], lawInfo: dict, current_level: int = 0) -> List[LawTree]:
        """Recursive function to parse the law sections and return a hierarchical structure.

        Args:
            lawSections (List[dict]): List of law sections with relevant info
            current_level (int, optional): Current level of recursion. Defaults to 0.

        Returns:
            List[LawTree]: List of LawTree objects representing the hierarchical structure of the law sections.
        """
        node_lawunit = []  # List of LawTree objects to be returned

        parents, children, next_level, sectionType, sections = self.dynamic_law_splitter.split_sections(
            lawSections, current_level)

        # Loop until parents is not empty
        while True:
            if parents:
                break
            if next_level:
                parents, children, next_level, sectionType, sections = self.dynamic_law_splitter.split_sections(
                    lawSections, next_level)
            else:
                break

        # If parents is not empty, create a LawTree object and append it to node_lawunit
        if parents:
            if sections:
                node_lawunit.extend(self.get_sections(lawSections, lawInfo=lawInfo))
            for parent, child in zip(parents, children):
                sectionLabel = parent["sectionLabel"].split("/")[-1].strip()
                try:
                    sectionName = re.findall(r"\d+(.+)", parent["sectionContent"])[0].strip()
                except IndexError:
                    sectionName = parent["sectionContent"].replace(sectionLabel, "").strip()
                law = LawTree(
                    nameEn=lawInfo["lawNameEn"].strip(),
                    nameTh=lawInfo["lawNameTh"].strip(),
                    lawCode=lawInfo["lawCode"].strip(),
                    lawType=lawInfo["lawType"].strip(),
                    sectionType=sectionType.strip(),
                    sectionNo=parent["sectionNo"].strip(),
                    sectionId=parent["sectionId"],
                    sectionLabel=sectionLabel.strip(),
                    sectionName=sectionName.strip(),
                    sectionChildren=self.parse_hierarchical(child, lawInfo=lawInfo, current_level=next_level)
                )
                node_lawunit.append(law)
            return node_lawunit

        # If all levels have been passed, assume it is a leaf now
        # and return the result of get_sections function
        return self.get_sections(lawSections, lawInfo=lawInfo)

    def get_sections(self, lawSections: List[dict], lawInfo: dict) -> List[LawTree]:
        """
        Get section and subsection from law object, handling nested miscellaneous sections.

        Parameters:
            lawSections (List[dict]): List of law sections from Thai laws.
            lawInfo (dict): Dictionary containing law information.

        Returns:
            List[LawTree]: List of LawTree objects representing the hierarchical structure of the law sections.
        """
        def find_common_root(words: List[str]) -> str | None:
            """
            Finds the longest common substring that appears within a list of words.

            Args:
                words: A list of words (strings).

            Returns:
                The longest common substring, or None if no common substring is found.
            """
            if not words:
                return "เบ็ดเตล็ด"
            # Start with the shortest word as the potential root
            shortest_word = min(words, key=len)

            # Iterate through potential root lengths (from shortest word length down to 1)
            for root_len in range(len(shortest_word), 0, -1):
                # Generate all possible substrings of that length from the shortest word
                for start_pos in range(len(shortest_word) - root_len + 1):
                    potential_root = shortest_word[start_pos: start_pos + root_len]
                # Check if this potential root is a substring in all other words
                    if all(potential_root in word for word in words):
                        return potential_root.strip()  # Found a common substring!

            return "เบ็ดเตล็ด"  # No common substring found
        
        misc_list = [misc["sectionName"] for misc in lawSections if misc["sectionTypeId"] == self.dynamic_law_splitter.miscellaneous_id]
        misc_name = find_common_root(misc_list)

        def build_tree(sections: List[dict]) -> List[LawTree]:
            """
            Recursive function to build the LawTree structure with nested miscellaneous sections.
            """
            tree_nodes = []
            current_misc = None

            for section in sections:
                # normalize space
                # section["sectionContent"] = re.sub(r"\s+", " ", section["sectionContent"])
                # check thai index
                full_section_name = re.findall(rf"^{section['sectionLabel']} (\S+) ", section["sectionContent"])
                if full_section_name:
                    assert len(full_section_name) == 1, f"Error -> full_section_name: {full_section_name}"
                    full_section_name = full_section_name[0].strip()
                    if full_section_name in ORDINAL_WORDS:
                        section["sectionNo"] = f"{section['sectionNo']} {full_section_name}"
                        section["sectionLabel"] = f"{section['sectionLabel']} {full_section_name}"

                # Handle miscellaneous sections
                if section["sectionTypeId"] == self.dynamic_law_splitter.miscellaneous_id:
                    if current_misc is None:
                        current_misc = LawTree(
                            nameEn=lawInfo["lawNameEn"].strip(),
                            nameTh=lawInfo["lawNameTh"].strip(),
                            lawCode=lawInfo["lawCode"].strip(),
                            lawType=lawInfo["lawType"].strip(),
                            sectionType=misc_name.strip(),  # Miscellaneous section type
                            sectionNo=section["sectionNo"].strip(),
                            sectionId=section["sectionId"],
                            sectionLabel=f"{lawInfo['lawNameTh']} {section['sectionLabel']}",
                            sectionContent=f"{lawInfo['lawNameTh']} {section['sectionContent']}",
                            sectionChildren=[],
                        )
                        tree_nodes.append(current_misc)
                    else:
                        next_misc = LawTree(
                            nameEn=lawInfo["lawNameEn"].strip(),
                            nameTh=lawInfo["lawNameTh"].strip(),
                            lawCode=lawInfo["lawCode"].strip(),
                            lawType=lawInfo["lawType"].strip(),
                            sectionType=misc_name.strip(),  # Miscellaneous section type
                            sectionNo=section["sectionNo"].strip(),
                            sectionId=section["sectionId"],
                            sectionLabel=f"{lawInfo['lawNameTh']} {section['sectionLabel']}",
                            sectionContent=f"{lawInfo['lawNameTh']} {section['sectionContent']}",
                            sectionChildren=[],
                        )
                        # Nested miscellaneous section, add as child to current
                        current_misc.sectionChildren.append(next_misc)
                        current_misc = next_misc
                elif section["sectionTypeId"] == self.dynamic_law_splitter.section_id:
                    # Leaf section (regular or under miscellaneous)
                    leaf_section = LawTree(
                        nameEn=lawInfo["lawNameEn"].strip(),
                        nameTh=lawInfo["lawNameTh"].strip(),
                        lawCode=lawInfo["lawCode"].strip(),
                        lawType=lawInfo["lawType"].strip(),
                        sectionType="มาตรา",
                        sectionNo=section["sectionNo"].strip(),
                        sectionId=section["sectionId"],
                        sectionLabel=f"{lawInfo['lawNameTh']} {section['sectionLabel']}",
                        sectionContent=f"{lawInfo['lawNameTh']} {section['sectionContent']}",
                        sectionClause=section["sectionContent"].splitlines(),
                        sectionReference=self.get_reference(section["sectionContent"], section["sectionNo"]),
                    )

                    # Add subsections if available
                    subsection_leafs = []
                    if self.deepest_subsection:
                        subsections, subsection_clauses, subsection_index = self.get_subsections(
                            section["sectionContent"], label=section["sectionLabel"]
                        )
                        if subsections:
                            for subsection, subsection_clause, subsection_id in zip(subsections, subsection_clauses, subsection_index):
                                subsection_leafs.append(
                                    LawTree(
                                        nameEn=lawInfo["lawNameEn"].strip(),
                                        nameTh=lawInfo["lawNameTh"].strip(),
                                        lawCode=lawInfo["lawCode"].strip(),
                                        lawType=lawInfo["lawType"].strip(),
                                        sectionType="อนุมาตรา", 
                                        sectionNo=f"{section['sectionNo']}{subsection_id}", 
                                        sectionId=section["sectionId"], 
                                        sectionLabel=f"{lawInfo['lawNameTh']} {section['sectionLabel']} อนุมาตรา {subsection_id}", 
                                        sectionContent=f"{lawInfo['lawNameTh']} {subsection}", 
                                        sectionClause=subsection_clause, 
                                        sectionReference=self.get_reference(subsection, section['sectionNo'])  
                                    )
                                )
                    leaf_section.sectionChildren = subsection_leafs

                    if current_misc is not None:
                        current_misc.sectionChildren.append(leaf_section)
                    else:
                        tree_nodes.append(leaf_section)
                else:
                    continue
            return tree_nodes

        return build_tree(lawSections)

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
    
    def get_reference(self, content: str, section_no: str) -> List[str]:
        """
        Extracts and processes references from the given content.

        Args:
            content (str): The input content to extract references from.
            section_no (str): The section number of the content.

        Returns:
            List[str]: A list of extracted and processed references.

        Notes:
            - The function uses regular expressions to find and process different patterns of references in the content.
            - It defines two helper functions: `clean_brackets` and `dedup_and_sort`.
            - The `clean_brackets` function removes any parentheses from a given string.
            - The `dedup_and_sort` function removes duplicates from a list and sorts it.
            - The function processes three different patterns of references: range pattern, conjunction pattern, and simple reference pattern.
            - The range pattern is identified using the `range_pattern` regular expression.
            - The conjunction pattern is identified using the `conjunction_pattern` regular expression.
            - The simple reference pattern is identified using the `simple_reference_pattern` regular expression.
            - The range pattern is processed by finding all matches in the content and replacing them with a space-separated list of new references.
            - The conjunction pattern is processed by finding all matches in the content and replacing them with a string joined by "และ" (and).
            - The simple reference pattern is processed by finding all matches in the content and appending them to the `referenceId` list.
            - The `referenceId` list is then deduplicated and sorted.
            - The final list of references is returned.

        """
        def clean_brackets(s: str):
            return s if "(" in s and ")" in s else s.replace("(", "").replace(")", "")

        def dedup_and_sort(lst: list, section_no: str):
            """Remove duplicates and sort the list

            Parameters
            ----------
            lst : list
                List to be deduplicated and sorted
            section_no: str
                Section number

            Returns
            -------
            list
                Sorted list with no duplicates
            """
            lst = [l for l in lst if l != section_no]
            return sorted(set(lst))

        referenceId = []
        range_pattern = re.compile(r"มาตรา \d+/?\d* ถึงมาตรา \d+/?\d*")
        conjunction_pattern = re.compile(rf"(?<!\()(มาตรา \d+/?\d*\(?\d*/?\d*\)?\s*(?:{ORDINAL_PATTERN})? \s*\(?\d*/?\d*\)? และ \(\d+\))")
        simple_reference_pattern = re.compile(rf"(?<!\()(มาตรา \d+/?\d*\(?\d*/?\d*\)?\s*(?:{ORDINAL_PATTERN})?)")
        dummy = content[:]

        def process_range_pattern(dummy: str) -> str:
            """
            Process the range pattern in the given dummy text.

            Args:
                dummy (str): The input text to process.

            Returns:
                str: The processed dummy text with the range pattern replaced.

            Notes:
                - The function searches for patterns in the dummy text using the `range_pattern` regular expression.
                - It filters out patterns that start with the same value as the pattern itself.
                - For each remaining pattern, it splits the start and end values by "/" if it exists.
                - If "/" exists in the start and end values, it asserts that the main section is the same in both cases.
                - It creates a list of integers between the start and end values (inclusive) using `range()`.
                - It replaces the original pattern with a space-separated list of new references using a list comprehension.
            """
            process_range_pattern = [pattern.strip() for pattern in range_pattern.findall(dummy)]
            for case in process_range_pattern:
                start, end = re.findall(r"\d+/?\d*", case)
                if "/" in start and "/" in end:
                    main_section = int(start.split("/")[0])
                    assert start.split("/")[0] == end.split("/")[0], "The main section should be the same in both cases."
                    start_sub = int(start.split("/")[1])
                    end_sub = int(end.split("/")[1])
                    numbers_between = list(range(start_sub, end_sub + 1))
                    replace_text = " ".join([f"มาตรา {main_section}/{num}" for num in numbers_between])
                else:
                    numbers_between = list(range(int(start), int(end) + 1))
                    replace_text = " ".join(["มาตรา " + f"{num}" for num in numbers_between])
                dummy = re.sub(case, replace_text, dummy)
            return dummy


        def process_conjunction_pattern(dummy: str) -> str:
            """
            Process the conjunction pattern in the given dummy text.

            Args:
                dummy (str): The input text to process.

            Returns:
                str: The processed dummy text with the conjunction pattern replaced.

            Raises:
                AssertionError: If the main section is not found in the conjunction pattern.

            Notes:
                - The function searches for patterns in the dummy text using the `conjunction_pattern` regular expression.
                - It filters out patterns that start with the same value as the pattern itself.
                - For each remaining pattern, it finds the main section using the `ORDINAL_PATTERN` regular expression.
                - It asserts that there is only one main section found.
                - It extracts the subsections from the pattern using the regular expression `\(\d+\)`.
                - It replaces the pattern in the dummy text with a string joined by "และ" (and) using the main section and subsections.
                - The processed dummy text is returned.

            """
            process_conjunction_pattern = [pattern.strip() for pattern in conjunction_pattern.findall(dummy)]
            for case in process_conjunction_pattern:
                main_section = re.findall(rf"มาตรา \d+/?\d*\(?\d*/?\d*\)?\s*(?:{ORDINAL_PATTERN})?", case)
                assert len(main_section) == 1
                main_section = main_section[0]
                subsections = re.findall(r"\(\d+\)", case)
                replace_text = " และ ".join([f"{main_section}{sub}" for sub in subsections])
                dummy = re.sub(case, replace_text, dummy)
            return dummy

        def process_simple_reference_pattern(dummy: str) -> list:
            """
            Find and process simple reference pattern in the given text.

            Args:
                dummy (str): The input text to process.

            Returns:
                list: The list of references found in the given text.

            Notes:
                - The function searches for patterns in the dummy text using the `simple_reference_pattern` regular expression.
                - It filters out patterns that start with the same value as the pattern itself.
                - For each remaining pattern, it removes "มาตรา" and any whitespace using `.replace()`.
                - It removes any parentheses using the `clean_brackets()` function.
                - It appends the processed reference to the `referenceId` list and returns it at the end.

            """
            process_simple_reference_pattern = [
                pattern.strip() for pattern in simple_reference_pattern.findall(dummy)]
            
            for reference in process_simple_reference_pattern:
                reference = reference.replace("มาตรา", "").strip()  # remove "มาตรา" and strip whitespaces
                reference = clean_brackets(reference)  # remove any parentheses
                referenceId.append(reference)  # append the reference to the list
            return referenceId  # return the list of references

        dummy = process_range_pattern(dummy)
        dummy = process_conjunction_pattern(dummy)
        referenceId = process_simple_reference_pattern(dummy)
        referenceId = dedup_and_sort(referenceId, section_no)
        return referenceId

class DynamicLawSplitter:
        def __init__(self, SECTION_TYPE_ID_MAPPER: dict, get_sections_func) -> None:
            self.requiredId = list(SECTION_TYPE_ID_MAPPER.keys())
            self.sectionId = []
            self.sectionName = []
            self.get_sections = get_sections_func  # Reference to the get_sections function
            for id, section_type in SECTION_TYPE_ID_MAPPER.items():
                if section_type == "คำปรารภ":
                    self.preface_id = id
                    self.preface_name = section_type
                elif section_type == "มาตรา":
                    self.section_id = id
                    self.section_name = section_type
                elif section_type == "บทเฉพาะกาล":
                    self.provision_id = id
                    self.provision_name = section_type
                elif section_type == "หมายเหตุ":
                    self.footnote_id = id
                    self.footnote_name = section_type
                elif section_type == "ผู้รับสนองพระบรมราชโองการ":
                    self.respondent_id = id
                    self.respondent_name = section_type
                elif section_type == "เบ็ดเตล็ด":
                    self.miscellaneous_id = id
                    self.miscellaneous_name = section_type
                else:
                    self.sectionId.append(id)
                    self.sectionName.append(section_type)
            assert len(self.sectionId) == len(self.sectionName)
                    
            logging.debug(f"Thai Law Hierarchical Structure {' -> '.join(self.sectionName)}")
            logging.debug(f"Thai Law Hierarchical ID {' -> '.join(self.sectionId)}")

        def split_sections(self, lawSections: List[dict], level: int = 0) -> Union[List[dict], List[List[dict]], int, str]:
            """Hierarchical text splitter into sections based on section type

            Args:
                lawSections (List[dict]): list of sections
                level (int, optional): current level of the splitting. Defaults to 0.

            Returns:
                Union[List[dict], List[List[dict]], int, str]:
                    parents: sections of the current level
                    children: list of sections below the current level
                    next_level: next level of the splitting
                    section_type: type of the current level

            This function splits the law sections into parents and children based on the section type.
            If the current level is valid, it splits the sections into parents and children.
            Otherwise, it returns the next level and section type of the current level.
            """
            # check if the current level is valid
            if level + 1 > len(self.sectionName):
                return None, None, None, None, None

            # list of parents and children of the current level
            parents, children = [], []
            # chunk of sections of the current level
            chunk = []
            # list of section ids
            ids = [id["sectionTypeId"] for id in lawSections]

            # check if the current section id exists in the list of sections
            # if it does, split the sections into parents and children
            if self.sectionId[level] in ids:
                for section in lawSections:
                    # skip if the section type is not required
                    if section["sectionTypeId"] not in self.requiredId:
                        continue
                    # if the section type is the current section type, add it to parents
                    # if it is not the current section type, add it to the chunk
                    if section["sectionTypeId"] == self.sectionId[level]:
                        if chunk:
                            # if the chunk is not empty, add it to children and create a new chunk
                            children.append(chunk)
                            chunk = []
                        parents.append(section)
                    else:
                        chunk.append(section)
                # add the last chunk to children
                children.append(chunk)
                sections = None
                if len(children) - len(parents) == 1:
                    sections = children.pop(0)
                assert len(parents) == len(children), f"len(parents): {len(parents)} | len(children): {len(children)}\n parents: {parents}\n children: {children[0]}\nlawSections: {lawSections}"
                # return parents, children, next level, section type of the current level
                return parents, children, level+1, self.sectionName[level], sections

            # if the current section id does not exist, return the next level and section type
            else:
                return None, None, level + 1, self.sectionName[level], None

        def get_preface(self, lawSections: List[dict], lawInfo: dict) -> Union[LawTree, List[dict]]:
            """
            get preface if exists

            Returns:
                A LawTree object if preface exists, otherwise a tuple of None and the list of sections
            """
            is_preface = False  # flag to check if we are inside preface
            preface_section = []  # list of preface sections
            ids = [id["sectionTypeId"] for id in lawSections]  # list of section ids
            if not self.preface_id in ids:  # check if preface exists
                return None, lawSections  # return None and the list of sections if preface doesn't exist

            for index, section in enumerate(lawSections):
                if is_preface:
                    if section["sectionTypeId"] == self.section_id:
                        preface_section.append(section)  # add the section to the preface
                        if index+1 == len(lawSections):
                            index = index+1
                    elif section["sectionTypeId"] in self.sectionId:  # break if the section is not of the same type as preface
                        break
                    else:
                        continue  # continue if the sectionTypeId is anomaly -> we normalize the structure
                if section["sectionTypeId"] == self.preface_id:
                    is_preface = True  # set the flag to True if we are inside preface
                    start_preface_section = section

            if not is_preface and not preface_section:  # check if we found any preface sections
                return None, lawSections  # return None and the list of sections if preface doesn't exist
            preface_section = self.get_sections(preface_section, lawInfo=lawInfo)  # get the children of the preface sections
            return LawTree(  # return the LawTree with the preface information
                nameEn=lawInfo["lawNameEn"].strip(),
                nameTh=lawInfo["lawNameTh"].strip(),
                lawCode=lawInfo["lawCode"].strip(),
                lawType=lawInfo["lawType"].strip(),
                sectionName=self.preface_name,
                sectionType=self.preface_name,  # section type of the preface
                sectionId=start_preface_section["sectionId"],  # section id of the preface
                sectionLabel=start_preface_section["sectionLabel"].strip(),  # section label of the preface
                sectionContent=start_preface_section["sectionContent"].strip(),  # section content of the preface
                sectionChildren=preface_section  # children of the preface
            ), lawSections[index:]  # return the remaining list of sections
            
        
        def get_provision(self, lawSections: List[dict], lawInfo: dict) -> Tuple[Optional[LawTree], List[dict]]:
            """
            get provision if exists

            Returns:
                A LawTree object if provision exists, otherwise a tuple of None and the list of sections
            """
            is_provision = False  # flag to check if we are inside provision
            provision_section = []  # list of provision sections
            ids = [id["sectionTypeId"] for id in lawSections]  # list of section ids
            if not self.provision_id in ids:  # check if provision exists
                return None, lawSections  # return None and the list of sections if provision doesn't exist
            for index, section in enumerate(lawSections):
                if is_provision:
                    # if we are inside provision, add the section to the provision list
                    # or break if the section is not of the same type as provision
                    if section["sectionTypeId"] == self.section_id:
                        provision_section.append(section)
                    else:
                        continue
                # set the flag to True if we are inside provision
                if section["sectionTypeId"] == self.provision_id:
                    is_provision = True
                    start_provision_section = section
                    # store the index of the provision section
                    start_provision = index

            if not is_provision and not provision_section:
                # return None and the list of sections if we didn't find any provision sections
                return None, lawSections
            provision_section = self.get_sections(provision_section, lawInfo=lawInfo)  # get the children of the provision sections
            return LawTree(  # return the LawTree with the provision information
                nameEn=lawInfo["lawNameEn"].strip(),
                nameTh=lawInfo["lawNameTh"].strip(),
                lawCode=lawInfo["lawCode"].strip(),
                lawType=lawInfo["lawType"].strip(),
                sectionName=self.provision_name,
                sectionType=self.provision_name,  # section type of the provision
                sectionId=start_provision_section["sectionId"],  # section id of the provision
                sectionLabel=start_provision_section["sectionLabel"].strip(),  # section label of the provision
                sectionContent=start_provision_section["sectionContent"].strip(),  # section content of the provision
                sectionChildren=provision_section  # children of the provision
            ), lawSections[:start_provision]  # return the remaining list of sections