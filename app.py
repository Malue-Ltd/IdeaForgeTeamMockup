
# %%
import json
import os
import re
# import subprocess
import markdown
from flask import Flask, url_for, request, Response , render_template , make_response
import requests 

zindex = 0
idSeq = 0
ypos = 10
xpos = 10

path = os.path.dirname(os.path.realpath(__file__))
json_file = f'{path}/menu.json'
note_file = 'initialteam.md'
# Load the JSON structure
with open(json_file, 'r') as f:
    menu_structure = json.load(f)

note_content = 'empty note'


def count_ids(obj : object) -> int:
    count = 0
    if isinstance(obj, dict):
        # Check if "id" is in the dictionary and count it if present
        my_dict: dict[str, str] = obj
        if "id" in my_dict:
            count += 1
        # Recursively count "id" in each value
        for value in my_dict.values():
            count += count_ids(value)
    elif isinstance(obj, list):
        # Recursively count "id" in each item of the list\
        my_list : list[str] = obj
        for item in my_list:
            count += count_ids(item)
    return count
# Function to mark an ID as used
def mark_as_used(id_value : int):
    global used_ids
    used_ids[int(id_value)] = True
# Function to check if an ID has been used
def is_used(id_value : int):
    global used_ids
    return used_ids[int(id_value)]
# Function to clear the usage indicator
def clear_usage(id_value : int):
    global used_ids
    used_ids[int(id_value)] = False
   
ids = count_ids(menu_structure ) 
used_ids = [False] * ids # Initially, all IDs are unused (False)



# command = [r"mmdc.cmd", "-i", f"{path}/artefacts/{note_file}", "-o", f"{path}/artefacts/out_{note_file}"]
# # Run the command and capture the output
# result = subprocess.run(command, capture_output=True, text=True)

# with open(f"{path}/artefacts//out_{note_file}", 'r' ) as note:
#     html = markdown.markdown(note.read(),extensions=['extra'])
#     note_content = html
   

  
# Define the generate_menu_html function
def generate_menu_html(structure : list[dict[str, str]] ) -> str:
    # Helper function to recursively build the tree menu
    def build_tree(data : list[dict[str, str]]): 
        html_content =  '<nav class="navbar-default navbar-static-side" role="navigation">'
        html_content += '<div class="sidebar-collapse">'
        html_content += '<div class="tree-menu">'
        for key , value in data.items():   # type: ignore
            if isinstance(value, dict):  
                for sub_key, sub_value in value.items():
                    html_content += f"""<h3 onclick="toggleMenu('{clean_string(sub_key)}','{sub_key}','')">{sub_key}</h3>"""

                    html_content += f"""<ul id="{clean_string(sub_key)}" class="collapsed">"""
                    for step_key, tasks in sub_value.items():
                        html_content += f"""  <li onclick="toggleMenu(\'{clean_string(step_key)}\',\'{sub_key}\',\'{step_key}\')">{step_key}"""
                        # html_content += f"""    <ul id="{clean_string(step_key)}" class="collapsed">"""
                        # html_content += '    </ul>'
                        html_content += '  </li>'
                    html_content += '</ul>'
        html_content += '</div>'
        html_content += '</nav>'

        return html_content
    return build_tree(structure)

def clean_string(stringToBeCleaned : str) -> str:
    return (re.sub(r'[^a-zA-Z0-9]', '', stringToBeCleaned)).upper()

def extract(data : dict[str, object], stage : str | None, step : str | None) -> list[dict[str, object]]:
    main_pane_contents : list[dict[str, object]] = []
    for _, value in data.items():
        value : dict[str,object]
        items  = value.items()           
        for sub_key, sub_value in items:
            
            sub_key : str
            sub_value : object
            if sub_key == stage or stage == "":
                print(sub_key)
                for step_key, tasks in sub_value.items():  
                    if step_key == step or step == "":      
                        for task in tasks:                                     
                            main_pane_contents.append({ 'stage':               sub_key,
                                                        'step':                step_key,
                                                        'task':                task["task"],
                                                        'description':         task["description"],
                                                        'artifact' :           task["artifact"],
                                                        'tool':                task["tool"],
                                                        'artefact-locations' : task["artefact-locations"],
                                                        'id' :                 task["id"] ,
                                                        'tooloutsideWorkbench':  task["tooloutsideWorkbench"]
                                                        })

    return main_pane_contents                        

