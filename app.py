import json
import os
import re
import subprocess
import markdown
from flask import Flask, url_for, request
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
            if isinstance(value, dict):  # If it's another dictionary, go deeper
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
                                    # print(f'Stage  {sub_key }')     
                                    # print(f'  Step  {step_key} Task: {task["task"]}')                    
                                    # print(f'    Task:                {task["task"]}')
                                    # print(f'    description :        {task["description"]}')
                                    # print(f'    artifact :           {task["artifact"]}')
                                    # print(f'    tool:                {task["tool"]}')
                                    # print(f'    artefact-locations : {task["artefact-locations"]}', [])
                                    main_pane_contents.append({ 'stage':               sub_key,
                                                                'step':                step_key,
                                                                'task':                task["task"],
                                                                'description':         task["description"],
                                                                'artifact' :           task["artifact"],
                                                                'tool':                task["tool"],
                                                                'artefact-locations' : task["artefact-locations"]                                                           
                                                                })

    return main_pane_contents                        

def generate_html_items(stage, step):
    main_pane_contents = extract(menu_structure, stage, step)
    ypos = 0
    xpos = 0
    html_content = '<div id="main-pane" style="position: relative;">'
    for artifactRecord in main_pane_contents:
        matchItem = artifactRecord['tool']
        
        match matchItem:
            case 'MALUE_NOTE' | 'MALUE_FEED' | 'MALUE_CANVAS' | 'MALUE_CONTACTS' | 'MALUE_CONTACT': 
                location = path + '\\static\\documents\\' + artifactRecord['artefact-locations'][0]
                try:
                    with open(location, 'r') as f:
                            note_content = f.read()
                            note_content = markdown.markdown(note_content,extensions=['extra'])
                except:
                    note_content = ''  
                html_content += f'<fieldset id="note01" class="window" style="z-index: 3; top: {ypos}px; left: {xpos}px;">'
                html_content += f'                    <legend>Notes</legend>'
                html_content += f'                    <textarea style="height: 100%;width:800px;" id="mytextarea">'
                html_content += f'                    <div>{note_content}</div>'
                html_content += f'                    </textarea>'
                html_content += f'</fieldset>'
                ypos += 50
                xpos += 50
            case 'MALUE_PDF_VIEWER' :
                location = artifactRecord['artefact-locations'][0]
                
                html_content += f'<fieldset id="pdf01" class="window" style="z-index: 4; top: {ypos}px; left:{xpos}px;height:500px;width:50%">'
                html_content += f'                    <legend>PDF</legend>'
                html_content += f'                    <embed src="{location}#view=FitH"'
                html_content += f'                    width="100%" height="100%" type="application/pdf">'
                html_content += f'</fieldset>'
                ypos += 50
                xpos += 50
            # case 'MALUE_DOCUMENT' :
            #     location = artifactRecord['artefact-locations'][0]
                
            #     html_content += f'<fieldset id="pdf01" class="window" style="z-index: 4; top: {ypos}px; left:{xpos}px;height:500px;width:50%">'
            #     html_content += f'                    <legend>Document</legend>'
            #     html_content += f'                    <iframe src="{location}"'
            #     html_content += f'                    width="100%" height="100%" ><iframe>'
            #     html_content += f'</fieldset>'
            #     ypos += 50
            #     xpos += 50
            # case 'MALUE_WEB_VIEWER':
            #     location = artifactRecord['artefact-locations'][0]
            #     html_content += f'<fieldset id="pdf01" class="window" style="z-index: 4; top: {ypos}px; left:{xpos}px;height:500px;width:50%">'
            #     html_content += f'                    <legend>Website</legend>'
            #     html_content += f'                    <iframe src="{location}"'
            #     html_content += f'                    width="100%" height="100%"><iframe>'
            #     html_content += f'</fieldset>'
            #     ypos += 50
            #     xpos += 50
            case _ :
                pass
    html_content += f'</div>'
    return html_content


