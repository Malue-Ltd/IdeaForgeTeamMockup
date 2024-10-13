import xmltodict
import json

def opml_to_jstree_format(opml_dict):
    def process_node(node):
        """Recursively process nodes to jsTree format."""
        jstree_node = {"text": node.get("@text", "Untitled Node")}
        children = node.get("outline")
        
        if isinstance(children, list):
            # Multiple child nodes
            jstree_node["children"] = [process_node(child) for child in children]
        elif isinstance(children, dict):
            # Single child node (not a list)
            jstree_node["children"] = [process_node(children)]
        
        return jstree_node

    # Start processing from the root node
    root_node = opml_dict["opml"]["body"]["outline"]
    return [process_node(root_node)] if isinstance(root_node, dict) else [process_node(item) for item in root_node]

# Load OPML file
with open("opml/ExampleIdeaForgeProcess.opml", "r") as file:
    opml_content = xmltodict.parse(file.read())

# Convert OPML to jsTree compatible JSON
jstree_data = opml_to_jstree_format(opml_content)

# Output to JSON file
with open("opml/jstree_data.json", "w") as json_file:
    json.dump(jstree_data, json_file, indent=2)

print("OPML converted to jsTree JSON format!")
