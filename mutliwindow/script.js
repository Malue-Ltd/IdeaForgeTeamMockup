let wins = []

function openWindows(windowNo) {
    switch ( windowNo ) {
        case 1: {
            wins[windowNo] = window.open("https://google.com", `Window ${windowNo}`, "width=400,height=300");
            break;
        }
        case 2: {
            wins[windowNo] = window.open("", `Window ${windowNo}`, "width=400,height=300");
            wins[windowNo].document.body.innerHTML = `
                <h1>Window 2</h1>
                <p>This is the second window.</p>
                <button onclick="window.opener.document.getElementById('message').innerText = 'Message from Window 2';">Send Message to Parent</button>
                
            `;

        }
    }
    
    // Check if windows are closed
    checkIfClosed(wins[1], 'Window 1');
    checkIfClosed(wins[2], 'Window 2');
}

function checkIfClosed(windowRef, windowName) {
    let checkClosedInterval = setInterval(() => {
        if (windowRef.closed) {
            console.log(`${windowName} is closed.`);
            clearInterval(checkClosedInterval);
        }
    }, 500);
}