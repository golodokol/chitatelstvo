async function main() {
  const r = await fetch('https://chitatelstvo.ru', { redirect: 'follow' });
  const t = await r.text();
  console.log('HTTP', r.status, 'bytes', t.length);
  console.log('VERSION', (t.match(/CHIT VERSION [^\s]+/) || ['NOT FOUND'])[0]);
  console.log('has MutationObserver inline', /MutationObserver/.test(t));
  console.log('has removeAttribute inline', /removeAttribute\("style"\)/.test(t));
  console.log('css v', (t.match(/chit-zero\.css\?v=([^"']+)/) || [])[1]);
  console.log('js v', (t.match(/chit-zero\.js\?v=([^"']+)/) || [])[1]);
  const script = t.match(/<script>\(function\(\)\{var E[\s\S]{0,500}/);
  if (script) console.log('INLINE SCRIPT START:', script[0].slice(0, 200));
  else console.log('INLINE SCRIPT: none (good)');
  try {
    const js = await (await fetch('https://api.chitatelstvo.ru/assets/chit-zero.js?v=20260621f')).text();
    console.log('CDN 20260621f', js.includes('20260621f'), 'MutationObserver', js.includes('MutationObserver'));
  } catch (e) {
    console.log('CDN check failed', e.message);
  }
}
main().catch((e) => { console.error(e); process.exit(1); });
