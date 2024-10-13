//import "/static/scripts/@blocksuite/presets/themes/affine.css";
// import { AffineSchemas } from "/static/scripts/@blocksuite/blocks/dist/index.js";
// import { AffineEditorContainer } from '/static/scripts/@blocksuite/presets/dist/index.js';
// import { Schema, DocCollection, Text } from "/static/scripts/@blocksuite/store/dist/index.js";
// import { IndexeddbPersistence } from "/static/scripts/y-indexeddb/src/y-indexeddb.js";
// import { EdgelessEditor, PageEditor, createEmptyDoc } from "/static/scripts/@blocksuite/presets/dist/index.js";


document.addEventListener("DOMContentLoaded", function () {
    createSheetData();
    //setupCanvas();
    SetupSpreadsheet();
    SetupNotePad();
    SetupDragAndDrop();
    setToolWrapperZindexes();
    OutputFieldSetPositions();
    PreventDialogFromClosingWhenClickingInsideThedialog();
    OutputFieldSetPositions();

    const draggableDiv = document.getElementById("list-pane");
    const resizeHandle = document.createElement("div");
    resizeHandle.className = "resize-handle";
    draggableDiv.appendChild(resizeHandle);

    function animateDescend() {
        draggableDiv.style.top = "0px"; // Adjust the final top position as needed
    }

    let isResizing = false;
    let startY, startHeight;

    resizeHandle.addEventListener("mousedown", function (e) {
        isResizing = true;
        startY = e.clientY;
        startHeight = parseInt(window.getComputedStyle(draggableDiv).height, 10);
        document.documentElement.style.cursor = "ns-resize"; // Change cursor globally
    });

    document.addEventListener("mousemove", function (e) {
        if (isResizing) {
            const newHeight = startHeight + (e.clientY - startY);
            draggableDiv.style.height = `${newHeight}px`;
        }
    });

    document.addEventListener("mouseup", function () {
        isResizing = false;
        document.documentElement.style.cursor = ""; // Reset cursor
    });

    // Trigger descend animation when needed
    // animateDescend();


    function toggleBox() {
        // If the checkbox is checked, display the output text
        let checked = (document.getElementById("toggle"))?.checked;
        let parentE = document.getElementById("blocksuiteEditorEdgeless")?.parentNode;
        let parentP = document.getElementById("blocksuiteEditorPage")?.parentNode;
        if (checked) {
            //alert('P');
            parentP.style.display = 'none';
            parentE.style.display = 'block';
        } else {
            //alert('E');
            parentP.style.display = 'block';
            parentE.style.display = 'none';
        }


    }
    function PreventDialogFromClosingWhenClickingInsideThedialog() {
        document.getElementById("popupDoclist")
            .addEventListener("click", function (event) {
                event.stopPropagation();
            });
        document.getElementById("popupDialog")
            .addEventListener("click", function (event) {
                event.stopPropagation();
            });
    }
    function SetupNotePad() {
        tinymce.remove('#mytextarea');
        tinymce.init({
            selector: "#mytextarea",
            promotion: false,
            branding: false,
            license_key: 'gpl',
            plugins:
                "advlist preview visualblocks autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table",
            toolbar:
                "undo redo | preview visualblocks blocks fontfamily fontsize | bold italic underline strikethrough | link image media table | align lineheight | numlist bullist indent outdent | emoticons charmap | removeformat",
        });
    }
    function SetupSpreadsheet() {
        const myData = localStorage.getItem("sheetdata");
        let sheet = document.getElementById("sheet");
        if (sheet) {
            let widthOfBox = 500;//sheet.offsetWidth;
            console.log(widthOfBox);
            const options = {
                mode: "edit", // edit | read
                showToolbar: true,
                showGrid: true,
                showContextmenu: true,
                view: {
                    height: () => 500,
                    width: () => widthOfBox,
                }
            }
            x_spreadsheet("#xspreadsheet", options).loadData(JSON.parse(myData));
        }


    }
    function OutputFieldSetPositions() {
        const fieldsets = document.querySelectorAll("div.tool-wrapper");
        console.log(fieldsets);
        for (const element of fieldsets) {
            let rect = element.getBoundingClientRect();
            let elementName = element.querySelector('legend').textContent;
            console.log(`${elementName}, ${rect.top},${rect.left},${rect.height},${rect.width} `);
        }
        return fieldsets;
    }
    function SetupDragAndDrop() {
        const position = { x: 0, y: 0 }
        interact(".tool-wrapper")
            .draggable({
                listeners: {
                    start(event) {
                        console.log(event.type, event.target)
                    },
                    move(event) {
                        position.x += event.dx
                        position.y += event.dy

                        event.target.style.transform =
                            `translate(${position.x}px, ${position.y}px)`
                    },
                },
            })
        // interact(".tool-resize")
        //     .resizable({
        //         edges: { top: false, left: false, bottom: true, right: true },
        //         listeners: {
        //             move: function (event) {
        //                 let { x, y } = event.target.dataset

        //                 x = (parseFloat(x) || 0) + event.deltaRect.left
        //                 y = (parseFloat(y) || 0) + event.deltaRect.top

        //                 Object.assign(event.target.style, {
        //                     width: `${event.rect.width}px`,
        //                     height: `${event.rect.height}px`,
        //                     transform: `translate(${x}px, ${y}px)`
        //                 })

        //                 Object.assign(event.target.dataset, { x, y })
        //             }
        //         }
        //     })
    }
    function setToolWrapperZindexes() {
        let highestZIndex = document.querySelectorAll(".tool-wrapper").length;
        const maxZIndex = 65535; // Define a maximum threshold

        function resetZIndices() {
            highestZIndex = 1;
            const updatedDivs = document.querySelectorAll(".tool-wrapper");
            updatedDivs.forEach((tool_wrapper) => {
                tool_wrapper.style.zIndex += 1;
            });
        }
        const tool_wrappers = document.querySelectorAll(".tool-wrapper");
        tool_wrappers.forEach((tool_wrapper) => {
            tool_wrapper.addEventListener("mousedown", () => {
                highestZIndex += 1;
                tool_wrapper.style.zIndex = highestZIndex;
                if (highestZIndex >= maxZIndex) {
                    resetZIndices();
                }
            });
        });
    }
    function reflowBlocks() {
        OutputFieldSetPositions();
    }
    function resolveOverlaps(blocks) {
        for (let i = 0; i < blocks.length; i++) {
            for (let j = i + 1; j < blocks.length; j++) {
                while (isOverlapping(blocks[i], blocks[j])) {
                    // Move block j to the right
                    blocks[j].x += blocks[i].width + 10; // Add a margin of 10px

                    // If it moves out of the window, move it to the next row
                    if (blocks[j].x + blocks[j].width > window.innerWidth) {
                        blocks[j].x = 0;
                        blocks[j].y += blocks[i].height + 10; // Move down by height + margin
                    }
                }
            }
        }

        // Apply the resolved positions to the DOM elements
        blocks.forEach((block) => {
            block.element.style.left = `${block.x}px`;
            block.element.style.top = `${block.y}px`;
        });
        function isOverlapping(block1, block2) {
            return !(
                block2.x >= block1.x + block1.width ||
                block2.x + block2.width <= block1.x ||
                block2.y >= block1.y + block1.height ||
                block2.y + block2.height <= block1.y
            );
        }
    }
    function toggleLeftColumn() {
        document.body.classList.toggle("collapsed");
    }
    function openDialog(source) {
        document.getElementById("popupDialog").style.display = "block";
        const actionButton = document.getElementById("launchApp");
        actionButton.onclick = function() {
            launchApp(source);
        };

        document.getElementById("toolLaunchLabel").innerText= "Launch "+source;
        document.getElementById("overlay").style.display = "block";
    }
    function launchApp(source){        
        switch (source){
            case "sheet":
                window.location.href = "ms-excel:ofe|u|https://malue.sharepoint.com/:x:/s/MalueArchtecture/EfcQgnJDmmFBt2XT8bYJo1cBoQu0MMR8Y3nxVbyKVRoHdw?e=efeFIg|s|https://malue.sharepoint.com/:x:/s/MalueArchtecture/";
                break;
            case "document":
                window.location.href = "ms-word:ofe|u|https://stmaluepocsharewesteu.blob.core.windows.net/ideaforgemockupdocuments/blank.docx|s|https://malue.sharepoint.com/:f:/s/ProofofConcept-Initial/";
                break;
            case "workflow":
                window.open("http://localhost:13000/workflows/definitions/9d644b4c0b3914e/edit");
                break;
            default:
                alert("launching "+ source);
        }
    }

    function openArtifact(stage, step, id) {

        let tempdata = '';
        fetch('/artifact-details?stage=' + stage + '&step=' + step + '&id=' + id)
            .then(response => response.text())
            .then(data => {
                tempdata = data;
                const child = document.createElement('div');
                child.innerHTML = tempdata;
                let popupDialogHtml = document.getElementById("main-pane");
                popupDialogHtml.append(child);
                createSheetData();
                //setupCanvas();
                SetupSpreadsheet();
                SetupNotePad();
                SetupDragAndDrop();
                setToolWrapperZindexes();
                OutputFieldSetPositions();
                PreventDialogFromClosingWhenClickingInsideThedialog();
                OutputFieldSetPositions();
            })
            .catch(error => console.error('Error:', error));

        document.getElementById("popupDoclist").style.display = "block";
    }
    function closeArtifact() {
        document.getElementById("popupDoclist").style.display = "none";
        document.getElementById("overlay").style.display = "none";
    }
    function closeDialog() {
        document.getElementById("popupDialog").style.display = "none";
        document.getElementById("overlay").style.display = "none";
    }
    function setupCanvas() {
        const schema = new Schema().register(AffineSchemas);
        const collection = new DocCollection({ schema });
        collection.meta.initialize();
        const doc = createEmptyDoc().init();
        const editor = new AffineEditorContainer();
        new IndexeddbPersistence('provider-demo', doc.spaceDoc);
        editor.doc = doc;
        // Init doc with default block tree
        let edgelessEditor = new EdgelessEditor();
        let pageEditor = new PageEditor();
        edgelessEditor.doc = doc;
        pageEditor.doc = doc;
        // Update block node with some initial text content
        // start with edgeless editor
        document.getElementById("blocksuiteEditorEdgeless")?.append(edgelessEditor);
        document.getElementById("blocksuiteEditorPage")?.append(pageEditor);

        //const paragraphs = doc.getBlocksByFlavour("affine:paragraph");
        //const paragraph = paragraphs[0];
        //doc.updateBlock(paragraph.model, {text: new Text("Hello edgeless World!"),});
        const pageBlockId = doc.addBlock('affine:page', {});
        doc.addBlock("affine:surface", {}, pageBlockId);
        const noteId = doc.addBlock("affine:note", {}, pageBlockId);
        doc.addBlock(
            "affine:paragraph",
            { text: new Text("Hello old New World!") },
            noteId
        );
        doc.addBlock(
            "affine:paragraph",
            { text: new Text("Hello Newish one World!") },
            noteId
        );
    }
    function createSheetData() {

        const myData = [
            {
                name: "sheet-test-1",
                freeze: "B3",
                styles: [
                    {
                        bgcolor: "#f4f5f8",
                        textwrap: true,
                        color: "#900b09",
                        border: {
                            top: ["thin", "#0366d6"],
                            bottom: ["thin", "#0366d6"],
                            right: ["thin", "#0366d6"],
                            left: ["thin", "#0366d6"],
                        },
                    },
                ],
                merges: ["C3:D4"],
                rows: {
                    1: {
                        cells: {
                            0: { text: "testingtesttestetst" },
                            2: { text: "testing" },
                        },
                    },
                    2: {
                        cells: {
                            0: { text: "render", style: 0 },
                            1: { text: "Hello" },
                            2: { text: "haha", merge: [1, 1] },
                        },
                    },
                    8: {
                        cells: {
                            8: { text: "border test", style: 0 },
                        },
                    },
                },
            },
            { name: "sheet-test" },];
        localStorage.setItem("sheetdata", JSON.stringify(myData));
    }
    function toggleMenu(levelId, stage, step) {
        const level = document.getElementById(levelId);
        const currentDate = new Date();
        const milliseconds = currentDate.getMilliseconds();
        console.log(`Milliseconds: ${milliseconds}, ${levelId} , ${stage} , ${step})`);

        document.getElementById("popupDoclist").style.display = "block";
        if (level != null) {
            level.classList.toggle('collapsed');
        };
        let main = document.getElementById("main-pane");
        main.innerHTML = '';
        let main_pane = document.querySelector("#list-pane");
        fetch('/document-list?stage=' + stage + '&step=' + step)
            .then(response => response.text())
            .then(data => {
                main_pane.innerHTML = data;
                createSheetData();
                //setupCanvas();
                SetupSpreadsheet();
                SetupNotePad();
                SetupDragAndDrop();
                setToolWrapperZindexes();
                OutputFieldSetPositions();
                PreventDialogFromClosingWhenClickingInsideThedialog();
                OutputFieldSetPositions();
            })
            .catch(error => console.error('Error:', error));
        animateDescend();
    }
    function closeNote(idSeq) {
        document.getElementById("note" + idSeq).style.display = "none"; // or use `.remove()` to delete it
        disposeOfArtifactDisplay(idSeq)
    }
    function closeDoc(idSeq) {
        document.getElementById("doc" + idSeq).style.display = "none"; // or use `.remove()` to delete it
        disposeOfArtifactDisplay(idSeq)
    }
    function closeCanvas(idSeq) {
        document.getElementById("canvas" + idSeq).style.display = "none"; // or use `.remove()` to delete it
        disposeOfArtifactDisplay(idSeq)
    }
    function closeWeb(idSeq) {
        document.getElementById("web" + idSeq).style.display = "none"; // or use `.remove()` to delete it
        disposeOfArtifactDisplay(idSeq)
    }
    function closeUnsupported(idSeq) {
        document.getElementById("unknown" + idSeq).style.display = "none"; // or use `.remove()` to delete it
        disposeOfArtifactDisplay(idSeq)
    }
    function closePdf(idSeq) {
        document.getElementById("pdf" + idSeq).style.display = "none"; // or use `.remove()` to delete it
        disposeOfArtifactDisplay(idSeq)

    }
    function disposeOfArtifactDisplay(id) {
        fetch('/disposeOfArtifactDisplay?id=' + id)
            .then(response => response.text())
            .then(data => {
                createSheetData();
                //setupCanvas();
                SetupSpreadsheet();
                SetupNotePad();
                SetupDragAndDrop();
                setToolWrapperZindexes();
                OutputFieldSetPositions();
                PreventDialogFromClosingWhenClickingInsideThedialog();
                OutputFieldSetPositions();
            })
            .catch(error => console.error('Error:', error));
    }
    function openNewWindow() {
        window.open(
            "http://localhost:13000/workflows/definitions/9d644b4c0b3914e/edit", 
            "_blank", 
            "width=800,height=600,scrollbars=yes,resizable=yes"
        );
    }
    window.openNewWindow = openNewWindow;
    window.disposeOfArtifactDisplay = disposeOfArtifactDisplay;
    window.closePdf = closePdf;
    window.closeUnsupported = closeUnsupported;
    window.closeDoc = closeDoc;
    window.closeCanvas = closeCanvas;
    window.closeWeb = closeWeb;
    window.closeNote = closeNote;
    window.openArtifact = openArtifact;
    window.closeArtifact = closeArtifact;
    window.toggleMenu = toggleMenu;
    window.closeDialog = closeDialog;
    window.openDialog = openDialog;
    window.reflowBlocks = reflowBlocks;
});