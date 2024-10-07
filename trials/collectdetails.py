import json

# Load the JSON file
with open('menu.json') as f:
    data = json.load(f)

# Function to collect information from all nodes and print each level's text
def collect_tasks(node, level=[]):
    tasks = []
    if isinstance(node, list):  # Iterate over the list of task entries
        for item in node:
            task_info = {
                "task": item.get("task"),
                "description": item.get("description"),
                "artifact": item.get("artifact"),
                "tool": item.get("tool"),
                "artefact-locations": item.get("artefact-locations", [])
            }
            tasks.append((level, task_info))
    elif isinstance(node, dict):  # Handle nested dictionaries
        for key, sub_node in node.items():
            new_level = level + [key]  # Track the path down the hierarchy
            tasks.extend(collect_tasks(sub_node, new_level))  # Recurse into all nodes
    return tasks

# Collect tasks from the root of the data
all_tasks = collect_tasks(data)

# Display the collected tasks along with level text
for level, task in all_tasks:
    print(f"Path: {' > '.join(level)}")  # Print the path to the task
    print(f"Task: {task['task']}")
    print(f"Description: {task['description']}")
    print(f"Artifact: {task['artifact']}")
    print(f"Tool: {task['tool']}")
    print(f"Artefact Locations: {', '.join(task['artefact-locations'])}")
    print("-" * 40)
