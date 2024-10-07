import json

# Load the JSON file
with open('menu.json') as f:
    data = json.load(f)


def extract(data, stage, step):
    for key, value in data.items():
            if isinstance(value, dict):  # If it's another dictionary, go deeper
                
                    for sub_key, sub_value in value.items():
                        if sub_key == stage:
                            print(sub_key)
                            for step_key, tasks in sub_value.items():  
                                if step_key == step or step == "":      
                                    for task in tasks: 
                                        print(f'Stage  {sub_key }')     
                                        print(f'  Step  {step_key} Task: {task["task"]}')                    
                                        print(f'    Task:                {task["task"]}')
                                        print(f'    description :        {task["description"]}')
                                        print(f'    artifact :           {task["artifact"]}')
                                        print(f'    tool:                {task["tool"]}')
                                        print(f'    artefact-locations : {task["artefact-locations"]}', [])
                                


stage = "Initiation"  # Define the path to the subtree
step  = "What's the Idea"
subtree = extract(data, stage, step)


print(subtree)