import json
import os
import re
import subprocess
import markdown
from flask import Flask, url_for, request, Response , render_template , make_response
import requests 
# Sample JSON path (you can replace it with the actual path)
path = os.path.dirname(os.path.realpath(__file__))
json_file = f'{path}/menu.json'
note_file = 'initialteam.md'
# Load the JSON structure
with open(json_file, 'r') as f:
    menu_structure = json.load(f)

# command = [r"mmdc.cmd", "-i", f"{path}/artefacts/{note_file}", "-o", f"{path}/artefacts/out_{note_file}"]
# # Run the command and capture the output
# result = subprocess.run(command, capture_output=True, text=True)

# with open(f"{path}/artefacts//out_{note_file}", 'r' ) as note:
#     html = markdown.markdown(note.read(),extensions=['extra'])
#     note_content = html
note_content = 'empty note'   
   
# Define the generate_menu_html function
def generate_menu_html(structure):
    # Helper function to recursively build the tree menu
    def build_tree(data):
        html_content =  '<nav class="navbar-default navbar-static-side" role="navigation">'
        html_content += '<div class="sidebar-collapse">'
        html_content += '<div class="tree-menu">'
        for key, value in data.items():
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

def clean_string(stringToBeCleaned):
    return (re.sub(r'[^a-zA-Z0-9]', '', stringToBeCleaned)).upper()

def extract(data, stage, step):
    main_pane_contents= []
    for key, value in data.items():
            if isinstance(value, dict):  # If it's another dictionary, go deeper               
                for sub_key, sub_value in value.items():
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
                                                                'artefact-locations' : task["artefact-locations"]                                                           
                                                                })

    return main_pane_contents                        

def generate_main_pane_items(stage, step):
    main_pane_contents = extract(menu_structure, stage, step)
    zindex = 0
    idSeq = 0
    ypos = 10
    xpos = 10
    html_content = '<div id="main-pane" style="position: relative;">'
    for artifactRecord in main_pane_contents:
        matchItem = artifactRecord['tool']
        description = artifactRecord['description']
        match matchItem:
            case 'MALUE_NOTE' | 'MALUE_FEED' | 'MALUE_CONTACTS' | 'MALUE_CONTACT': 
                location = path + '\\static\\documents\\' + artifactRecord['artefact-locations'][0]
                try:
                    with open(location, 'r') as f:
                            note_content = f.read()
                            note_content = markdown.markdown(note_content,extensions=['extra'])
                except:
                    note_content = ''  
                html_content += f'<div class="tool-wrapper" id="note{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
                html_content += f'<fieldset>'
                html_content += f'                    <legend>Notes - {description}</legend>'
                html_content += f'                    <textarea style="height: 100%;width:100%;" id="mytextarea">'
                html_content += f'                    <div>{note_content}</div>'
                html_content += f'                    </textarea>'
                html_content += f'</fieldset>'
                html_content += f'</div>'

            case 'MALUE_PDF_VIEWER' :
                location = artifactRecord['artefact-locations'][0]
                html_content += f'<div class="tool-wrapper" id="pdf{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width: 50%; overflow: hidden;">'
                html_content += f'<fieldset>'
                html_content += f'                    <legend>PDF - {description}</legend>'
                html_content += f'                    <embed src="{location}#zoom=page-fit"'
                html_content += f'                    height="100%" width="500" type="application/pdf" >'
                html_content += f'</fieldset>'
                html_content += f'</div>'
                
            case 'MALUE_DOCUMENT' :
                location = artifactRecord['artefact-locations'][0]
                html_content += f'<div class="tool-wrapper" id="doc{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
                html_content += f'<fieldset>'
                html_content += f'                    <legend>Document</legend>'
                html_content += f'                    <iframe src="{location}"></iframe>'
                # html_content += f'                    width="100%" height="100%" >'
                html_content += f'</fieldset>'
                html_content += f'</div>'

            case 'MALUE_CANVAS':
                location = artifactRecord['artefact-locations'][0]
                
                html_content += f'<div class="tool-wrapper" id="canvas{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
                html_content += f'<fieldset>'
                html_content += f'                    <legend>Canvas  {description}</legend>'
                html_content += f'                    <iframe width="768" height="432" src="https://miro.com/app/live-embed/uXjVMzWlxxY=/?moveToViewport=-3874,-2438,7747,4875&embedId=397718520920&autoplay=true&embedAutoplay=true" frameborder="0" interaction=off scrolling="no" allow="fullscreen; clipboard-read; clipboard-write" allowfullscreen></iframe>'
                html_content += f'</fieldset>'
                html_content += f'</div>'

            case 'MALUE_WEB_VIEWER':
                location = artifactRecord['artefact-locations'][0]
                location = 'http://localhost:5000/proxy'
                html_content += f'<div class="tool-wrapper" id="web{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:500px; width:50%">'
                html_content += f'<fieldset>'
                html_content += f'                    <legend>Website  {description}</legend>'
                html_content += f'                    <iframe src="{location}" width="100%" height="100%"></iframe>'
                html_content += f'</fieldset>'
                html_content += f'</div>'
                
            case _ :
                location = artifactRecord['artefact-locations'][0]
                html_content += f'<div class="tool-wrapper" id="unknown{idSeq}" style="z-index: {zindex};  top: {ypos}px; left:{xpos}px; height:100px; width:500px">'
                html_content += f'<fieldset>'
                html_content += f'                    <legend>{matchItem} Not Supported or not found </legend>'
                html_content += f'                    <p>{description}</p>'
                html_content += f'                    <p>{location}</p>'
                html_content += f'</fieldset>'
                html_content += f'</div>'

        ypos += 50
        xpos += 50 
        if xpos > 400:
            xpos = 20
        idSeq += 1
        zindex += 1
    html_content += f'</div>'
    return html_content

