const fs = require('fs');
const path = require('path');

const file = path.join(__dirname, '..', 'docs', 'zapis_preview.html');
let s = fs.readFileSync(file, 'utf8');

const R = (pairs) => {
  for (const [from, to] of pairs) {
    if (!s.includes(from)) console.warn('MISSING:', from);
    else s = s.split(from).join(to);
  }
};

R([
  ["['8','Маленькая Бaba-Яaga']", "['8','Мalеньkaya Babа-Яaga, Malenkiy vodyanoy O. Proysler']"],
]);

console.log('test');
