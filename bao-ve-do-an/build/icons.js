const React = require('react');
const ReactDOMServer = require('react-dom/server');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');
const fa = require('react-icons/fa');
const md = require('react-icons/md');
const gi = require('react-icons/gi');
const tb = require('react-icons/tb');
const io5 = require('react-icons/io5');
const libs = {fa, md, gi, tb, io5};
const list = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
const out = process.argv[3];
(async () => {
  for (const it of list) {
    const lib = libs[it.lib];
    const Comp = lib[it.icon];
    if (!Comp) { console.log('MISSING', it.lib, it.icon); continue; }
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, {color: '#' + (it.color || 'FFFFFF'), size: 512}));
    const buf = await sharp(Buffer.from(svg)).resize(it.px || 384, it.px || 384, {fit: 'contain', background: {r:0,g:0,b:0,alpha:0}}).png().toBuffer();
    fs.writeFileSync(path.join(out, it.name + '.png'), buf);
  }
  console.log('done');
})();