#     return f"""
# <div id="main-pane" style="position: relative;">
#                         main pane
#                         <fieldset id="miro1" class="window" style="z-index: 1; height: 200px; width: 500px ;top: 5px; left: 550px;">
#                             <legend>Canvas</legend>
#                              <iframe width="768" height="432" src="https://miro.com/app/live-embed/uXjVKozDgAA=/?moveToViewport=-2938,-2041,5601,4892&embedId=797928089089&embedAutoplay=true" frameborder="0" scrolling="no" allow="fullscreen; clipboard-read; clipboard-write" autoplay interaction=off allowfullscreen></iframe>
#                         </fieldset>
#                         <fieldset id="miro2" class="window" style="z-index: 1; height: 200px; width: 500px ;top: 5px; left: 550px;">
#                             <legend>Canvas</legend>
#                             <iframe frameborder="0" style="width:100%;height:673px;" src="https://viewer.diagrams.net/?tags=%7B%7D&lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&title=WorkflowArchitectureElsa2.drawio#R%3Cmxfile%3E%3Cdiagram%20name%3D%22Page-1%22%20id%3D%22WExiqHBwSb-j7HjDrdKM%22%3E7V1Zk5vIsv4t98ER5zzMBDvokVWAQCA2gd4QIEBiB4nl199C3W13t%2BTdnrbPuCfGgqKoKiozv8rMSpJ3KJsPy8avErUMo%2BwdAoXDO5R7hyAwjBHgZy4ZH0sgBH8oiZs0fCz7UGCmU%2FRU8bH0nIZR%2B6JiV5ZZl1YvC4OyKKKge1HmN03Zv6x2KLOXvVZ%2BHN0UmIGf3ZZu07BLHkoRFCU%2BXBCjNE6euiZw7OFK7j%2FVfnyUNvHDsn9WhPLvULYpy%2B7hKB%2FYKJun72liHu4TPnL1%2FciaqOi%2B5IYtyq%2FOftuJG3j5F24lXrdc%2F%2FXYysXPzo9P%2FDjYbnyagqY8F2E0NwK9Q5k%2BSbvIrPxgvtoDqoOypMszcAaDw0vUdCmYPjpL4wKU7cuuK3Nw4ZBmGVtmZXNtFA39iDoEoLztmvIUPbtCBFS0P8x3lEX3yBAwAc7z8uLvr4OaO2qiNp2en5ed3z07B5wYPT%2BPwvT5aVYGp%2FfP9Mg8zy7fzu3TRIHni4ZnRY9zvYzKPOqaEVR5vEo8kv2R8%2FEnNug%2FsBGBP5YlzziIIB8L%2FUfWjd83%2FYG44OCRvl9Ba%2FKG1rxi0qAEBf%2BbUQOe7RPEhz9P%2FN%2BMQhj8ikTYLYkQ9B6JfhaF4FtxtADagRKp6KLmME%2F8D6IQ9IpC0CsKQa8oBL2kEPScQvANhaAfQyGcekkhAr0jRP8ogfCb%2BY9CsGA8npZNl5RxWfgZ%2F6GUeQmgH%2BooZVk9zt4x6rrxEez8c1e%2BpBqYwGZ0n594c2N%2F40%2Bn3PBEoevZ%2BEQ%2Fv03eEygqQnpeEMFpURbRQ4mQzs9%2FrfxLsEZbnpsg%2BhQBHtenzm%2FiqPtUxcdleCbPJ1mtiTK%2FSy8v1%2FsfzzjInYUW6BAo%2FDAfRNbNi2HlFy%2B4i6jPs3oApvC6Ps5g3cT7%2FwD2BsOAnn7%2Be20CmhfMvw5%2BnmbjQ1Uxyi7RvBw%2Fu95emWy%2BCiPV8PzCQ6fzlaJscj97du3iN6kPfsGi7nfnZlbIPlkv8KuPVekfxXS%2BiEEPDw8BXgLw9hd4%2FCAt4ts7y6ZK%2FOKxSeShDEBI95f%2FoGbMxUE0Q%2BSzaykQuuKxJ%2BjpUa9XugY0dgDtP%2FV0FYcHWLlqjM%2B66csmfDmw922BZ9mfUtDc3OaDHvPXIzC9qHfF5Gsbd%2BZ37wen%2BIoQf70iMoLDD%2FR9fvDfZ48RRkHZAN4ti7%2B6JA1ORdQ%2Bjj0t0i596uF13WeE%2FmS9Z8N5US9M2yrzx6crWQpmD4H%2BL80rAG3%2BPONXYmel372a3yduBkfx%2FHu7tj2IAZCwB0l4qPZSUD4c%2FpsWQvhXWwixP3j2B8%2F%2B4NkfPPs20wuiPo9nyD%2BJZ8SbKPZD2rkfVHlw5j1RBBx%2F0Ornkyel%2Fr0xAP1NEcRLg2CxwD5jElzP9KhJwbTN6PJY%2BN402M%2B0f2EbzONsgbrdva5yLXxR6ZUnZ%2F4ThPdXnvxnyK%2FCrp83Np48jp8zNshfy9agfkNehhHyNS8jf3j5B%2FIy9la8fL0VTLg%2FPqtQlWnRtc9a1ueCZwsEuni5QECvnNuv62PQp%2BqDg4cRfJCq94%2Fy7YL23rP%2FNt4gIGkE%2Flxo4D8C8waepjcDf5NLdYvHSy5BoV3so6UJdX%2Fd7t%2F8oyz5EsM%2F56D8PTgBuaMG3J17%2BJdSA5DbzYTH%2FZ65dFs2J2DT9OCQB%2FNY%2Fru2fhaf3%2FmB%2F1F%2FCkLc86d82ony2v9BPBror81SKYx8cF0oAfuCX7Zs5p%2BnDb%2BPmKjfwwyvN4G7GUYYvwkeAYT8%2FRjm1UYUecdexRd3GAZFfxrHkG%2BtfGCvNHYIGPV%2FFJB%2FXmN%2Fwo5fZd15G%2FPzA2OS5Mt90j9M%2BQZa8a%2FGlIs3ZsoF8sJU%2B2uGS%2BIPZ76Bs%2B4X48wnBeGZ5qfSis2DIk5jv08RK%2Bd9nm5mJ3ye3FcxeBEc4hF5jxkWBIn6v2HMHfpqm3RBoTdq2j%2Bq1qO3NtgTcU2R560%2F5P0a8iLYr0be26ieJ%2FKuNYv%2FQ93vEl74ramLfhyZv9NC%2FrfR9kZy35y2t%2FErf2j7Y%2BSWwt6atvhHafvk7ppdZ1%2FiU6M%2B4lJTedPk10veeOY%2Fe2jzR%2FjP%2Fm0c9Bod3p6Dbr2x38pB76PSXrOQwPPcH%2B75AdwDQ698s%2BRbc8%2FtizY%2FnHt0Tvgo8zwUh%2BnlddF39%2BpI%2FPYTmPe%2B%2BEXff3j5K3iZ%2FNUsHOrn8%2FKWZ%2F7w8r%2BAl99c51%2F8A7is0Ov1H7XwpzDQm6uFT2rqz2QgSaWX%2FB84%2FN%2Fn5jdXU7GP%2B6ZZeu3Q5h%2F6fo8b5O3pe%2Buc5l2WV%2F6Q9Xt8E29P1luv9FYzuD9U%2FR6fwdurFrc%2BS127LsiQrknrPxuF30XeNzc9sFuHImfQ2zsKnaT9UbZ%2BAgO8tR8Fe%2BP4o3fo18Tl34kOEgQUfff7Rgdhj36s3y1vCHbrf3t4y%2FgGOPQmOkRgYoKo%2FUIEaRO%2Fmg9DQKG2m6PC%2F9deM34d53%2FvNWPqn4QB%2FHbb2fLb07v5pfELEKzmEzAPfZ48r3D9cDggwd0kayGxJ3Di3cska9jvh%2FPY67h88pbAMPKPUvitA02pm6h89DNofzfM9CXQo%2FeYaF4S0IfGP51a6osiUn8JaPnsOoK%2FXVD%2BN71Hi782X%2FFPv0eLL76z%2FmPE409975a43WB9C6H7RhG5H7X9TIIJ8jZU%2FJvehf8lwPyzIvUExW8lUjc8jRKvefrVYvEw0se7PjD7V7%2Fj%2FqqfxefecX89LuIz9UnqU%2FV%2Fkmze7pE8ajhsmVeAw9KyuKO90s0%2B7Rr%2F%2Bh7qV5q%2Ff%2FSiz%2BtF1JvrReQXZBp%2Bjq1PyZKvi%2F1THsv55DFFFvc%2BP9brt03zNAyvAP9k3%2BRDPGen%2FvshHzTy8Ds3Oz7A7Xw4zxt2dY1kaSU%2BDqIouyB57PY1C%2BHzf%2FdYiLj%2BPbLQqxdsrkvBL6HofE0e4%2Fuo84KVyDus9PPyGN9ubPxPsNLHGObjLPabodJrVqII%2FI1ZibjjXvml7PH7r9L%2FZnR%2FMiLeQwh0CyHYvVzo75eoH0%2F421ige2qKn8%2FTXezb6t0XZLW8n%2FvwebLB11EXd9WeL0zE8If%2FvpX%2FqDtuwPv8B%2F0A%2FrubKga9IewvvB3wS2gsz%2B3IT2Xf%2Bc3yNd1Ti59ZR3dQ5hZFvjoIDPpY8FkY%2BU9pYqwI4KDfvdhN%2BJKYsB%2Fzgs1%2FnvITtf%2F90ljKf8F2xiur7m7aIugnWXV3ufd2O4NLm%2Fk7PAikRsX5UY8K%2FIfl9KNL2RfsYP9mpHq98XTn6y8%2FLcHUXUq97Ycr5vye7wu%2BOSnL7ebzx9NY%2FBL88tk169dP8XMgkRVhZvqOGid8hbv%2Bubj8dRuCZiXXNeOV7QSl7XVMbVUWbTpP2Jw1%2FXphtrirBujZRfxu%2FnxXnvtFONeO0i653ntoynyem2vLz9LVtWPbRfOVa0PhFW%2By8cMNc66z%2FAF8QJPXxv8qmzAt%2FMfOHlp8SvsN2jm8LwySso1m5b67brKz78cbDf5sFjw2b4KR%2B2GbRIBo10oPHWWlHz508Z%2FAP7ePvZXgn330eDkK%2F3utfvUTAzA5%2BFew%2FFBp5rwo%2FPt%2BqPdrc%2BSuefIZx%2BmcFv2llD65QbLo0H1U5b8Hzy%2Fx4aUshuDRzg%2BqwDMj5EPpj1DrX0dU31Pr4TsgSyE%2FSS7ufhThx8TnXwXsK%2B3RT3xS4Kb5LzV%2Bb3PZf%2FMYPvKtgC%2B1l6EQLA3BvMHyJLxZWz7I3FWirwN6EKeXwnYV1llq07ka4PTsWuMF3vTv8eZasZi%2FrnDFsteXQf0ryHUPE5j47VWSryASPMzmQ%2F9zef%2FAQ9fjtkub8zM8uhnp319Jgs%2Fpx%2F%2B7gk%2FdcUnfFfwfoV01i1VUOIPqxXGUry9V0JyDt8m6%2BzU5vL4oBONzcRzP1DnkQ1TJN2ee%2FiK16e50v12qr%2Fs7rfArdR%2B%2BcRx9ZMv4G3ZdPzUhzxWy%2BZswAEWuUA5Ujzi%2BQuOPMcF%2BC68f9Zom8D9og92l0pvYYF%2BDEj8mt%2BDzUJaXMDF%2F1eGbcsR%2BO1SgvxhUYOgbQ8WdpFZATmd1yp9%2F%2FkUAgWK%2FHEK8yVeI3hQhqJd%2BIfhv6B%2FWJd44oPOzEZX%2FOEDcGrFPFkn7r4KH199c%2FGfh4X4GixvS3FDkaRckza9ftn9v1Cn%2BPsr0sk2vGuGzD7Nn8wXmvSV%2Ba7B9JJt%2FW81%2BfpQ7pMNMB%2BbaIf1UCj2VvHvYkAGm%2FcMpIlSzHsqmDqMZPbRaxiUN%2FtamnfB2DI5UDPzD6SztgV92sXmHMHgyV2FdRtq6Kk0zXgZOt%2FJGkO3U6sGxrUIZv3EMrNCQkEUNB94V4gW9TFZJU6bn0acsB7LCsPRKWLWwxthCYsphXNulxPrVZixL9iTsmi0jMNuQT2yGXvVxkhZ%2BrsfSdGH6IabXXsJkOCM04GjF%2BMsVjTLcKDVZARcBno1eMqEXRM%2Bjw%2FyUoDfwb%2BdLShAh00SReHEtYoYLKIfChNhVO2Yrm8GpMtYWxGCspmnFYmW2nbYtHL865YVqnnAmTpf1HtzDsatUgxBc1Rk0TBSDNhW%2FtxZZZdrOrhsvjiaWXpI3oOqiv5C2RIMjGVobihkdEHNlSlUfMmGrJ8uMHaggVskEim3IxXaKDG%2Bw1C5kUlKynoa4tBXPqDqOUCVxZe1lBpcSJu5xbK%2FaMky5pyXvTnkGxfMI5YzIYi2l%2FYabwAMmMuh3d4ITldoaZDD6gwjR%2BIU1vY3qEohuUYrhDSftojdJveERPDGKg4jIh33T1qmdy9tDqbmaxHRxeCh3KKEuICAZTGoOIX85SQeROcRJvt1m8rYlI%2Fgcdsd4wx2YiWqqNLLKTJTiJUOnoXACt4lNVqX2UXGzHBVPvcqmymVlnjqkEyOS3FTihJMDvRYw%2F0TTfWQT8aJs4G1hOdvzaPW6EfP0cdstzv5OR7ykP0PJKBm9x69o1QIPPyFNAzsZBA%2BcTbsr0YlWwOpaaDkU05IqNE6fuSy0ucTYSmICOWcaf1vmZFZHJyWWGYmlOZNrkb6yNh27hesgN%2Bg1LRyYPE%2Fy0ClXFXUR9jHNsyqqUUJvHM%2BkWEbSLl7vqwxPbX29J9eUsJ5FKxqcFDyzt770TD0z2m65appwBxWUUtrLM9JHJ2xM1cVKsA71cnEJdtCaWFqkTEBCXU1sZ1IqWdvCdK4vMuKwXeLCJMTkiK%2Fs%2BbO79TkNtLqs2QAvxWgmS%2BCv8tDSXVt1Z9Y7yWurYpt9SsmmcULNY9senQu5UM%2FnWqeo2JnWW2zVHC6RuHcza3vY4CVopc1Pm1buc2pPVMkuI3fBFqrd4Bgakd0cYTm74JSQLVOa3w22iO9bHYCdgMhWTVIJ5%2BgXrRb8S0UFY2AdFjGTjp6Ik7i62AqDkw0QxegQm3p1TSyOVOUKmbDA037aE%2FUuWBl7cYmaCgfaigG1e%2BtYqc2%2BWij4Go123Z6OGusIl%2F3aXCBELQAUZurCgJDM2qx4IQhyHj%2FazOg008BmkLeQ9IsJ%2Bf2uQoYmAMMkOhq2wsYKbBqa6I2PiULGdElhuZOpBv4OVHFr8djQ9Cw6Hlc5vqNV63bdT5SImKJYF4t%2BY7X2gYNpzqDVtkzLziR2WNIIvXcy9SgV0PVkY5JRTvEs98E67aNFD3GVNHWCiPCltpQNZ%2BMKKdAEaYbCu7E94NEQidFqFbqb4NBjmVmdxXQNrgMUrs1VtaMkZfTAwbSqFpgJAJve5KlEaF15EYh2HHeaJh5Ad2yK%2Bbbsr0jRYatxpwKEtYpEhQUtNk16ATElytYiedKW4pE1eG2Y9lIZi069B8QXtotYTTbHArtsgg5LBlpmZW1KIkRL2ETQLStkmFVMn2xcB1OfybSyFMlYtB4AlQ22%2B57b2yiH78xl47ciV8vYcVr2y80xbHeraNPt4RgL9yhhTkjFlYw3gNViSGHNn%2BcK8wNmC68XM%2Fuq7ORFQsmdN0KsINhao5EeFOuCjSxQjE32cbFUYqz3WZ6JAT1p7zJkgBUZnsZodcPNk8%2FQ2qfOlnTM6%2FyUXov1x2KJSbCNSRKkeO4Fnxf1XMGiky%2BcyBOyU0u1NxHpbIKRwMk5anIxSUQUUeqSirdwD2TV1ri6E1yc5zoTofF2XjY7KFl7uKbigoMS%2FEJQaAF1SGw3ipbAasFxS6UaADwDN%2FdGveLBczKEbyOtrRobGiqPFHaEE2of9%2BZCPMIibmx6PqY9lKXwYLWEfS%2BQ5MOUbGCB5ljWbzH5aHKytUFSv6w3O4le8QWqbSgJtTwD8JC0BvhpblhbIo5JodMV66Kbzqd0Gz2G0U7g6Jz18tVWZ50Fjxl%2BesYMmT7TTb9Bi1FctqZ%2BJFgj0LY4UrKjXcoWLcPcGbaoCdIIU12Ndp7u4gXdLHSPy41ZUBEnq0dTaCdRXJQnH4lprVzupWom6rx7Yw4Xrz30O%2FYkwfSelRAJ3HTI0Cqpo%2BJ4FoJiNPooFvZJwnMbeMaqk1LiNuayqaTtbT0fV3SiGxVr83kqL%2FpJxrx9aQ3EmdkGxoMaQIdWk1srq5hd9z687hEalmRKhi1Z78riNBgWwMnUaQ%2BLs2piPD3YGSzorqqtNWRjj40Szpzf0dbAVSxvFMIuhuDQFTRFPRbRxrEZXuqWrN3meUPkVRZMAWwzp9ihBUUgnURfLHZcRSCFrHqsN%2FR%2BcjL53tLGCGiOJbmVFaFbjdQEuHRiWFQmnazMl42GhdyBp13sSHpHG4dJ%2FEyE1e6QSxYWC6F0IJR1ZKkt7EEAMV02i6lR8ZlFtyx3FM4HZ3NRtRtiFarHWFl3iBYAtX95Ms71TsVyqOwjZztPUZbnl14%2FzTQh%2FW5TxNqZF0S0sNozMfqZwav1IUtXq743hSPMlxvUmfMUMTSPdikLuevlCj%2Fh4yaTqS28t5Ac7RVXsWm5LKrVJAPd0Adta07hMZlGcHghhsIRkohhTQ8z5GLJcjUxlUgS9DLbww3OlHJEUOqCYzhyhphFcjTsaAUO11i48zqy45HCivAEEig45moqWA%2B1GumecmjFyac2a6SozOyy25Vmo%2BK2djqUqLLUGHZVu2QS1aClaSciSLmnS6U6R8sDsV2ClWvJWT7FBOq2mk2FwyWXc%2BhkU3RbE7yxB4u%2BOSWHXM%2BmYeCky5KtV8domJf8GmACuSbgdsLgEDzmZUIuMRcv%2BzbqYNYNSH91KqSgSuLtRNnghu3k6msicws7jk7LhBQBbrI9teY6hAzdpZZFfKrHEZgeJhrWg1ACu1BYYzIfX2weGh0wGYKy6AZ2FrIrjIdWCYuz9nkwtb1QDuWIKxDJb3k5Ldbs5kSDronEKEdtlZaEtFzLhUa37slC2WUgpOdL5zocDDj4TGyBrcQUSUoqVcuk6SFP0uXxvFNB65mzziV%2BPPl8dQps%2FkS5l%2BO%2BYpaAXzK%2B4hHfMA7nfGU5DBQyG08etKSsznXlsWhHFrWepIqzrSyHT7EdXxHaAmtEf79t18Osryu1eoAKtEnLXWpFA6%2BzJmPWhBUth9BE1%2BZ%2BtTxuCYk2uCCTDHKNsUdwG5kpq6kg8N1iQZK8r4hCDwwAoZkMLQQPYp%2BP6jlHGsYT%2FKiSmZ5cHAcSLLSgzmXRxyVEGpGr5HvxknTFegFuuWwMJanN82ZJRLrQ8PZ5exGws4%2F2Rste3H2w34yU0JzDVAe8JJR7UblA6MEcd4Pur4bK8bxFgeIh6e5lfkNKDTPu9LxK%2B4vL7M9eSp23E1sMaBFE65RDoFMySUlzcHjfiMp5zNhRkFX4tCyRZlYtmUu80IvMmsZwv4YtfoBCfmxGbYEv93TMtNZWh%2BrhiHT83qC41imqjU%2FFQtwfXOlQescDetrByayYNOpKR7BdMA2T3hKeySe8tbpUWNVt6%2FZQ4mRRtSiMuMuFvdnU9GoF1XVpIQRhTCy8TmiV8MndMUEE3FqZ9BIG9q5YHJlcn%2BFegOEDPp7h%2BOCnqzhfghJHZ9rTqgkiLD9uGFdtYIOMZCSZZeDAKflMqNVlp1k8NVLNuXAgd%2BTCBrAaY%2BksG7IHcSMDa%2BeSOHy5nIARgFx4xbCRme%2BzLYfhQXvxgBG1RYXFiGFA%2F0d1SNlANbGPeXw5kagIuZzFKHDly04QhK62JZcymNHVRBh9MMJJtttVKeGeggsQ6Ti%2BGsmHkbLrc92I8KzkkI0ELVYrbKBI%2FoTD226WBMLZzCo%2BOXRTrhnFUTwa8tpxaq8y0ymoBf44Qyo5Dj5eHyrdk1y3SyL1EM53s0RLNKrPa1fM6h9M1hyYFJy7t0VlpW%2BpXTRGAclCLe6NHjmFwy4DUx3QtYGOhnhMxnO7O9PnlvLMC0866ak%2Fkb4crI2KlHfhlhMOsJlFiRP0JHjwWU9EYdNs1pYFGMm0yTDZbGBqVS0v51OxxgXbUUWE8DFn6zKRIG4HBKollgyBRqLiErwor7atXRZ2uOM4K4zaccXWAqnaOY%2BKAT1xrKk5TLSeHyViN0xgZtrDg02HcdEhh%2FEwzKY0NpixsOtmFpA27VhoI7F1c685dmG1TqvaMRYUf1Hwjt7NVVypaN0KIsJak%2FxBzfStsB0dxziNO%2F44P5biNITWWofpojunY3Z0DAQ1pK2%2BPcqUt7Uhsq0U7VxUs72EtiQH5tIXXMyiNrmlx3PpZjwRmAAwGff2FeSvRVIzZJ7MpUwl7Ey2CtyH1qv06PFCF7iriSZ1TDsjOFXoHUvmRD3zq1jScTDoU0NJjnvKL9pMZ4Jk0XZlJ2PgXqdCmLRiPJSbRtTF00YROQjgXDHKVLUyEQvY%2FBEltY0OpmqL%2B5W9y3CVDFphC6zYcIfRhaN7ZZ0cOgd02MCsFOo6De8Ryxw2a1LZkxZesPFDT8cjhNerwVWWR6PTz%2FOC1qrWZr0F1q8YgKWCofYjPlF%2BpOkYGgF7lVmEWOfUpyb2%2Bs48xZ5v%2B%2BkxPpQANYE1tcMpqiymYV6KFnCwnXWrMjZm5r34k%2BE2rHAm%2FAoINnw6GvFYpHHtzkt%2FvhK2mNPIdOFbjLyXLm61krrjRVeKWq1LXyeSDiz4a2DB9Z6dyxI02wLADpt7Ikw8rPXLMe6xszIzU3CqGU9BDERzXaAeCOcpz%2Bo62lwCxiF6eQ0tKqTGYEsICLW1LsvcJsiU92za1IKqYDqRtk4aoi9R4bCOs2UVtkNLZxLmngffXZYOmq28td%2B5xsavPaXnO5EtfVcAfCH44REC45PHVnByAhlFO0knFshiRJ%2FWQD8tYEw%2F1KJHICmyJ0KtgPeysztfWhQ9%2BGuTDYQLvYc9XDxDrjXrM1CUVw%2FU6gMXnybK3Z%2F27lJpGWxvMqJxVtKVMq%2BM%2BmltI2E%2BT4xhbAidwjCSn02XJUTDQRqIKhlmkV34Bi1dqtDs9eISivP8laMYV%2FOSEhDcAZUDVZJ7zeMiAd1tAdotOmgn2s5VEctDAZsF1FPI06I40gghJ9huKAk64BoZUkyIWeLEnISBOS%2FJLqeIMGNWMOEzaZRABJtEJUsqzbCDphbuVrWyLzPZ0WdXgb8gXUUfZsSsG83OhNhlCVY%2BnCmRWKKHkEI0eA4PYshwzOBJbiWY6ucFpPGILTe79HBeXo5oz9Tcojgc4xPvibzaa6shn9Upxlc3NGYceeu8mo8ZbHOkuYdjFtsk7O4g0GttxQS0NY5zgJ5Q1jk2kesTFbWb45aORUnos0DcKruudvyyx5ayo5ILW0gTWpOUBOuLVqhPvTARVR1IhXroDZYPWJLZ7cDSzzQhdkDhkUEJ6tQqrHleuhCixTOEjaEXXlCYmbVtt51t7mk%2FexsYrtwc0%2BuCAMvd%2BZKHajzsd%2BjBaKiJl2aHzqyKEcDqklg6SPf9PPfdPiYWMoDsBLfcvVEUKBKiJBw7lBO79Klvtxa3gOEtylGct16fkf25rbfZzEa7s3OyY1EtejOoRJGCINkRaXR73DiqGkhMb0ViMzPmMp6WyYOFf8IXbtNyHRNvNsfTqXV1Jq2Dvmkt1uA5WmfV4IRIW9N3nRM7qBBDScPJmyCDsHitGuQNMhyVhNVS3ywsXBzXUXU4JjkHN1B%2B5WCPncGIdPg9vNAsmcd5W2VO0oA82m%2FRZehzFZwISY0Sl0O3H%2BItN1tzlbKm3dY8q0sOD3x2y1xIs26T8zJx9Xwh52MstPDsZDAUwjxAe3VczAbmglm3EIut6t1RS8Zc5uKTxJU%2BAflJ6UxkN%2BzS%2BSaPzaKMciCmnyFu4cBUmMlyytj01rAdkZMW7ZabFdDLtnN1rEBZidlcLg%2Bz5vCJ6gsxFvVAs2WUAaNn9bmgKAqcCjvOXrPUAeDWZpJN1wN2MeKt9VzZw8IkrCVvZg63m3bSwMX0KFmoqIQtYjYn9rTibZjtJWfPazQnVTo79afK6PvWsAphULforEDGJwQrOXOSUZRBeAdXFcTjDY2NOYOSzqF79RrxrAdQHInVWj6QvDxrcNtgHp9jmAcXWpgnlrbPVt4UrNxx3ml7TIO8wFvkrJUyza16oc2UEfZWylV7v9BEi0H7NeScUSWRU39%2FlBQuWeiavYoyc1kl0irkqMlfWxhEHPQYHWi%2BwwNV4VlGgH0fZfrjqfRmk48kE4yhNpwyqvgMN7mPXsRVX5hjwCanY0D2HLVhp7NrVfZxqxiXXbEQThiDbNbTWcHHHbPHBm6iOT0%2BaqRk%2B%2Bpx552X60BnNbMgi%2BNxho0AOdrE2ahjf0QUuLBmDKRh%2BcLtAhtSDrS0w4LdvNTK7XJBeetTzphsWbvsPKaVR%2B3XE8HoxmhpwJRajYiB1zWczLDVng6WWrFLFJW8mkZoSYgnUb0gl%2FO49F2qzJvaB9b7em0gVE8tDtIZ2KW0Cc8Pr8t4AWz1whPR3X43gyIxYKhyHAZJGiSgrHJzLVGoJ9ARM2tAyaFZFz0t%2B10%2B4KQiZ%2BOELo4L3YTO6YFsjkdY4xgah4fgMK%2BgW0%2FYOPBBmT00tu0cQ5jUj8O%2BW1Czv3Rl17pge4sHPj4Eomjho6SwUyBmnR1KpuAV7jQcXIrDotzfmV4mD6yxpsoOKemaD9t5cyAJQmc1th0WTL51GYGtkLqc2ft%2BJoztsGuYE0sCPQf0UIGaFL7yMnWcVQoGiWgl9W0ENGIWM%2FIv6nFk1lsG47a%2B76%2BzVpExq4eFmKB3TQLtnTHJXQ7ql2D0DByP9K6dUDneUmupGy4st6UjesVQ3Qp0D7sSgYDFLPPWEE1x7NRtndKxkqwyncDc0zbRe2yx2hJCTaSOE62VpmtUt6ymlqHdCdqcFKsui6xqZyWXFuMhk9R2SSeMO6OVsDpTELFgVTEVQ7rklsjsslIR0fXxeW8Js1acxfWExHPSnj2ffbsukJPmZDu%2FTdyEpmW2mn1NbQidZwb1E1qnRJVQDMAvpzWb0gdM8olzWu59E4pQA5FNKqUXjolQ8kjRcrtKl9FOQXvksD1ztQA1DGaFsUcedaOsL9O2otpjsjbtYVXUJzdpFYLmLjFUtkiATSq8Z3oCTK9dWEOl6Qa9qa2JdArFPIcHeykFSn%2BSU1uHegeScSwqGZoMzfbY6HluawIG7VRRRZZMrG77JMgNyDWstGApQtqm3gwvo%2BjEiUd7%2B8XKA4C7xXZLKAHzv4ZsG2rUk17XBMOK%2B9pdDPEaaFiWwkODZSWdtD9DzTK%2B6NSyZNfekh1t9qgDSY64VMcOlh1E6GlrAGC6%2Fpm2oxkrnPUkad6a%2Fe32vzF48Tf8Ygccx5GbDXB08Td1uwOO%2FawdcOQ2T%2B6HV0NuXpkwr68Bfl02xOt%2B%2BK8VzPAyyuIHkBbBvyC04WclRrwbdPLWWfNQ8vvjmW%2FiqCDw91PjqL4o6umTcvQLv3l2P9AZemNGWSwWLyNaIRL7X2cW8m1D5L42rxrxKoIOJz%2BdJ%2B11ffIxyeNH679OOvqy%2Frvvzat2n%2FHvhPiXZfadIXmvEoSwrCDwcxoQvwkehWHODZGUTTqVRec%2FvQjyOiTsfTDZs%2FQhyAyoH%2FKOIz%2Fnxep72ajex%2FU%2BX7ne3%2FgVkDQ7f8r5%2FbMPhJyzP6llOGsI%2FP8D%3C%2Fdiagram%3E%3C%2Fmxfile%3E"></iframe>
#                              </fieldset>
#                          <fieldset id="canvas02" class="window" style="z-index: 1; height: 200px; width: 500px ;top: 5px; left: 550px;">
#                             <legend>Important table</legend>
#                             <table class="blueTable">
#                                 <thead>
#                                     <tr>
#                                         <th>Doctor</th>
#                                         <th>Patient</th>
#                                         <th>Visits</th>
#                                         <th>Waiting Time</th>
#                                     </tr>
#                                 </thead>
#                                 <tr>
#                                     <td>Dr Evan Pollock</td>
#                                     <td>Mr Smilley</td>
#                                     <td>7</td>
#                                     <td>4 hr</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Dr Evelyn Simms</td>
#                                     <td>Ethel Nitrate</td>
#                                     <td>6</td>
#                                     <td>2 hr</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Mr Super Villain</td>
#                                     <td>Craig McTaggart</td>
#                                     <td>14</td>
#                                     <td>1 hr</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Dr John John John</td>
#                                     <td>Mrs Malarkey</td>
#                                     <td>2</td>
#                                     <td>1.5 hr</td>
#                                 </tr>

