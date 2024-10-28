const CDP = require('chrome-remote-interface');

async function saveMHTML() {
  const client = await CDP();
  const { Page } = client;
  await Page.enable();
  Page.lifecycleEvent((event) => {
    if (event.name === 'unload') {
        alert('Page is being unloaded or closed');
        console.log('Page is being unloaded or closed');
    }
});
  await Page.navigate({url: 'https://example.com'});
  await Page.loadEventFired();
  const mhtml = await Page.captureScreenshot({format: 'png'});
  require('fs').writeFileSync('webpage.png', mhtml.data,'base64');
  //client.close();
}

saveMHTML();