def render_artifact_item(artifactRecord : dict[str,str] ,stage : str,step : str,id : int, zindex : int, idSeq : int,ypos : int, xpos : int):
    # if is_used(id):
    #     return ''
    html_content = '<div >'
    matchItem: str = artifactRecord['tool']
    description : str = artifactRecord['description']
    mark_as_used(id)
    match matchItem:
        case 'MALUE_NOTE' | 'MALUE_FEED' | 'MALUE_CONTACTS' | 'MALUE_CONTACT': 
            location = path + '\\static\\documents\\' + artifactRecord['artefact-locations'][0]
            try:
                with open(location, 'r') as f:
                        note_content = f.read()
                        note_content = markdown.markdown(note_content,extensions=['extra'])
            except:
                note_content = ''  
            html_content += f'<div class="tool-wrapper" id="note{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px;width:50%">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    Notes - {description}'
            html_content += f'                    <span class="close-icon" onclick="closeNote({idSeq})">❌</span>'
            html_content += f'                    <span class="close-icon" onclick="popoutWindow({idSeq})">➕</span>'

            html_content += f'                    </legend>'
            html_content += f'                    <textarea style="height: 100%;width:100%;" id="mytextarea">'
            html_content += f'                    <div>{note_content}</div>'
            html_content += f'                    </textarea>'
            html_content += f'</fieldset>'
            html_content += f'</div>'

        case 'MALUE_PDF_VIEWER' :
            location = artifactRecord['artefact-locations'][0]
            html_content += f'<div class="tool-wrapper" id="pdf{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width: 50%; ;">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    PDF - {description}'
            html_content += f'                    <span class="close-icon" onclick="closePdf({idSeq})">❌</span>'
            html_content += f'                    </legend>'
            html_content += f'                    <embed src="{location}#zoom=page-fit"'
            html_content += f'                    height="100%" width="500" type="application/pdf" >'

            html_content += f'</fieldset>'
            html_content += f'</div>'
            
        case 'MALUE_DOCUMENT' :
            location = artifactRecord['artefact-locations'][0]
            html_content += f'<div class="tool-wrapper" id="doc{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    Document - {description}'
            html_content += f'                    <span class="close-icon" onclick="closeDoc({idSeq})">❌</span>'
            html_content += f'                    </legend>'
            html_content += f'                    <iframe src="{location}"></iframe>'
            # html_content += f'                    width="100%" height="100%" >'
            html_content += f'</fieldset>'
            html_content += f'</div>'

        case 'MALUE_CANVAS':
            location = artifactRecord['artefact-locations'][0]
            
            html_content += f'<div class="tool-wrapper" id="canvas{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    Canvas - {description}'
            html_content += f'                    <span class="close-icon" onclick="closeCanvas({idSeq})">❌</span>'
            html_content += f'                    </legend>'
            html_content += f'                    <iframe width="768" height="432" src="https://miro.com/app/live-embed/uXjVMzWlxxY=/?moveToViewport=-3874,-2438,7747,4875&embedId=397718520920&autoplay=true&embedAutoplay=true" frameborder="0" interaction=off scrolling="no" allow="fullscreen; clipboard-read; clipboard-write" allowfullscreen></iframe>'
            html_content += f'</fieldset>'
            html_content += f'</div>'

        case 'MALUE_WEB_VIEWER':
            location = artifactRecord['artefact-locations'][0]
            location = f'http://localhost:5000/proxy/{location}'
            html_content += f'<div class="tool-wrapper" id="web{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    Website - {description}'
            html_content += f'                    <span class="close-icon" onclick="closeWeb({idSeq})">❌</span>'
            html_content += f'                    </legend>'
            html_content += f'                    <iframe src="{location}" width="100%" height="100%"></iframe>'
            html_content += f'</fieldset>'
            html_content += f'</div>'
        case 'MALUE_PLANNER':
            location = artifactRecord['artefact-locations'][0]
            html_content += f'<div class="tool-wrapper" id="planner{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    Planner - {description}'
            html_content += f'                    <span class="close-icon" onclick="closePlanner({idSeq})">❌</span>'
            html_content += f'                    </legend>'
            html_content += f'                    <div id="chart" style="background: white;"></div>'
            
            html_content += f'</fieldset>'
            html_content += f'</div>'

        case 'MALUE_PROCESS':
            location = artifactRecord['artefact-locations'][0]
            xpos = ypos = 0
            html_content += f'<div class="tool-wrapper" id="process{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:100%; ">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    Process - {description}'
            html_content += f'                    <span class="close-icon" onclick="closeProcess({idSeq})">❌</span>'
            html_content += f'                    </legend>'
            html_content += f'                    <div >Process</div>'
            
            html_content += f'</fieldset>'
            html_content += f'</div>'
        case _ :
            location = artifactRecord['artefact-locations'][0]
            html_content += f'<div class="tool-wrapper" id="unknown{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:100px; width:500px">'
            html_content += f'<fieldset>'
            html_content += f'                    <legend style="display: flex; justify-content: space-between; align-items: center;">'
            html_content += f'                    {matchItem} Not Supported or not found '
            html_content += f'                    <span class="close-icon" onclick="closeUnsupported({idSeq})">❌</span>'
            html_content += f'                    </legend>'
            html_content += f'                    <p>{description}</p>'
            html_content += f'                    <p>{location}</p>'
            html_content += f'</fieldset>'
            html_content += f'</div>'
    html_content += '<div>'
    return html_content