#                             </table>
#                         </fieldset>
#                         <fieldset id="chart01" class="window" style="z-index: 2;top: 250px; left: 600px;">
#                             <legend>Chart of Things</legend>
#                             <table
#                                 class="charts-css column show-heading show-labels show-primary-axis show-4-secondary-axes show-data-axes data-spacing-15 hide-data">
#                                 <caption> Chart Heading</caption>
#                                 <thead>
#                                     <tr>
#                                         <th scope="col"> Year</th>
#                                         <th scope="col"> Value</th>
#                                     </tr>
#                                 </thead>
#                                 <tbody>
#                                     <tr>
#                                         <th> 2016</th>
#                                         <td style="--size: calc( 20 / 100 );"> 20</td>
#                                     </tr>
#                                     <tr>
#                                         <th> 2017</th>
#                                         <td style="--size: calc( 40 / 100 );"> 40</td>
#                                     </tr>
#                                     <tr>
#                                         <th> 2018</th>
#                                         <td style="--size: calc( 60 / 100 );"> 60</td>
#                                     </tr>
#                                     <tr>
#                                         <th> 2019</th>
#                                         <td style="--size: calc( 80 / 100 );"> 80</td>
#                                     </tr>
#                                     <tr>
#                                         <th> 2020</th>
#                                         <td style="--size: calc( 100 / 100 );"> 100</td>
#                                     </tr>
#                                 </tbody>
#                             </table>
#                         </fieldset>
                        
