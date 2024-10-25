import json
import pickle

def law_unit_to_dict(law_unit):
    """Recursively convert LawUnit objects into dictionaries."""
    return {
        "lawType": law_unit.lawType,
        "nameTh": law_unit.nameTh,
        "nameEn": law_unit.nameEn,
        "lawCode": law_unit.lawCode,
        "sectionType": law_unit.sectionType,
        "sectionNo": law_unit.sectionNo,
        "sectionId": law_unit.sectionId,
        "sectionLabel": law_unit.sectionLabel,
        "sectionContent": law_unit.sectionContent,
        "sectionClause": law_unit.sectionClause,
        "sectionName": law_unit.sectionName,
        "sectionChildren": [law_unit_to_dict(child) for child in law_unit.sectionChildren],
        "sectionKeyword": law_unit.sectionKeyword,
        "sectionSummary": law_unit.sectionSummary,
        "sectionReference": law_unit.sectionReference,
        "lawSectionReference": law_unit.lawSectionReference,
    }

def save_to_json(law_unit, filename):
    """Save the LawUnit structure to a JSON file with hierarchical indentation."""
    law_unit_dict = law_unit_to_dict(law_unit)
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(law_unit_dict, file, ensure_ascii=False, indent=4)  # Use indent=4 for pretty printing
        
def load_from_json(filepath):
    """Load LawUnit json file"""
    with open(filepath, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data

def save_with_pickle(law_unit, filename):
    """Serialize the LawUnit structure using pickle."""
    with open(filename, "wb") as file:
        pickle.dump(law_unit, file)

def load_with_pickle(filepath):
    """Load LawUnit object"""
    with open(filepath, "rb") as file:
        data = pickle.load(file)
    return data