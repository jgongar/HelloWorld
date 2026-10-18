const { chromium } = require('playwright');
(async () => {
  const [,, input, output] = process.argv;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + input, { waitUntil: 'load' });
  await page.pdf({
    path: output, format: 'A4', landscape: true, printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="font-size:7px;width:100%;padding:0 12mm;color:#667;display:flex;justify-content:space-between;"><span>PEA screening — leads, not investment advice — data as of 18 Oct 2026</span><span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '12mm', bottom: '14mm', left: '10mm', right: '10mm' },
  });
  await browser.close();
})();
