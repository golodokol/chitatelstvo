const fs = require('fs');
fetch('https://chitatelstvo.ru')
  .then((r) => r.text())
  .then((t) => {
    fs.writeFileSync('C:/Users/Оля/Documents/ЧИТАТЕЛЬСТВО/scripts/live.html', t);
    const idx = t.indexOf('id="chit-main"');
    console.log('chit-main at', idx);
    console.log('ends with </div>', t.trimEnd().slice(-200));
    const scripts = [...t.matchAll(/<script[^>]*>[\s\S]*?<\/script>|<script[^>]+\/>/g)].map((m) => m[0].slice(0, 120));
    scripts.forEach((s, i) => console.log('SCRIPT', i, s.replace(/\n/g, ' ')));
  });