def generate_html_document(menu_html : str, items_html : str, note_content : str):
    data = {
        "menu_html" : menu_html, 
        "items_html" : items_html, 
        "note_content" : note_content
    }
    
    # response.headers["Content-Security-Policy"] = "default-src 'self';"
    return render_template("main.html", **data)
    
def generate_document_list_item(stage : str, step : str, main_pane_contents : list[dict[str,object]]):
    data : dict[str,object] = {
        "stage": stage,
        "step": step,
        "main_pane_contents" : main_pane_contents
    }
    temp = render_template("document-list.html", **data) 
    return temp

#################################################################################
# Main program and routes

app = Flask(__name__)

app.jinja_env.globals ['render_artifact_item'] = render_artifact_item  # type: ignore
app.jinja_env.globals['generate_document_list_item'] = generate_document_list_item # type: ignore



@app.route('/proxy/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/proxy/<path:path>', methods=['GET','POST','DELETE'])
def proxy(path): # type: ignore
    # Construct the URL to the third-party site
    target_url = f"{request.path}"
    target_url = target_url[7:]
    # Forward request headers and data as needed
    headers = {key: value for key, value in request.headers if key != 'Host'}
    if request.method == 'POST':
        resp = requests.post(target_url, headers=headers, data=request.get_data(), cookies=request.cookies)
    else:
        resp = requests.get(target_url)

    # Modify headers to allow embedding
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
    headers.append(('x-frame-options', 'ALLOWALL'))
    headers.append(('content-security-policy', ''))

    # Return the response to the client
    return Response(resp.content, resp.status_code, headers)

@app.route('/')
def show_menu():
    items_html = '<div style="position: relative;height: 100%;overflow-y: hidden; ">'
    items_html += '<div id="list-pane"  class="scrollable-div doclist-content"style="position: relative;">'
    items_html += '</div>'
    items_html += '<div id="main-pane" style="position: relative;height: 100vh;overflow-y: hidden; border: solid black 3px; ">'
    
    items_html += '<iframe  src="https://xmind.ai/embed/DASmVuOe?sheet-id=1df9858b-5171-48dc-97f2-e5054bcbdc99" width="100%" height="900px" frameborder="0" scrolling="no" allow="fullscreen"></iframe>'
   
    items_html += '</div>'
  
    menu_html = generate_menu_html(menu_structure)
    html_document = generate_html_document(menu_html,items_html,note_content)
    return html_document

@app.route('/artifact-details')
def get_artifactData():
    stage = request.args.get('stage')
    step = request.args.get('step')
    id   = request.args.get('id')
    # Return fresh HTML content for the div
    main_pane_contents  = extract(menu_structure , stage, step) # type: ignore
    
    artifactRecords : dict[str,object] = [item for item in main_pane_contents if item.get("id") == int(id)][0] # type: ignore
    
    global zindex, idSeq, ypos, xpos
    items_html = render_artifact_item(artifactRecords,stage,step,id,zindex,idSeq,ypos,xpos) # type: ignore
    zindex += 1
    idSeq += 1
    ypos += 50
    xpos += 150
    return items_html    

@app.route('/document-list')
def get_document_list():
    global zindex, idSeq, ypos, xpos, menu_structure
    zindex = 0
    idSeq = 0
    ypos = 10
    xpos = 150
    stage : str | None = request.args.get('stage')
    step  : str | None = request.args.get('step')
    # Return fresh HTML content for the div
    main_pane_contents : list[dict[str, object]] = extract(menu_structure, stage, step)
    
    items_html = generate_document_list_item(stage or '', step or '' ,  main_pane_contents )

    return items_html    

@app.route('/disposeOfArtifactDisplay')
def disposeOfArtifactDisplay():
    id : int = int(request.args.get('id') or '')
    clear_usage(id)
    return "Succss", 200

if __name__ == '__main__':
    app.run(debug=True)
