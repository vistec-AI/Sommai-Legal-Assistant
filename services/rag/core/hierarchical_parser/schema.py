import logging
import os
import re
from tqdm import tqdm
from typing import List, Dict, Union

from .utils import (
    save_to_json,
    save_with_pickle,
    load_with_pickle,
    load_from_json
)

class LawTree():
    """LawTree object for storing law data
    
    Initializes the class with the given parameters.

        Args:
            lawType (str): Type of law, e.g., "code", "act", "book", "title", "chapter", "division", "section"
            sectionType (str): Type of section
            sectionId (str): ID of the section
            nameTh (str): Thai name
            nameEn (str): English name
            lawCode (str): Code of the law
            sectionNo (str): Section number
            sectionContent (str): Content of the section
            sectionName (str): Name of the section
            sectionChildren (list): List of children sections
            sectionClause (list): List of section clauses
            sectionKeyword (list): List of section keywords
            sectionLabel (str): Label of the section
            sectionSummary (str): Summary of the section
            sectionReference (list): List of section references

        Returns: None"""
    def __init__(self, lawType=None, sectionType=None, sectionId=None, nameTh=None, nameEn=None, lawCode=None,
                 sectionNo=None, sectionContent=None, sectionName=None, sectionChildren=None, sectionClause=None,
                 sectionKeyword=None, sectionLabel=None, sectionSummary=None, sectionReference=None,
                 lawSectionReference=None) -> None:
        
        self.lawType = lawType
        self.nameTh = nameTh
        self.nameEn = nameEn
        self.lawCode = lawCode
        
        self.sectionType = sectionType
        self.sectionNo = sectionNo
        self.sectionId = sectionId
        self.sectionLabel = sectionLabel
        self.sectionContent = sectionContent
        self.sectionName = sectionName
        self.sectionClause = sectionClause if sectionClause else []
        self.sectionChildren = sectionChildren if sectionChildren else []
        self.sectionKeyword = sectionKeyword if sectionKeyword else []
        self.sectionSummary = sectionSummary
        self.sectionReference = sectionReference if sectionReference else []
        self.lawSectionReference = lawSectionReference if lawSectionReference else []
        
    def __repr__(self):
        return (f"LawTree(lawType={self.lawType!r}, nameTh={self.nameTh!r}, nameEn={self.nameEn!r}, "
                f"lawCode={self.lawCode!r}, sectionType={self.sectionType!r}, sectionNo={self.sectionNo!r}, "
                f"sectionId={self.sectionId!r}, sectionLabel={self.sectionLabel!r}, "
                f"sectionContent={self.sectionContent!r}, sectionClause={self.sectionClause!r}, "
                f"sectionChildren={self.sectionChildren!r}, sectionKeyword={self.sectionKeyword!r}, "
                f"sectionSummary={self.sectionSummary!r}, sectionReference={self.sectionReference!r},"
                f"lawSectionReference={self.lawSectionReference!r})"
                )

    def __str__(self):
        # Construct a formatted string with the law unit information
        truncated_sectionContent = self.sectionContent[:30] + "..." if self.sectionContent and len(self.sectionContent) > 30 else self.sectionContent
        unit_info_parts = [part for part in [self.lawType, self.sectionLabel, truncated_sectionContent] if part is not None]
        unit_info = f"Law Unit: {'  '.join(unit_info_parts)}\n" if unit_info_parts else ""
        children_info = f"Contains {len(self.sectionChildren)} sub-units\n" if self.sectionChildren else ""
        references_info = f"Total References: {len(self.sectionReference)}" if self.sectionReference else ""

        # Combine all information into a single string
        return f"{unit_info}{children_info}{references_info}"

    def get_leaf_nodes(self, collection: Union[List["LawTree"], Dict[str, "LawTree"]] = None,
                       return_as_list: bool = False, keyword: Union[str, List[str]] = None,
                       as_reference: bool = False) -> Union[List["LawTree"], Dict[str, "LawTree"]]:
        """
        Recursively find all leaf nodes in the given LawTree structure and return them as either a list or a dictionary.

        Args:
        - node (LawTree): The current node being inspected.
        - collection: The collection used to accumulate leaf nodes, automatically determined based on return_as_list.
        - return_as_list (bool, optional): If True, returns a list of LawTree objects; otherwise, returns a dictionary.

        Returns:
        - A list or a dictionary of LawTree objects, depending on return_as_list.
        """
        if isinstance(keyword, str):
            keyword = [keyword]
        if collection is None:
            collection = [] if return_as_list else {}

        if not self.sectionChildren:
            if return_as_list:
                collection.append(self)
            else:
                collection[self.sectionNo] = self
        else:
            if as_reference and self.sectionType == "มาตรา":
                if return_as_list:
                    collection.append(self)
                else:
                    collection[self.sectionNo] = self
            for child in self.sectionChildren:
                if keyword:
                    for key in keyword:
                        if key in child.sectionName:
                            child.get_leaf_nodes(collection=collection,
                                            return_as_list=return_as_list,
                                            as_reference=as_reference)
                else:
                    child.get_leaf_nodes(collection=collection,
                                           return_as_list=return_as_list,
                                           as_reference=as_reference)
        return collection
    
    @classmethod
    def from_filename(cls, filename: str) -> "LawTree":
        """
        A class method to create a LawCollection instance from a given filename.

        Parameters:
            filename (str): The name of the file to load the LawCollection from.

        Returns:
            LawCollection: A new LawCollection instance created from the loaded file.
        """
        return load_with_pickle(filename)
    
    def save_lawunit(self, lawunit_dir: str = None, save_json: bool = False,
                     save_pickle: bool = True) -> None:

        if not lawunit_dir:
            logging.warning(f"No directory provided. Using default path: {lawunit_dir}")
            lawunit_dir = lawunit_dir

        if not os.path.exists(lawunit_dir):
            logging.warning(f"Path not exist, creating path...")
            os.makedirs(lawunit_dir)
            
        filename = re.sub(r"[ก-๙]+", "", self.lawCode)
        if save_json:
            logging.info(f"Saving {filename}.json")
            save_path = os.path.join(lawunit_dir, f"{filename}.json")
            # Convert and save to JSON
            save_to_json(self, save_path)

        if save_pickle:
            logging.info(f"Saving {filename}.pkl")
            save_path = os.path.join(lawunit_dir, f"{filename}.pkl")
            # Serialize and save using pickle
            save_with_pickle(self, save_path) 

