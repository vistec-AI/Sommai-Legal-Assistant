from typing import List, Callable, Dict, Any

def visualize_retrieved_nodes(nodes: List[Callable]) -> List[Dict[str, Any]]:
    """
    Visualizes the retrieved nodes by creating a DataFrame from the given nodes.

    Parameters:
    - nodes: a list of nodes to visualize

    Returns:
    - List of details of nodes
    """
    result_nodes = []
    for node in nodes:
        node_text = node.node.get_text()
        node_text = node_text.replace("\n", " ")
        law_name = node_url = node.node.metadata["law_name"]
        node_url = node.node.metadata["url"]
        law_code = node.node.metadata["law_code"]

        result_dict = {"score": node.score, "text": node_text, "law_name": law_name, "url": node_url, "law_code": law_code}
        result_nodes.append(result_dict)

    return result_nodes