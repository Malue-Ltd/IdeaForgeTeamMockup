//import "/static/scripts/@blocksuite/presets/themes/affine.css";
// import { AffineSchemas } from "/static/scripts/@blocksuite/blocks/dist/index.js";
// import { AffineEditorContainer } from '/static/scripts/@blocksuite/presets/dist/index.js';
// import { Schema, DocCollection, Text } from "/static/scripts/@blocksuite/store/dist/index.js";
// import { IndexeddbPersistence } from "/static/scripts/y-indexeddb/src/y-indexeddb.js";
// import { EdgelessEditor, PageEditor, createEmptyDoc } from "/static/scripts/@blocksuite/presets/dist/index.js";


document.addEventListener("DOMContentLoaded", function () {
    var toggler = document.getElementsByClassName("caret");
    for (var i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function () {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("caret-down");
            console.log("adding click nested  ??")
        });
    }


    createSheetData();
    //setupCanvas();
    SetupTogglersListeners();
    SetupSpreadsheet();
    SetupNotePad();
    SetupDragAndDrop();
    setZindexes();
    OutputFieldSetPositions();
    PreventDialogFromClosingWhenClickingInsideThedialog();
    OutputFieldSetPositions();

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
        document.getElementById("searchDialog")
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
        if(sheet){
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
        const fieldsets = document.querySelectorAll("fieldset.window");
        console.log(fieldsets);
        for (const element of fieldsets) {
            let rect = element.getBoundingClientRect();
            let elementName = element.querySelector('legend').textContent;
            console.log(`${elementName}, ${rect.top},${rect.left},${rect.height},${rect.width} `);
        }
        return fieldsets;
    }
    function SetupTogglersListeners() {
        let input = document.querySelector("#toggle");
        input?.addEventListener("change", toggleBox);
        let togglers = document.getElementsByClassName("caret");
        for (const element of togglers) {
            element.addEventListener("click", function () {
                this.parentElement
                    .querySelector(".nested");
                    //.classList.toggle("active");
                console.log("clicked on nested: " + element.innerHTML)
                let main_pane = document.querySelector("#main-pane");
                fetch('/get-main-pane-contents?selected=' + element.innerText)
                    .then(response => response.text())
                    .then(data => {
                        main_pane.innerHTML = data;
                        SetupSpreadsheet()
                        SetupNotePad();
                    })
                    .catch(error => console.error('Error:', error));
            });
        }
    }
    function SetupDragAndDrop() {
        interact(".window")
            .draggable({
                modifiers: [
                    interact.modifiers.snap({
                        targets: [interact.snappers.grid({ x: 10, y: 10 })],
                        range: Infinity,
                        relativePoints: [{ x: 0, y: 0 }],
                    }),
                ],
                inertia: true,
                onmove: function (event) {
                    let target = event.target;
                    let x = (parseFloat(target.getAttribute("data-x")) || 0) + event.dx;
                    let y = (parseFloat(target.getAttribute("data-y")) || 0) + event.dy;

                    target.style.transform = "translate(" + x + "px, " + y + "px)";
                    target.setAttribute("data-x", x);
                    target.setAttribute("data-y", y);

                },
            })
            .resizable({
                edges: { left: true, right: true, bottom: true, top: true },
                modifiers: [
                    interact.modifiers.snapSize({
                        targets: [
                            { width: 10 },
                            interact.snappers.grid({ width: 10, height: 10 }),
                        ],
                    }),
                ],
                inertia: true,
            })
            .on("resizemove", function (event) {
                let target = event.target;
                let x = parseFloat(target.getAttribute("data-x")) || 0;
                let y = parseFloat(target.getAttribute("data-y")) || 0;

                target.style.width = event.rect.width + "px";
                target.style.height = event.rect.height + "px";

                x += event.deltaRect.left;
                y += event.deltaRect.top;

                target.style.transform = "translate(" + x + "px," + y + "px)";

                target.setAttribute("data-x", x);
                target.setAttribute("data-y", y);
                OutputFieldSetPositions();
            });
    }
    function setZindexes() {
        let highestZIndex = 1;
        const maxZIndex = 10; // Define a maximum threshold

        function resetZIndices() {
            highestZIndex = 1;
            const updatedDivs = document.querySelectorAll(".window");
            updatedDivs.forEach((fieldset) => {
                fieldset.style.zIndex = 1;
            });
        }
        const fieldsets = document.querySelectorAll("fieldset");
        fieldsets.forEach((fieldset) => {
            fieldset.addEventListener("mousedown", () => {
                highestZIndex += 1;
                fieldset.style.zIndex = highestZIndex;
                if (highestZIndex >= maxZIndex) {
                    resetZIndices();
                }
            });
        });
    }
    function reflowBlocks() {
        OutputFieldSetPositions();
        // const blocks = Array.from(document.querySelectorAll(".window")).map(
        //     (block) => {
        //         const rect = block.getBoundingClientRect();
        //         console.log(rect);
        //         return {
        //             element: block,
        //             x: rect.left,
        //             y: rect.top,
        //             width: rect.width,
        //             height: rect.height,
        //         };
        //     }
        // );
        // // Assuming blocks are divs with the class "block"
        // // document.querySelectorAll(".window").forEach((block) => {
        // //     block.style.position = "absolute";
        // //     block.style.left = `${block.getBoundingClientRect().left}px`;
        // //     block.style.top = `${block.getBoundingClientRect().top}px`;
        // // });

        // // Now trigger the rearrangement logic
        // resolveOverlaps(blocks);
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
        document.getElementById("searchDialog").style.display = "block";
        document.getElementById("overlay").style.display = "block";
    }
    function closeDialog() {
        document.getElementById("searchDialog").style.display = "none";
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
    function toggleMenu(levelId,stage,step) {
        const level = document.getElementById(levelId);
        const currentDate = new Date();
        const milliseconds = currentDate.getMilliseconds();
        console.log(`Milliseconds: ${milliseconds}, ${levelId} , ${stage} , ${step})`);
        level.classList.toggle('collapsed');
        let main_pane = document.querySelector("#main-pane");
                fetch('/get-main-pane-contents?stage=' + stage + '&step=' + step)
                    .then(response => response.text())
                    .then(data => {
                        main_pane.innerHTML = data;
                        SetupSpreadsheet()
                        SetupNotePad();
                    })
                    .catch(error => console.error('Error:', error));
    }
    window.toggleMenu = toggleMenu;
    window.closeDialog = closeDialog;
    window.openDialog = openDialog;
    window.reflowBlocks = reflowBlocks;
});