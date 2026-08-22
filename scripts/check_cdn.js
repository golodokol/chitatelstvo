fetch('https://api.chitatelstvo.ru/assets/chit-zero.js?v=20260621e')
  .then((r) => r.text())
  .then((t) => {
    console.log('VERSION:', (t.match(/VERSION = '([^']+)'/) || [])[1]);
    console.log('chitPatchTildaStyleBlock:', t.includes('chitPatchTildaStyleBlock'));
    console.log('removeAttribute:', t.includes('removeAttribute'));
  });