class LawCollection:
    """A collection of LawTree objects with additional methods for working with them."""
    def __init__(self, law_units: Union[List[LawTree], LawTree]) -> None:
        if isinstance(law_units, list):
            if all(isinstance(item, LawTree) for item in law_units):
                self.law_units = law_units
            else:
                raise ValueError("law_units must be an instance of LawTree or list of LawTree")
        elif isinstance(law_units, LawTree):
            self.law_units = [law_units]
        else:
            raise ValueError("law_units must be an instance of LawTree or list of LawTree")
            
        
    def __repr__(self):
        return f"LawCollection(law_units={self.law_units})"

    def __str__(self):
        summary_info = []
        for law_unit in self.law_units:
            max_depth = self.get_max_depth(law_unit)
            leaf_nodes = len(LawTree.get_leaf_nodes(law_unit, return_as_list=True))
            summary_info.append(f"Law Type: {law_unit.lawType}\tName (Thai): {law_unit.nameTh}\tName (English): {law_unit.nameEn}\tLaw Code: {law_unit.lawCode}\tTotal Levels: {max_depth}\tTotal Leaf Nodes: {leaf_nodes}")
        return f'Law Collection containing {len(self.law_units)} LawTree objects:\n' + '\n'.join(summary_info)

    def get_max_depth(self, law_unit):
        """
        Recursively calculates the maximum depth of the hierarchy starting from the given LawTree.
        """
        if not law_unit.sectionChildren:
            return 1
        else:
            return 1 + max(self.get_max_depth(child) for child in law_unit.sectionChildren)

    def __getitem__(self, index) -> None:
        """Allow indexing to access individual LawTree objects."""
        return self.law_units[index]

    def __len__(self)  -> None:
        """Return the number of LawTree objects in the collection."""
        return len(self.law_units)
    
    @classmethod
    def from_dir(cls, directory: str, mode: str = "json") -> "LawCollection":
        """
        Create a LawCollection instance from a directory containing lawunit files.
        
        Args:
            directory (str): The path to the directory containing the lawunit files.
        
        Returns:
            LawCollection: A LawCollection instance created from the lawunit files.
        """
        def load_json_to_lawtree(filepath: str):
            """
            Loads a JSON file containing LawTree data and returns a LawTree object.

            Args:
                filepath (str): The path to the JSON file.

            Returns:
                LawTree: The LawTree object constructed from the JSON data.
            """
            data = load_from_json(filepath)
            return build_lawtree_from_dict(data)

        def build_lawtree_from_dict(data: dict):
            """
            Recursively builds a LawTree object from a nested dictionary.

            Args:
                data (dict): The dictionary representing LawTree data.

            Returns:
                LawTree: The LawTree object constructed from the dictionary.
            """
            law_tree = LawTree(
                lawType=data.get("lawType"),
                nameTh=data.get("nameTh"),
                nameEn=data.get("nameEn"),
                lawCode=data.get("lawCode"),
                sectionType=data.get("sectionType"),
                sectionNo=data.get("sectionNo"),
                sectionId=data.get("sectionId"),
                sectionLabel=data.get("sectionLabel"),
                sectionContent=data.get("sectionContent"),
                sectionClause=data.get("sectionClause"),
                sectionName=data.get("sectionName"),
                sectionKeyword=data.get("sectionKeyword"),
                sectionSummary=data.get("sectionSummary"),
                sectionReference=data.get("sectionReference"),
            )

            if "sectionChildren" in data:
                law_tree.sectionChildren = [build_lawtree_from_dict(child) for child in data["sectionChildren"]]

            return law_tree
        
        
        if mode.lower() == "json":
            filenames = [filename for filename in os.listdir(directory)
                        if filename.endswith(".json")]
            law_units = [load_json_to_lawtree(os.path.join(directory,filename)) for filename in filenames]
        elif mode.lower() == "pickle":
            filenames = [filename for filename in os.listdir(directory)
                        if any(filename.endswith(ext) for ext in ['.pickle', '.pkl'])]
            law_units = [load_with_pickle(os.path.join(directory,filename)) for filename in filenames]
        else:
            raise ValueError("Invalid mode. Only 'json' or 'pickle' is supported.")
        
        return cls(law_units=law_units)
    
    @classmethod
    def from_filenames(cls, filenames: List[str]) -> "LawCollection":
        """
        A class method to create a LawCollection instance from a given filename.

        Parameters:
            filename (str): The name of the file to load the LawCollection from.

        Returns:
            LawCollection: A new LawCollection instance created from the loaded file.
        """
        filenames = [filename for filename in filenames
                     if any(filename.endswith(ext) for ext in ['.pickle', '.pkl'])]

        law_units = [load_with_pickle(filename) for filename in filenames]
        
        return cls(law_units=law_units)
    
    def merge(self, lawcollection: "LawCollection") -> "LawCollection":
        """
        Merge two LawCollection instances into a new LawCollection instance.
        """
        if isinstance(lawcollection, LawCollection):
            return LawCollection(law_units=self.law_units + lawcollection.law_units)
        else:
            raise ValueError("lawcollection must be an instance of LawCollection")
        
    
    def add_lawunit(self, lawunit: Union[LawTree, List[LawTree], "LawCollection"]) -> None:
        """
        Add a LawTree object or a list of LawTree objects to the collection.

        Args:
            lawunit (LawTree or List[LawTree]): The LawTree object(s) to add to the collection.

        Returns:
            None

        Raises:
            ValueError: If ``lawunit`` is not an instance of LawTree or a list of LawTree objects.
        """
        if not isinstance(lawunit, LawTree):
            if isinstance(lawunit, list):
                if all(isinstance(item, LawTree) for item in lawunit):
                    self.law_units.extend(lawunit)
                else:
                    raise ValueError("lawunit must be an instance of LawTree or list of LawTree")
            else:
                raise ValueError("lawunit must be an instance of LawTree or list of LawTree")
        else:
            self.law_units.append(lawunit)

    def save_lawunit(self, lawunit_dir: str = None, save_json: bool = False,
                     save_pickle: bool = True, show_progress: bool = False) -> None:
        """
        Saves the law units to a specified directory in either JSON or pickle format.
        
        Args:
            lawunit_dir (str, optional): The directory to save the law units to. Defaults to None.
            save_json (bool, optional): Whether to save the law units in JSON format. Defaults to False.
            save_pickle (bool, optional): Whether to save the law units in pickle format. Defaults to True.
            show_progress (bool, optional): Whether to display a progress bar while saving the law units. Defaults to False.
        
        Returns:
            None
        
        Raises:
            None
        """
        if not lawunit_dir:
            logging.warning(f"No directory provided. Using default path: {lawunit_dir}")
            lawunit_dir = lawunit_dir

        if not os.path.exists(lawunit_dir):
            logging.warning(f"Path not exist, creating path...")
            os.makedirs(lawunit_dir)

        iterator = tqdm(self.law_units, desc="Saving LawTree...", unit="doc",
                        leave=True, ncols=100, colour='blue') if show_progress else self.law_units
        
        for idx, lawunit in enumerate(iterator):
            filename = str(idx) + re.sub(r"[ก-๙]+", "", lawunit.lawCode)
            if save_json:
                logging.info(f"Saving {filename}.json")
                save_path = os.path.join(lawunit_dir, f"{filename}.json")
                # Convert and save to JSON
                save_to_json(lawunit, save_path)

            if save_pickle:
                logging.info(f"Saving {filename}.pkl")
                save_path = os.path.join(lawunit_dir, f"{filename}.pkl")
                # Serialize and save using pickle
                save_with_pickle(lawunit, save_path) 
                
    def as_vectorstoreindex(self) -> None:
        """Convert the LawCollection to a Vector Store Index."""
        raise NotImplemented("LawCollection.as_vectorstoreindex() is not implemented yet.")