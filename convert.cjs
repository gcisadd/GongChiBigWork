const fs = require('fs');
const MarkdownToDocx = require('markdown-to-docx');
const path = require('path');

async function convert() {
  const markdownPath = path.join(__dirname, '项目文档.md');
  const outputPath = path.join(__dirname, '项目文档.docx');
  
  const markdownContent = fs.readFileSync(markdownPath, 'utf8');
  
  const docx = await MarkdownToDocx(markdownContent);
  
  fs.writeFileSync(outputPath, docx);
  
  console.log('Word文档已导出:', outputPath);
}

convert().catch(console.error);