#                         <fieldset id="note01" class="window" style="z-index: 3; top: 700px; left: 660px;">
#                             <legend>Notes</legend>
#                             <textarea style="height: 100%;width:500px;" id="mytextarea">
#                             <div>{stage+'+'+step}</div>
#                             </textarea>
#                         </fieldset>
#                         <fieldset id="pdf01" class="window" style="z-index: 4; top: 450px; left: 5px;height:500px;width:50%">
#                             <legend>Levo Brochure</legend>
#                             <embed
#                                 src="https://stmaluepocprdwesteu.blob.core.windows.net/sinapiassetts/LEVO IFU XL2200S.pdf#view=FitH"
#                                 width="100%" height="100%" type="application/pdf">
#                         </fieldset>
#                         <fieldset id="iframe01" class="window" style="width: 600px; z-index: 5;top: 455px; left: 520px;">
#                             <legend>People's Answers</legend>
#                             <iframe title="Spreadsheet" width="100%" height="100%" frameborder="1" scrolling="yes"
#                                 src="https://malue-my.sharepoint.com/personal/jimd_malue_co_uk/_layouts/15/Doc.aspx?sourcedoc={{3dd180e5-8eae-4e16-803f-ad82fc1f228e}}&action=embedview&wbdiallowTypingandFormulaEntry=true&wdhideheaders=false&wdAllowInteractivity=True&Item=UnbundledQuestionsWithSnapshot&wdHideGridlines=False&wdDownloadButton=True">
#                             </iframe>
#                         </fieldset>
#                         <fieldset id="sheet" class="window" style="height:100%; width:550px; z-index: 6; top: 700px; left: 1px;">
#                             <legend>Spreadsheet</legend>
#                             <div>
#                                 <div id="xspreadsheet"></div>
#                             </div>
#                         </fieldset>
#                         <fieldset id="video01" class="window" style="z-index: 7; top: 1250px; left: 5px;">
#                             <legend>Video</legend>
#                             <iframe width="560" height="315"
#                                 src="https://www.youtube.com/embed/NVRXK1Idbv8?si=2VJ801QHNh33qdek"
#                                 title="YouTube video player" frameborder="0"
#                                 allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
#                                 referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
#                         </fieldset>
#                         <fieldset id="video02" class="window" style="z-index: 8; top: 1250px; left: 600px; width:400px">
#                             <legend>Video</legend>
#                             <video id="videoPlayer" controls width="100%"
#                                 src="https://cdn.muse.ai/u/YEYPt9W/55d8b61a2e60212336c075cbd61e37c3a8221220148146c5934c2caa65554457/videos/video.mp4"></video>
#                         </fieldset>
#                     </div>
# """

