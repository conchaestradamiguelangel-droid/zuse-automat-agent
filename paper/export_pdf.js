const fs = require("fs");
const path = require("path");
const { marked } = require("marked");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const draftPath = path.join(__dirname, "draft.md");
const htmlPath = path.join(__dirname, "zuse_preprint.html");
const pdfPath = path.join(__dirname, "zuse_preprint.pdf");

function htmlEscape(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const markdown = fs.readFileSync(draftPath, "utf8");

marked.setOptions({
  gfm: true,
  breaks: false,
  mangle: false,
  headerIds: false,
});

const body = marked.parse(markdown);

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata</title>
  <style>
    @page {
      size: A4;
      margin: 16mm 15mm 18mm 15mm;
    }
    * {
      box-sizing: border-box;
    }
    body {
      max-width: 980px;
      margin: 0 auto;
      color: #111;
      font-family: "Arial", "Helvetica", sans-serif;
      font-size: 10.5pt;
      line-height: 1.42;
    }
    h1, h2, h3, h4 {
      color: #111;
      line-height: 1.18;
      page-break-after: avoid;
    }
    h1 {
      font-size: 22pt;
      margin: 0 0 18pt;
      text-align: left;
    }
    h2 {
      font-size: 15.5pt;
      border-bottom: 1px solid #bbb;
      margin: 22pt 0 9pt;
      padding-bottom: 3pt;
    }
    h3 {
      font-size: 12.5pt;
      margin: 15pt 0 6pt;
    }
    h4 {
      font-size: 11pt;
      margin: 12pt 0 4pt;
    }
    p {
      margin: 0 0 8pt;
    }
    ul, ol {
      margin-top: 0;
      margin-bottom: 8pt;
      padding-left: 18pt;
    }
    li {
      margin: 2pt 0;
    }
    code {
      font-family: "Consolas", "Liberation Mono", monospace;
      font-size: 0.9em;
      background: #f4f4f4;
      padding: 0 2px;
      border-radius: 2px;
    }
    pre {
      background: #f6f6f6;
      border: 1px solid #ddd;
      padding: 7pt;
      overflow-wrap: anywhere;
      white-space: pre-wrap;
      page-break-inside: avoid;
    }
    pre code {
      background: transparent;
      padding: 0;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 8pt 0 12pt;
      table-layout: fixed;
      page-break-inside: auto;
      font-size: 7.4pt;
      line-height: 1.22;
    }
    thead {
      display: table-header-group;
    }
    tr {
      page-break-inside: avoid;
      page-break-after: auto;
    }
    th, td {
      border: 1px solid #cfcfcf;
      padding: 3pt 4pt;
      vertical-align: top;
      overflow-wrap: anywhere;
      word-break: normal;
    }
    th {
      background: #eeeeee;
      font-weight: 700;
    }
    blockquote {
      margin: 8pt 0;
      padding: 6pt 10pt;
      border-left: 3pt solid #777;
      background: #f7f7f7;
    }
    a {
      color: #0645ad;
      text-decoration: none;
    }
    strong {
      font-weight: 700;
    }
  </style>
</head>
<body>
${body}
</body>
</html>`;

fs.writeFileSync(htmlPath, html, "utf8");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(`file://${htmlPath.replace(/\\/g, "/")}`, { waitUntil: "networkidle" });
  await page.pdf({
    path: pdfPath,
    format: "A4",
    printBackground: true,
    margin: {
      top: "16mm",
      right: "15mm",
      bottom: "18mm",
      left: "15mm",
    },
    displayHeaderFooter: true,
    headerTemplate: "<div></div>",
    footerTemplate: `<div style="width:100%;font-size:8px;color:#666;padding:0 15mm;text-align:right;">Page <span class="pageNumber"></span> / <span class="totalPages"></span></div>`,
  });
  await browser.close();
  const stat = fs.statSync(pdfPath);
  console.log(`Wrote ${htmlEscape(path.relative(root, htmlPath))}`);
  console.log(`Wrote ${htmlEscape(path.relative(root, pdfPath))} (${stat.size} bytes)`);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