def generate_html_document(menu_html, items_html, note_content):
    data = {
        "menu_html" : menu_html, 
        "items_html" : items_html, 
        "note_content" : note_content
    }
    response = make_response(render_template("main.html", **data))
    # response.headers["Content-Security-Policy"] = "default-src 'self';"
    return response
    
def generate_document_list_item(stage, step, main_pane_contents):
    data = {
        "stage": stage,
        "step": step,
        "main_pane_contents" : main_pane_contents
    }
    return render_template("document-list.html", **data)


#################################################################################
# Main program and routes

app = Flask(__name__)
SITE_NAME = 'http://gov.uk/'

@app.route('/proxy', defaults={'path': ''},methods=['GET','POST','DELETE'])
@app.route('/proxy/<path:path>',methods=['GET','POST','DELETE'])
def proxy(path):
    global SITE_NAME
    if request.method=='GET':
        resp = requests.get(f'{SITE_NAME}{path}')
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in  resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method=='POST':
        resp = requests.post(f'{SITE_NAME}{path}',json=request.get_json())
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method=='DELETE':
        resp = requests.delete(f'{SITE_NAME}{path}').content
        response = Response(resp.content, resp.status_code, headers)
        return response

@app.route('/')
def show_menu():
    # Call the generate_menu_html function and return the result
    items_html = generate_main_pane_items('','')
    menu_html = generate_menu_html(menu_structure)
    html_document = generate_html_document(menu_html,items_html,note_content)
    return html_document

@app.route('/document-list')
def get_document_list():
    stage = request.args.get('stage')
    step = request.args.get('step')
    # Return fresh HTML content for the div
    main_pane_contents = extract(menu_structure, stage, step)
     
    items_html = generate_document_list_item(stage, step, main_pane_contents)

    return items_html    

@app.route('/get-main-pane-contents')
def get_new_content():
    stage = request.args.get('stage')
    step = request.args.get('step')
    # Return fresh HTML content for the div
    items_html = generate_main_pane_items(stage, step)
    return items_html


if __name__ == '__main__':
    app.run(debug=True)