def generate_html_document(menu_html, items_html, note_content):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Innovations</title>
        <link href="{url_for('static', filename='font-awesome/css/font-awesome.css')}" rel="stylesheet">
        <link rel="stylesheet" type="text/css" href="{url_for('static', filename='style.css')}">
        <link href="https://cdn.jsdelivr.net/npm/charts.css/dist/charts.min.css" rel="stylesheet" >
        <link href="https://unpkg.com/x-data-spreadsheet@1.1.5/dist/xspreadsheet.css" rel="stylesheet" >
        
        <script src="{url_for('static', filename='scripts/interact.min.js')}"></script>
        <script src="https://unpkg.com/x-data-spreadsheet@1.1.5/dist/xspreadsheet.js"></script>
        <script src="{url_for('static', filename='scripts/tinymce/js/tinymce/tinymce.min.js')}"></script>
        
    </head>
   <body>
   <div id="wrapper">
        {menu_html}
        <div id="page-wrapper" class="gray-bg">        
            <div class=" ">
                <nav class="navbar navbar-static-top white-bg" role="navigation" style="margin-bottom: 0">
                    <div class="navbar-header">
                        <a class="navbar-minimalize minimalize-styl-2 btn btn-primary " href="#"><i
                                class="fa fa-bars"></i> </a>
                        <form role="search" class="navbar-form-custom" method="post" action="#">
                            <div class="form-group">
                                <input type="text" placeholder="Search for something..." class="form-control"
                                    name="top-search" id="top-search">
                            </div>
                        </form>
                    </div>
                    <ul class="nav navbar-top-links navbar-right">
                        <li>
                            <a href="#">
                                <i class="fa fa-sign-out"></i> Log out
                            </a>
                        </li>
                    </ul>
                </nav>
            </div>
            <div class="animated fadeInRight">
                <div style="border: black;">
                    <nav class="navbar">
                        <ul>
                            <li><a href="#evaluations">Evaluations</a></li>
                            <li><a href="#iIdeaForge">Idea Forge</a></li>
                            <li><a href="#reviews">Reviews</a></li>
                            <li><a href="#library">Library</a></li>
                            <li><a href="#dashboard">Dashboard</a></li>
                        </ul>
                    </nav>
                </div>
                <div class="navbar rounded-rect">
                    <ul>
                        <li>
                            <a href="#web" onclick="openDialog('web')" alt="web">
                                <figure>
                                    <img src="{url_for('static', filename='icons/web.svg')}" alt="web">
                                    <figcaption>Web</figcaption>
                                </figure>
                            </a>
                        </li>
                        <li>
                            <a href="#chat" onclick="openDialog('chat')" alt="chat">
                                <figure>
                                    <img src="{url_for('static', filename='icons/chat.svg')}" alt="chat">
                                    <figcaption>Chat</figcaption>
                                </figure>
                            </a>
                        </li>
                        <li>
                            <a href="#search" onclick="openDialog('web')">
                                <figure>
                                    <img src="{url_for('static', filename='icons/search.svg')}" alt="search">
                                    <figcaption>Search</figcaption>
                                </figure>
                            </a>
                        </li>
                        <li>
                            <a href="#forum" onclick="openDialog('forum')">
                                <figure>
                                    <img src="{url_for('static', filename='icons/forum.svg')}" alt="forum">
                                    <figcaption>Forum</figcaption>
                                </figure>
                            </a>
                        </li>
                        <li>
                            <a href="#books" onclick="openDialog('books')">
                                <figure>
                                    <img src="{url_for('static', filename='icons/books.svg')}" alt="books">
                                    <figcaption>Books</figcaption>
                                </figure>
                            </a>
                        </li>
                        <li>
                            <a href="#academicPapers" onclick="openDialog('academicpapers')">
                                <figure>
                                    <img src="{url_for('static', filename='icons/academicPapers.svg')}" alt="academicpapers">
                                    <figcaption>Academic Papers</figcaption>
                                </figure>
                            </a>
                        </li>
                        <li>
                            <a href="#wikipedia" onclick="openDialog('wikipedia')">
                                <figure>
                                    <img src="{url_for('static', filename='icons/wikipedia_svg_logo.svg')}" alt="wikipedia">
                                    <figcaption>Wikipedia</figcaption>
                                </figure>
                            </a>
                        </li>
                        <li>
                            <a href="#youtube" onclick="openDialog('youtube')">
                                <figure>
                                    <img src="{url_for('static', filename='icons/youtubelogo.svg')}" alt="youtubelogo">
                                    <figcaption>YouTube</figcaption>
                                </figure>
                            </a>
                        </li>
                    </ul>
                </div>
                <div class="">
                  {items_html}  
                </div>
                <div class="overlay" id="overlay" onclick="closeDialog()"></div>
                <div class="search-container" id="searchDialog">
                    <h2>Search Books and Journals</h2>
                    <form>
                        <input type="text" placeholder="Search for books or journals..." required>
                        <div>
                            <input type="radio" id="books" name="type" value="books" checked>
                            <label for="books">Books</label>
                            <input type="radio" id="journals" name="type" value="journals">
                            <label for="journals">Journals</label>
                        </div>
                        <br>
                        <button type="submit">Search</button>
                        <button type="button" class="close-btn" onclick="closeDialog()">Close</button>
                    </form>
                </div>
            </div>           
        </div>
    </div>

   
    <script type="module" src="{url_for('static', filename='scripts/script.js')}"> </script>
    </body>
    </html>
    """

#################################################################################
# Main program and routes

app = Flask(__name__)
@app.route('/')
def show_menu():
    # Call the generate_menu_html function and return the result
    items_html = generate_html_items('','')
    menu_html = generate_menu_html(menu_structure)
    html_document = generate_html_document(menu_html,items_html,note_content)
    return html_document

@app.route('/get-main-pane-contents')
def get_new_content():
    stage = request.args.get('stage')
    step = request.args.get('step')
    # Return fresh HTML content for the div
    items_html = generate_html_items(stage, step)
    return items_html

if __name__ == '__main__':
    app.run(debug=True)
