import json

def extract_subtree(data, path):
    """
    Extracts a subtree from a JSON object based on a given path.

    :param data: The JSON object (parsed as a dictionary).
    :param path: A list of keys defining the path to the subtree.
    :return: The subtree if found, or None if any key in the path is not found.
    """
    subtree = data
    try:
        for key in path:
            subtree = subtree[key]
    except (KeyError, TypeError):
        return None  # Path not found or incorrect structure
    return subtree

# Example usage:
json_data = {
    "a": {
        "b": {
            "c": {
                "d": "value"
            }
        }
    }
}

path = ["a", "b", "c"]  # Define the path to the subtree
subtree = extract_subtree(json_data, path)
print(subtree)
