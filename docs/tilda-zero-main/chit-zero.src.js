(function ensureChitStylesheets() {
  var head = document.head || document.getElementsByTagName('head')[0] || document.documentElement;
  var nodes = document.querySelectorAll('link[rel="stylesheet"]');
  for (var i = 0; i < nodes.length; i++) {
    var href = nodes[i].getAttribute('href') || '';
    if (href.indexOf('api.chitatelstvo.ru/assets/chit-') === -1) continue;
    if (nodes[i].parentNode !== head) head.appendChild(nodes[i]);
  }
  // Служебная плашка ST100 не для родителей (оплата на /oplata)
  if (!document.getElementById('chit-hide-st100-warning')) {
    var style = document.createElement('style');
    style.id = 'chit-hide-st100-warning';
    style.textContent = '#chit-st100-warning,.st100-warning{display:none!important;visibility:hidden!important;height:0!important;margin:0!important;padding:0!important;overflow:hidden!important;border:0!important}';
    head.appendChild(style);
  }
  function killSt100Warning() {
    var warn = document.getElementById('chit-st100-warning');
    if (warn && warn.parentNode) warn.parentNode.removeChild(warn);
  }
  killSt100Warning();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', killSt100Warning);
  }
})();

function chitReady(fn) {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fn);
  } else {
    fn();
  }
}

function chitPatchTildaStyleBlock() {
  var rec = document.getElementById('rec2378409351');
  if (!rec) return;
  var styles = rec.querySelectorAll('style');
  for (var i = 0; i < styles.length; i++) {
    var txt = styles[i].textContent || '';
    if (txt.indexOf('1781424531092000001') === -1 && txt.indexOf('t396__artboard') === -1) continue;
    var next = txt
      .replace(/left:\s*calc\([^)]+\)/gi, 'left:0')
      .replace(/width:\s*(?:1200|960|640|480|320)px/gi, 'width:100%')
      .replace(/height:\s*37000px/gi, 'height:auto')
      .replace(/height:\s*35000px/gi, 'height:auto')
      .replace(/height:\s*100vh/gi, 'height:auto')
      .replace(/display:\s*table/gi, 'display:block')
      .replace(/top:\s*-\d+px/gi, 'top:0');
    if (next !== txt) styles[i].textContent = next;
  }
}

function fixForWhomCopy() {
  var replacements = [
    ['семей, которым важно системное чтение, а не случайные тексты', 'семей, понимающих ценность чтения'],
    ['тех, кому нужен свой темп — занятия без расписания и давления', 'тех, кто привык читать в своём удобном темпе'],
    ['тех, кому нужен свой темп — без давления и оценок', 'тех, кто привык читать в своём удобном темпе']
  ];
  var items = document.querySelectorAll('.for-whom__item');
  for (var i = 0; i < items.length; i++) {
    var html = items[i].innerHTML;
    for (var r = 0; r < replacements.length; r++) {
      if (html.indexOf(replacements[r][0]) !== -1) {
        html = html.split(replacements[r][0]).join(replacements[r][1]);
      }
    }
    items[i].innerHTML = html;
  }
  var leads = document.querySelectorAll('.section__lead');
  for (var j = 0; j < leads.length; j++) {
    var t = leads[j].innerHTML;
    if (t.indexOf(' — без оценок и сравнений') !== -1) {
      leads[j].innerHTML = t.split(' — без оценок и сравнений').join('');
    }
    if (t.indexOf(', без оценок и сравнений с другими') !== -1) {
      leads[j].innerHTML = leads[j].innerHTML.split(', без оценок и сравнений с другими').join('');
    }
  }
  var ctaBtn = document.querySelector('#final-cta .btn');
  if (ctaBtn) {
    ctaBtn.setAttribute('href', '#quiz');
    ctaBtn.textContent = 'Получить урок бесплатно';
  }
  var aboutPs = document.querySelectorAll('#chit-main p');
  for (var k = 0; k < aboutPs.length; k++) {
    var ph = aboutPs[k].innerHTML;
    if (ph.indexOf('родителю ничего отмечать не нужно') !== -1) {
      aboutPs[k].innerHTML = ph.split('родителю ничего отмечать не нужно').join(
        'словики и уровни начисляются сразу после заданий'
      );
    }
  }
  var ctaFix = document.getElementById('chit-cta-fix');
  if (!ctaFix) {
    ctaFix = document.createElement('style');
    ctaFix.id = 'chit-cta-fix';
    document.head.appendChild(ctaFix);
  }
  if ((ctaFix.textContent || '').indexOf('100vw') === -1) {
    ctaFix.textContent = (ctaFix.textContent || '') +
      '#chit-main .final-cta-scroller{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;box-sizing:border-box!important}' +
      '#chit-main .final-cta{width:100%!important;overflow:hidden!important}' +
      '#chit-main .final-cta__bg{inset:0!important;background-size:cover!important;background-position:center bottom!important}';
  }
}

function fixTildaLayout() {
  if (window._chitFixBusy) return;
  window._chitFixBusy = true;
  chitPatchTildaStyleBlock();
  var main = document.getElementById('chit-main');
  if (!main) {
    window._chitFixBusy = false;
    return;
  }
  var rec = document.getElementById('rec2378409351');
  if (rec) {
    rec.style.setProperty('padding-top', '0', 'important');
    rec.style.setProperty('margin-top', '0', 'important');
    rec.style.setProperty('width', '100%', 'important');
    rec.style.setProperty('max-width', '100%', 'important');
    rec.style.setProperty('overflow-x', 'hidden', 'important');
  }
  var wrap = main.closest('.t396');
  if (wrap) {
    wrap.style.setProperty('display', 'block', 'important');
    wrap.style.setProperty('position', 'relative', 'important');
    wrap.style.setProperty('width', '100%', 'important');
    wrap.style.setProperty('max-width', '100%', 'important');
    wrap.style.setProperty('left', '0', 'important');
    wrap.style.setProperty('margin', '0', 'important');
    wrap.style.setProperty('transform', 'none', 'important');
    wrap.style.setProperty('overflow-x', 'hidden', 'important');
  }
  var artboard = main.closest('.t396__artboard');
  if (artboard) {
    artboard.style.setProperty('width', '100%', 'important');
    artboard.style.setProperty('max-width', '100%', 'important');
    artboard.style.setProperty('height', 'auto', 'important');
    artboard.style.setProperty('left', '0', 'important');
    artboard.style.setProperty('position', 'relative', 'important');
  }
  var atom = main.closest('.tn-atom');
  if (atom) {
    atom.style.setProperty('width', '100%', 'important');
    atom.style.setProperty('height', 'auto', 'important');
  }
  var elem = main.closest('.tn-elem');
  if (elem) {
    elem.style.setProperty('display', 'block', 'important');
    elem.style.setProperty('position', 'relative', 'important');
    elem.style.setProperty('left', '0', 'important');
    elem.style.setProperty('top', '0', 'important');
    elem.style.setProperty('width', '100%', 'important');
    elem.style.setProperty('max-width', '100%', 'important');
    elem.style.setProperty('min-width', '0', 'important');
    elem.style.setProperty('height', 'auto', 'important');
    elem.style.setProperty('transform', 'none', 'important');
    elem.style.setProperty('margin', '0', 'important');
  }
  main.style.setProperty('width', '100%', 'important');
  main.style.setProperty('max-width', '100%', 'important');
  main.style.setProperty('overflow-x', 'hidden', 'important');
  document.documentElement.style.overflowX = 'hidden';
  document.body.style.overflowX = 'hidden';
  window._chitFixBusy = false;
}

function chitHookTildaInit() {
  if (window._chitT396Hooked) return;
  var orig = window.t396_init;
  if (typeof orig !== 'function') return;
  window._chitT396Hooked = true;
  window.t396_init = function() {
    var out = orig.apply(this, arguments);
    chitPatchTildaStyleBlock();
    fixTildaLayout();
    setTimeout(fixTildaLayout, 50);
    setTimeout(fixTildaLayout, 300);
    return out;
  };
}

function chitInjectTildaKillStyle() {
  var css = '#allrecords #rec2378409351 .t396,#allrecords #rec2378409351 .t396__artboard,#allrecords #rec2378409351 .tn-elem[data-elem-id="1781424531092000001"],#allrecords #rec2378409351 .tn-elem[data-elem-type="html"],#allrecords #rec2378409351 .tn-atom,#allrecords #rec2378409351 .tn-atom__html{display:block!important;position:relative!important;left:0!important;top:0!important;width:100%!important;max-width:100%!important;min-width:0!important;height:auto!important;margin:0!important;transform:none!important;zoom:1!important}';
  var style = document.getElementById('chit-tilda-kill');
  if (!style) {
    style = document.createElement('style');
    style.id = 'chit-tilda-kill';
    style.textContent = css;
    document.head.appendChild(style);
  } else if (style.parentNode && style.parentNode.lastElementChild !== style) {
    document.head.appendChild(style);
  }
}

function chitForceLoadImages() {
  var root = document.getElementById('chit-main');
  if (!root) return;
  root.querySelectorAll('img').forEach(function(img) {
    img.removeAttribute('onerror');
    var src = img.getAttribute('src') || '';
    if (!src || src.indexOf('api.chitatelstvo.ru/assets/') === -1) return;
    if (img._chitImgBound) return;
    img._chitImgBound = true;
    img.addEventListener('error', function onErr() {
      var tries = img._chitImgRetry || 0;
      if (tries > 2) return;
      img._chitImgRetry = tries + 1;
      var base = src.split('?')[0];
      setTimeout(function() {
        img.src = base + '?r=' + Date.now();
      }, img._chitImgRetry * 600);
    });
  });
}

function chitStartLayoutPin() {
  chitInjectTildaKillStyle();
  chitHookTildaInit();
  chitPatchTildaStyleBlock();
  fixTildaLayout();
  fixForWhomCopy();
  var n = 0;
  var pin = setInterval(function() {
    chitInjectTildaKillStyle();
    chitPatchTildaStyleBlock();
    fixTildaLayout();
    fixForWhomCopy();
    chitHookTildaInit();
    if (++n > 4) clearInterval(pin);
  }, 500);
  window.addEventListener('resize', fixTildaLayout, { passive: true });
  window.addEventListener('load', function() {
    chitPatchTildaStyleBlock();
    fixTildaLayout();
    fixForWhomCopy();
  });
}

chitReady(function() {
  chitStartLayoutPin();

var COURSE_PAGES = {
  'early-letters': 'https://chitatelstvo.ru/bukvy-ozhivayut',
  'early-stories': 'https://chitatelstvo.ru/pervye-istorii',
  'grade-1': 'https://chitatelstvo.ru/1-klass',
  'grade-2': 'https://chitatelstvo.ru/2-klass',
  'grade-3': 'https://chitatelstvo.ru/3-klass',
  'grade-4': 'https://chitatelstvo.ru/4-klass',
  'extra-6-8': 'https://chitatelstvo.ru/6-8-let',
  'extra-9-11': 'https://chitatelstvo.ru/9-11-let',
  'wind': 'https://chitatelstvo.ru/veter-v-ivah',
  'garden': 'https://chitatelstvo.ru/tainstvenny-sad',
  'rus-6-9': 'https://chitatelstvo.ru/russkie-skazki-6-9',
  'rus-10-12': 'https://chitatelstvo.ru/russkie-skazki-10-12'
};
var COURSE_HUB = 'https://chitatelstvo.ru/programmy';

var PROGRAMS = {
  basic: [
    { group: 'grade-1', title: '1 класс', intro: 'Для учеников 1 класса (примерно 7–8 лет).',
      june: [['1','Царевна лягушка'],['2','Рассказы из Азбуки Л.Н. Толстой'],['3','Рассказы Н. Носова (Ступеньки, Заплатка, Затейники, Шляпа)'],['4','Кот в сапогах, Мальчик с пальчик Ш. Перро']],
      july: [['5','По щучьему велению'],['6','Сказка о мёртвой царевне и о семи богатырях А.С. Пушкин'],['7','Принцесса на горошине, Дюймовочка Г. Андерсен'],['8','Аля, Кляксич и буква А И.П. Токмакова']] },
    { group: 'grade-2', title: '2 класс',
      june: [['1','Сказка о рыбаке и рыбке А.С. Пушкин'],['2','Цветик-семицветик В.П. Катаев'],['3','Как муравьишка домой добирался, Где раки зимуют В.В. Бианки'],['4','Гадкий утёнок Г. Андерсен']],
      july: [['5','Филипок + Азбука Л.Н. Толстой'],['6','Незнайка на Луне Н. Носов'],['7','Рикки-Тикки-Тави Р. Киплинг'],['8','Маленькая Баба-Яга, Маленький водяной О. Пройслер']] },
    { group: 'grade-3', title: '3 класс',
      june: [['1','Сказка о царе Салтане, о сыне его славном и могучем богатыре А.С. Пушкин'],['2','Сказка про храброго зайца, Серая Шейка Д.Н. Мамин-Сибиряк'],['3','Черная курица или Подземные жители А. Погорельский'],['4','Чудесный доктор А. Куприн']],
      july: [['5','Сказка о молодильных яблоках и живой воде, Волшебное кольцо'],['6','Серебряный рубль В. Одоевский'],['7','Аленький цветочек С.Т. Аксаков'],['8','Королевство кривых зеркал В. Губарев']] },
    { group: 'grade-4', title: '4 класс',
      june: [['1','Уральские сказы П. Бажов'],['2','Сказка о потерянном времени Е. Шварц'],['3','Три толстяка Ю. Олеша'],['4','Остров Сокровищ Р. Стивенсон']],
      july: [['5','Приключения Тома Сойера М. Твен'],['6','Белый Бим, Черное ухо Г. Троепольский'],['7','Пеппи Длинный чулок А. Линдгрен'],['8','Путешествия Гулливера Дж. Свифт']] }
  ],
  extra: [
    { group: 'extra-6-8', title: '6–8 лет',
      june: [['1','Плюшевый заяц, или как игрушки становятся настоящими У. Марджери'],['2','Муми-тролль и комета Т. Янссон'],['3','Шляпа волшебника Т. Янссон'],['4','Приключения медвежонка Паддингтона М. Бонд']],
      july: [['5','Невероятные приключения кролика Эдварда К. ДиКамилло'],['6','Тутта Карлссон Первая и единственная, Людвиг Четырнадцатый и др. Я. Экхольм'],['7','Карлик Нос В. Гауф'],['8','Чарли и шоколадная фабрика Р. Даль']] },
    { group: 'extra-9-11', title: '9–11 лет',
      june: [['1','Опасное лето Т. Янссон'],['2','Рони, дочь разбойника А. Линдгрен'],['3','Собака Пес Д. Пеннак'],['4','Вафельное сердце М. Парр']],
      july: [['5','Чудесное путешествие Нильса с дикими гусями С. Лагерлеф'],['6','Чудесное путешествие Нильса с дикими гусями С. Лагерлеф, 2 часть'],['7','Полианна Э. Портер'],['8','Калиф-аист, Маленький Мук В. Гауф']] }
  ]
};

var TALE_INFO = {
  'Царевна лягушка': { desc: 'Русская волшебная сказка о верности, терпении и испытаниях на пути к счастью.', quote: null },
  'Рассказы из Азбуки Л.Н. Толстой': { desc: 'Короткие нравственные тексты из азбуки Толстого учат внимательности, доброте и честности.', quote: null },
  'Рассказы Н. Носова (Ступеньки, Заплатка, Затейники, Шляпа)': { desc: 'Смешные и жизненные рассказы Носова показывают детскую находчивость и дружбу.', quote: null },
  'Кот в сапогах, Мальчик с пальчик Ш. Перро': { desc: 'Сказки Перро о смекалке маленького героя и победе ума над обстоятельствами.', quote: null },
  'По щучьему велению': { desc: 'Народная сказка о Емеле, в которой чудо и удача соседствуют с ответственностью за желания.', quote: 'По щучьему велению, по моему хотению.' },
  'Сказка о мёртвой царевне и о семи богатырях А.С. Пушкин': { desc: 'Поэтическая сказка Пушкина о красоте души, зависти и торжестве справедливости.', quote: 'Свет мой, зеркальце! скажи.' },
  'Принцесса на горошине, Дюймовочка Г. Андерсен': { desc: 'Сказки Андерсена о тонкой душевной чуткости и поиске своего места в большом мире.', quote: null },
  'Аля, Кляксич и буква А И.П. Токмакова': { desc: 'Веселая повесть-игра о буквах и словах, которая развивает интерес к языку.', quote: null },
  'Сказка о рыбаке и рыбке А.С. Пушкин': { desc: 'История о жадности и мере желаний, где неблагодарность приводит к утрате всего.', quote: 'Осталась старуха у разбитого корыта.' },
  'Цветик-семицветик В.П. Катаев': { desc: 'Добрая сказка о девочке, которая учится использовать чудесный дар ради другого человека.', quote: 'Лети, лети, лепесток.' },
  'Как муравьишка домой добирался, Где раки зимуют В.В. Бианки': { desc: 'Познавательные рассказы Бианки знакомят с природой и повадками животных.', quote: null },
  'Гадкий утёнок Г. Андерсен': { desc: 'Трогательная история о принятии себя и превращении одиночества в внутреннюю силу.', quote: null },
  'Филипок + Азбука Л.Н. Толстой': { desc: 'Тексты Толстого о первых шагах в учебе помогают почувствовать ценность знаний.', quote: null },
  'Незнайка на Луне Н. Носов': { desc: 'Фантастическое приключение о мире коротышек, дружбе и критическом взгляде на общество.', quote: null },
  'Рикки-Тикки-Тави Р. Киплинг': { desc: 'Рассказ о смелом мангусте, который защищает дом от кобр и не отступает перед опасностью.', quote: 'Рикки-тикки-тикки-тикки-чк!' },
  'Маленькая Баба-Яга, Маленький водяной О. Пройслер': { desc: 'Сказочные истории Пройслера о взрослении, шалостях и выборе добра.', quote: null },
  'Сказка о царе Салтане, о сыне его славном и могучем богатыре А.С. Пушкин': { desc: 'Яркая пушкинская сказка о клевете, чудесах и счастливом воссоединении семьи.', quote: 'Ветер по морю гуляет и кораблик подгоняет.' },
  'Сказка про храброго зайца, Серая Шейка Д.Н. Мамин-Сибиряк': { desc: 'Истории Мамина-Сибиряка о храбрости и сострадании к тем, кто слабее.', quote: null },
  'Черная курица или Подземные жители А. Погорельский': { desc: 'Литературная сказка о тайне, соблазне легкого успеха и цене данного слова.', quote: null },
  'Чудесный доктор А. Куприн': { desc: 'Рассказ о милосердии и помощи в самый трудный момент человеческой жизни.', quote: null },
  'Сказка о молодильных яблоках и живой воде, Волшебное кольцо': { desc: 'Народные сюжеты о поиске чудесных даров, верности и награде за смелость.', quote: null },
  'Серебряный рубль В. Одоевский': { desc: 'Поучительная история о честности и том, как деньги связаны с трудом и совестью.', quote: null },
  'Аленький цветочек С.Т. Аксаков': { desc: 'Русская версия сказки о любви, которая видит за внешностью истинную душу.', quote: null },
  'Королевство кривых зеркал В. Губарев': { desc: 'Повесть-сказка о встрече с собственными недостатками и работе над собой.', quote: null },
  'Уральские сказы П. Бажов': { desc: 'Сказы Бажова соединяют уральский фольклор, ремесло и волшебство родной земли.', quote: null },
  'Сказка о потерянном времени Е. Шварц': { desc: 'Сказка Шварца напоминает, что время невосполнимо и его важно ценить.', quote: null },
  'Три толстяка Ю. Олеша': { desc: 'Романтическая сказка о свободе, дружбе и сопротивлении несправедливой власти.', quote: null },
  'Остров Сокровищ Р. Стивенсон': { desc: 'Классический приключенческий роман о карте, море, пиратах и испытании характера.', quote: 'Пятнадцать человек на сундук мертвеца.' },
  'Приключения Тома Сойера М. Твен': { desc: 'Веселая и ироничная история о детстве, дружбе и стремлении к свободе.', quote: null },
  'Белый Бим, Черное ухо Г. Троепольский': { desc: 'Пронзительная повесть о преданности собаки и человеческой ответственности.', quote: null },
  'Пеппи Длинный чулок А. Линдгрен': { desc: 'Добрая и озорная книга о независимой девочке с огромной фантазией и смелостью.', quote: null },
  'Путешествия Гулливера Дж. Свифт': { desc: 'Приключенческая сатира о необычных странах, которая учит видеть мир с разных сторон.', quote: null },
  'Плюшевый заяц, или как игрушки становятся настоящими У. Марджери': { desc: 'Трогательная сказка о любви, благодаря которой игрушка становится по-настоящему живой.', quote: null },
  'Муми-тролль и комета Т. Янссон': { desc: 'Философская история Янссон о семье, тревоге перед неизвестным и взаимной поддержке.', quote: null },
  'Шляпа волшебника Т. Янссон': { desc: 'Сказочная повесть о чудесных превращениях и последствиях любопытства.', quote: null },
  'Приключения медвежонка Паддингтона М. Бонд': { desc: 'Теплые рассказы о вежливом медвежонке, который учится жить в новом доме.', quote: null },
  'Невероятные приключения кролика Эдварда К. ДиКамилло': { desc: 'История фарфорового кролика о потерях, путешествии и способности снова любить.', quote: null },
  'Тутта Карлссон Первая и единственная, Людвиг Четырнадцатый и др. Я. Экхольм': { desc: 'Ироничные сказки о дружбе вопреки привычным ролям и предрассудкам.', quote: null },
  'Карлик Нос В. Гауф': { desc: 'Волшебная сказка о превращении, стойкости и возвращении к себе.', quote: null },
  'Чарли и шоколадная фабрика Р. Даль': { desc: 'Фантастическая история о честном мальчике, который получает шанс на чудо.', quote: null },
  'Опасное лето Т. Янссон': { desc: 'Летняя повесть Туве Янссон о муми-троллях, свободе и приключениях на необитаемом острове.', quote: null },
  'Рони, дочь разбойника А. Линдгрен': { desc: 'Сказочная повесть Астрид Линдгрен о смелой девочке, дружбе и жизни в разбойничьем крае.', quote: null },
  'Собака Пес Д. Пеннак': { desc: 'История о бездомной собаке и людях, которые учатся ответственности и сочувствию.', quote: null },
  'Вафельное сердце М. Парр': { desc: 'Трогательная повесть М. Парр о семье, потере и исцелении через маленькие добрые дела.', quote: null },
  'Чудесное путешествие Нильса с дикими гусями С. Лагерлеф': { desc: 'Путешествие мальчика с гусями по Швеции учит ответственности и уважению к природе.', quote: null },
  'Чудесное путешествие Нильса с дикими гусями С. Лагерлеф, 2 часть': { desc: 'Продолжение приключений Нильса раскрывает путь взросления и верность друзьям.', quote: null },
  'Полианна Э. Портер': { desc: 'Книга о девочке, которая меняет мир вокруг силой благодарности и участия.', quote: null },
  'Калиф-аист, Маленький Мук В. Гауф': { desc: 'Сказки Гауфа о волшебных превращениях, испытаниях и награде за смекалку.', quote: null }
};

function getTaleInfo(title) {
  if (TALE_INFO[title]) return TALE_INFO[title];
  return { desc: 'Уточните название сказки — напишите команде Читательства.', quote: null };
}

var CHIT_SCHEDULE = {
  '1': {
    lessons: ['15 июля', '3 августа', '31 августа', '31 августа'],
    weekdays: ['среда', 'понедельник', 'понедельник', 'понедельник'],
    meetings: ['16 июля', '23 июля', '30 июля', '6 августа'],
    meetingWeekdays: ['четверг', 'четверг', 'четверг', 'четверг']
  },
  '2': {
    lessons: ['7 сентября', '7 сентября', '14 сентября', '14 сентября'],
    weekdays: ['понедельник', 'понедельник', 'понедельник', 'понедельник'],
    meetings: ['10 сентября', '17 сентября', '24 сентября', '1 октября'],
    meetingWeekdays: ['четверг', 'четверг', 'четверг', 'четверг']
  }
};

var CHIT_SINGLE_MEETINGS_ISO = {
  '1': ['2026-07-16', '2026-07-23', '2026-07-30', '2026-08-06'],
  '2': ['2026-09-10', '2026-09-17', '2026-09-24', '2026-10-01']
};

var CHIT_LESSON_OPENS_ISO = {
  '1': ['2026-07-15', '2026-08-03', '2026-08-31', '2026-08-31'],
  '2': ['2026-09-07', '2026-09-07', '2026-09-14', '2026-09-14']
};

/** Early-курсы (Буквы / Истории), модуль 1: 4 встречи по четвергам */
var CHIT_EARLY_SCHEDULE = {
  meetings: ['3 сентября', '10 сентября', '17 сентября', '24 сентября'],
  meetingWeekdays: ['четверг', 'четверг', 'четверг', 'четверг'],
  meetingsIso: ['2026-09-03', '2026-09-10', '2026-09-17', '2026-09-24']
};

var MEETING_ADDON_PRICE = 799;
var WITH_TEACHER_STAGE1_CLOSED = true;

function todayIsoLocal() {
  var d = new Date();
  return d.getFullYear() + '-' +
    String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0');
}

function lessonIsOpen(stage, taleNum) {
  var dates = CHIT_LESSON_OPENS_ISO[String(stage)];
  if (!dates || !taleNum) return false;
  var open = dates[Number(taleNum) - 1];
  return !!(open && open <= todayIsoLocal());
}

function lessonOpenLabel(stage, index) {
  var s = CHIT_SCHEDULE[String(stage)];
  if (!s || index < 0) return '';
  if (lessonIsOpen(stage, index + 1)) {
    return 'Уже доступен для прохождения';
  }
  var lessonDay = lessonWeekday(stage, index);
  var lessonPrefix = lessonDay ? lessonDay + ', ' : '';
  return 'Урок откроется: ' + lessonPrefix + s.lessons[index];
}

/** Можно ли ещё докупить встречу. Блок 1 с преподавателем закрыт; блок 2 — если дата в будущем. */
function singleMeetingAddonAvailable(stage, taleNum) {
  if (String(stage) === '1') return false;
  var dates = CHIT_SINGLE_MEETINGS_ISO[String(stage)];
  if (!dates || !taleNum) return false;
  var meet = dates[Number(taleNum) - 1];
  return !!(meet && meet > todayIsoLocal());
}

function singleMeetingUnavailableLabel(stage) {
  if (String(stage) === '1') {
    return 'Только онлайн. Живые занятия по сказкам блока 1 сейчас не проводятся — выберите блок 2';
  }
  return 'Только онлайн. Занятие-квест по этой сказке уже нельзя докупить';
}

function singleMeetingAddonLine(stage, taleNum) {
  var s = CHIT_SCHEDULE[String(stage)];
  var idx = Number(taleNum) - 1;
  if (singleMeetingAddonAvailable(stage, taleNum) && s && s.meetings[idx]) {
    return {
      available: true,
      date: 'четверг, ' + s.meetings[idx]
    };
  }
  return { available: false };
}

function lessonWeekday(stage, index) {
  var s = CHIT_SCHEDULE[stage];
  return s && s.weekdays && s.weekdays[index] ? s.weekdays[index] : '';
}

function meetingWeekday(stage, index) {
  var s = CHIT_SCHEDULE[stage];
  return s && s.meetingWeekdays && s.meetingWeekdays[index] ? s.meetingWeekdays[index] : 'четверг';
}

function taleScheduleHtml(stage, index, tariff) {
  var s = CHIT_SCHEDULE[stage];
  if (!s || index < 0 || index > 3) return '';
  var taleNum = index + 1;
  var html = '<div class="tale-schedule">';
  if (tariff === 'single') {
    html += '<span class="tale-schedule__line"><strong>' + lessonOpenLabel(stage, index) + '</strong></span>';
  } else if (tariff === 'with_teacher') {
    html += '<span class="tale-schedule__meet">Встреча с преподавателем: <strong>' + meetingWeekday(stage, index) + ', ' + s.meetings[index] + '</strong></span>';
    html += '<span class="tale-schedule__line">' + lessonOpenLabel(stage, index) + '</span>';
  } else {
    html += '<span class="tale-schedule__line"><strong>' + lessonOpenLabel(stage, index) + '</strong></span>';
  }
  html += '</div>';
  return html;
}

/** Расписание встреч early: уроки 1–2 → 1-я встреча, 3–4 → 2-я и т.д. */
function earlyScheduleHtml(index, tariff) {
  if (tariff !== 'with_teacher') return '';
  var s = CHIT_EARLY_SCHEDULE;
  if (!s || !s.meetings || index < 0) return '';
  var mi = Math.min(3, Math.floor(index / 2));
  var day = (s.meetingWeekdays && s.meetingWeekdays[mi]) || 'четверг';
  return '<div class="tale-schedule">' +
    '<span class="tale-schedule__meet">Встреча с преподавателем: <strong>' + day + ', ' + s.meetings[mi] + '</strong></span>' +
    '</div>';
}

function renderPeriod(title, rows, stageKey, groupKey) {
  var sched = CHIT_SCHEDULE[stageKey];
  var enrollBase = groupKey && COURSE_PAGES[groupKey] ? COURSE_PAGES[groupKey] + '#enroll' : '#program';
  var cards = rows.map(function(r, i) {
    var info = getTaleInfo(r[1]);
    var quoteHtml = info.quote ? '<p class="tale-card__quote">' + info.quote + '</p>' : '';
    var open = lessonIsOpen(stageKey, i + 1);
    var datesHtml = sched
      ? '<div class="tale-card__dates">' +
          '<span class="tale-card__date' + (open ? ' tale-card__date--open' : '') + '">' +
            (open ? 'Уже доступен для прохождения' : ('Урок откроется: ' + (lessonWeekday(stageKey, i) || 'пн') + ' ' + sched.lessons[i])) +
          '</span>' +
        '</div>'
      : '';
    return '<div class="tale-card" tabindex="0" role="button" aria-label="' + r[1] + '">' +
      '<div class="tale-card__week">Сказка ' + r[0] + '</div>' +
      '<div class="tale-card__title">' + r[1] + '</div>' +
      datesHtml +
      '<p class="tale-card__desc">' + info.desc + '</p>' +
      quoteHtml +
      '<p class="tale-card__action"><a href="' + enrollBase + '">→ записаться на эту сказку</a></p>' +
      '</div>';
  }).join('');
  return '<div class="prog-period"><div class="prog-period__title">' + title + '</div><div class="tale-cards">' + cards + '</div></div>';
}

function buildAccordion(containerId, items) {
  var el = document.getElementById(containerId);
  if (!el) return;
  items.forEach(function(item) {
    var courseUrl = item.group && COURSE_PAGES[item.group] ? COURSE_PAGES[item.group] : '';
    var courseLink = courseUrl
      ? '<p class="prog-course-link"><a href="' + courseUrl + '">Подробнее о курсе →</a></p>'
      : '';
    var div = document.createElement('div');
    div.className = 'acc-item';
    div.innerHTML =
      '<button type="button" class="acc-head">' + item.title + '</button>' +
      '<div class="acc-body">' +
        (item.intro ? '<p>' + item.intro + '</p>' : '') +
        courseLink +
        renderPeriod('Блок 1 · сказки 1–4', item.june, '1', item.group) +
        renderPeriod('Блок 2 · сказки 5–8', item.july, '2', item.group) +
      '</div>';
    el.appendChild(div);
  });
  el.addEventListener('click', function(e) {
    var head = e.target.closest('.acc-head');
    if (!head) return;
    var body = head.nextElementSibling;
    var open = body.classList.contains('is-open');
    el.querySelectorAll('.acc-head').forEach(function(h) { h.classList.remove('is-open'); });
    el.querySelectorAll('.acc-body').forEach(function(b) { b.classList.remove('is-open'); });
    if (!open) { head.classList.add('is-open'); body.classList.add('is-open'); }
    fixTildaLayout();
  });
}

buildAccordion('acc-basic', PROGRAMS.basic);
buildAccordion('acc-extra', PROGRAMS.extra);

(function wireCourseHubLinks() {
  var hub = document.querySelector('.hero__actions a.btn--outline[href="#programs"]');
  if (hub) hub.setAttribute('href', COURSE_HUB);
})();

var faqList = document.getElementById('faq-list');
if (faqList) {
  faqList.addEventListener('click', function(e) {
    var q = e.target.closest('.faq-q');
    if (!q) return;
    var a = q.nextElementSibling;
    var open = q.classList.contains('is-open');
    document.querySelectorAll('.faq-q').forEach(function(x) { x.classList.remove('is-open'); });
    document.querySelectorAll('.faq-a').forEach(function(x) { x.classList.remove('is-open'); });
    if (!open) { q.classList.add('is-open'); a.classList.add('is-open'); }
    fixTildaLayout();
  });
}

(function () {
  var MODULES = {
    'grade-1': { single: 1, self_paced: 2, with_teacher: 3, label: '1 класс' },
    'grade-2': { single: 4, self_paced: 5, with_teacher: 6, label: '2 класс' },
    'grade-3': { single: 7, self_paced: 8, with_teacher: 9, label: '3 класс' },
    'grade-4': { single: 10, self_paced: 11, with_teacher: 12, label: '4 класс' },
    'extra-6-8': { single: 13, self_paced: 14, with_teacher: 15, label: '6–8 лет' },
    'extra-9-11': { single: 16, self_paced: 17, with_teacher: 18, label: '9–11 лет' },
    'early-letters': { single: 26, self_paced: 21, with_teacher: 22, trial: 20, label: 'Буквы оживают' },
    'early-stories': { single: 27, self_paced: 24, with_teacher: 25, trial: 23, label: 'Первые истории' },
    'wind': { single: 28, self_paced: 29, with_teacher: 30, label: 'Ветер в ивах' },
    'garden': { single: 31, self_paced: 32, with_teacher: 33, label: 'Таинственный сад' },
    'rus-6-9': { single: 34, self_paced: 35, with_teacher: 36, label: 'Русские сказки · 6–9 лет' },
    'rus-10-12': { single: 37, self_paced: 38, with_teacher: 39, label: 'Русские сказки · 10–12 лет' }
  };
  var NO_WITH_TEACHER_GROUPS = ['grade-1', 'grade-2', 'grade-3', 'grade-4', 'extra-6-8', 'extra-9-11'];
  var COHORT_GROUPS = ['wind', 'garden', 'rus-6-9', 'rus-10-12'];
  var TARIFF_LABEL = { single: 'Разовое', self_paced: 'Индивидуальное', with_teacher: 'С преподавателем', trial: 'Пробный' };
  var TARIFF_PRICE = { single: 799, self_paced: 1990, with_teacher: 4990, trial: 0 };
  var STAGE_LABEL = { '1': 'Блок 1 · сказки 1–4', '2': 'Блок 2 · сказки 5–8' };
  var STAGE_LABEL_EARLY = { '1': 'Модуль 1 · 8 уроков' };
  var ORDER_PRODUCTS = {
    single: { title: 'Читательство · Разовое', price: 799, uid: '797131986522', lid: '863983274147', sku: 'SKU0001-2' },
    self_paced: { title: 'Читательство · Индивидуальное', price: 1990, uid: '206548598642', lid: '205285061796', sku: 'SKU0002' },
    with_teacher: { title: 'Читательство · С преподавателем', price: 4990, uid: '956231952022', lid: '776534181255', sku: 'SKU0003' }
  };
  var ST100_RECID = '2379461281';
  var PAY_PAGE_URL = 'https://chitatelstvo.ru/oplata';
  var orderConfigReady = Promise.resolve();

  function isOnPayPage() {
    return window.location.pathname.replace(/\/+$/, '').indexOf('/oplata') >= 0;
  }

  function usesPayPageRedirect() {
    return !!PAY_PAGE_URL && !isOnPayPage() && !findSt100Root();
  }

  function applyOrderConfig(cfg) {
    if (!cfg) return;
    if (cfg.pay_page_url) PAY_PAGE_URL = String(cfg.pay_page_url);
    if (!cfg.products) return;
    Object.keys(ORDER_PRODUCTS).forEach(function(key) {
      var src = cfg.products[key];
      if (!src) return;
      if (src.title) ORDER_PRODUCTS[key].title = src.title;
      if (src.price) ORDER_PRODUCTS[key].price = src.price;
      if (src.uid) ORDER_PRODUCTS[key].uid = String(src.uid);
      if (src.lid) ORDER_PRODUCTS[key].lid = String(src.lid);
      if (src.sku) ORDER_PRODUCTS[key].sku = String(src.sku);
    });
  }

  function ensureCatalogBridge() {
    if (document.getElementById('chit-catalog-bridge')) return;
    var host = document.getElementById('rec' + ST100_RECID) || document.body;
    var wrap = document.createElement('div');
    wrap.id = 'chit-catalog-bridge';
    wrap.setAttribute('aria-hidden', 'true');
    wrap.style.cssText = 'position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;';
    Object.keys(ORDER_PRODUCTS).forEach(function(key) {
      var p = ORDER_PRODUCTS[key];
      if (!p || !p.uid) return;
      var card = document.createElement('div');
      card.className = 'js-product t-store__card-one';
      card.setAttribute('data-product-uid', p.uid);
      card.setAttribute('data-product-lid', p.lid || p.uid);
      card.setAttribute('data-product-gen-uid', p.uid);
      card.setAttribute('data-product-inv', '');
      var nameEl = document.createElement('div');
      nameEl.className = 'js-product-name';
      nameEl.textContent = p.title;
      var priceEl = document.createElement('div');
      priceEl.className = 'js-product-price js-store-prod-price-val';
      priceEl.setAttribute('data-product-price-range-val', String(p.price));
      priceEl.textContent = String(p.price);
      var link = document.createElement('a');
      link.href = '#order:' + p.title + '=' + p.price + ':::uid=' + p.uid;
      link.setAttribute('aria-hidden', 'true');
      card.appendChild(nameEl);
      card.appendChild(priceEl);
      card.appendChild(link);
      wrap.appendChild(card);
    });
    host.appendChild(wrap);
  }

  function buildOrderHashes(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p || !p.uid) return [];
    return [
      'order:::uid=' + p.uid,
      'order:' + p.title + '=' + p.price + ':::uid=' + p.uid
    ];
  }

  function triggerOrderHash(hashBody) {
    if (window.location.hash) {
      history.replaceState(null, '', window.location.pathname + window.location.search);
    }
    var root = document.getElementById('rec' + ST100_RECID) || document.querySelector('.t706') || document.body;
    var link = document.createElement('a');
    link.href = '#' + hashBody;
    link.setAttribute('aria-hidden', 'true');
    link.style.cssText = 'position:absolute;left:-9999px;top:0;width:1px;height:1px;opacity:0;pointer-events:none;';
    root.appendChild(link);
    link.click();
    root.removeChild(link);
    try { window.dispatchEvent(new HashChangeEvent('hashchange')); } catch (e) { window.dispatchEvent(new Event('hashchange')); }
  }

  orderConfigReady = new Promise(function(resolve) {
    function load() {
      fetch('https://api.chitatelstvo.ru/assets/order-config.json?v=5', { cache: 'no-store' })
        .then(function(r) { return r.ok ? r.json() : null; })
        .then(function(cfg) { applyOrderConfig(cfg); resolve(); })
        .catch(function() { resolve(); });
    }
    if ('requestIdleCallback' in window) {
      requestIdleCallback(load, { timeout: 3000 });
    } else {
      setTimeout(load, 1500);
    }
  });
  var TALES = {
    'grade-1': {
      '1': ['Царевна лягушка', 'Рассказы из Азбуки Л.Н. Толстой', 'Рассказы Н. Носова (Ступеньки, Заплатка, Затейники, Шляпа)', 'Кот в сапогах, Мальчик с пальчик Ш. Перро'],
      '2': ['По щучьему велению', 'Сказка о мёртвой царевне и о семи богатырях А.С. Пушкин', 'Принцесса на горошине, Дюймовочка Г. Андерсен', 'Аля, Кляксич и буква А И.П. Токмакова']
    },
    'grade-2': {
      '1': ['Сказка о рыбаке и рыбке А.С. Пушкин', 'Цветик-семицветик В.П. Катаев', 'Как муравьишка домой добирался, Где раки зимуют В.В. Бианки', 'Гадкий утёнок Г. Андерсен'],
      '2': ['Филипок + Азбука Л.Н. Толстой', 'Незнайка на Луне Н. Носов', 'Рикки-Тикки-Тави Р. Киплинг', 'Маленькая Баба-Яга, Маленький водяной О. Пройслер']
    },
    'grade-3': {
      '1': ['Сказка о царе Салтане, о сыне его славном и могучем богатыре А.С. Пушкин', 'Сказка про храброго зайца, Серая Шейка Д.Н. Мамин-Сибиряк', 'Черная курица или Подземные жители А. Погорельский', 'Чудесный доктор А. Куприн'],
      '2': ['Сказка о молодильных яблоках и живой воде, Волшебное кольцо', 'Серебряный рубль В. Одоевский', 'Аленький цветочек С.Т. Аксаков', 'Королевство кривых зеркал В. Губарев']
    },
    'grade-4': {
      '1': ['Уральские сказы П. Бажов', 'Сказка о потерянном времени Е. Шварц', 'Три толстяка Ю. Олеша', 'Остров Сокровищ Р. Стивенсон'],
      '2': ['Приключения Тома Сойера М. Твен', 'Белый Бим, Черное ухо Г. Троепольский', 'Пеппи Длинный чулок А. Линдгрен', 'Путешествия Гулливера Дж. Свифт']
    },
    'extra-6-8': {
      '1': ['Плюшевый заяц, или как игрушки становятся настоящими У. Марджери', 'Муми-тролль и комета Т. Янссон', 'Шляпа волшебника Т. Янссон', 'Приключения медвежонка Паддингтона М. Бонд'],
      '2': ['Невероятные приключения кролика Эдварда К. ДиКамилло', 'Тутта Карлссон Первая и единственная, Людвиг Четырнадцатый и др. Я. Экхольм', 'Карлик Нос В. Гауф', 'Чарли и шоколадная фабрика Р. Даль']
    },
    'extra-9-11': {
      '1': ['Опасное лето Т. Янссон', 'Рони, дочь разбойника А. Линдгрен', 'Собака Пес Д. Пеннак', 'Вафельное сердце М. Парр'],
      '2': ['Чудесное путешествие Нильса с дикими гусями С. Лагерлеф', 'Чудесное путешествие Нильса с дикими гусями С. Лагерлеф, 2 часть', 'Полианна Э. Портер', 'Калиф-аист, Маленький Мук В. Гауф']
    },
    'early-letters': {
      '1': ['Мотор на поляне', 'Поющая У', 'Круглая О', 'Змейка: с-с-с!', 'Рычит буква Р', 'Слоги дружат', 'Первые слова', 'Праздник у Словика']
    },
    'early-stories': {
      '1': ['Кот и коробка', 'Дождь за окном', 'Где мяч?', 'Словик проверяет память', 'Мокрый кот', 'Кот и плед', 'Словик пришёл', 'Словик дома']
    },
    'wind': {
      '1': ['Знакомство с книгой', 'Читаем дальше', 'Главные герои', 'Итог модуля']
    },
    'garden': {
      '1': ['Знакомство с книгой', 'Читаем дальше', 'Тайна сада', 'Итог модуля']
    },
    'rus-6-9': {
      '1': ['Урок 1', 'Урок 2', 'Урок 3', 'Урок 4']
    },
    'rus-10-12': {
      '1': ['Урок 1', 'Урок 2', 'Урок 3', 'Урок 4']
    }
  };
  var state = { group: '', tariff: '', stage: '', taleNum: 0 };

  function isEarlyGroup(group) {
    var g = group || state.group;
    return !!(g && g.indexOf('early-') === 0);
  }

  function isCohortGroup(group) {
    var g = group || state.group;
    return !!(g && COHORT_GROUPS.indexOf(g) >= 0);
  }

  function usesLessonLabels(group) {
    return isEarlyGroup(group) || isCohortGroup(group);
  }

  function refreshTariffAvailability() {
    var teachCard = document.querySelector('#chit-tariffs [data-tariff="with_teacher"]');
    if (!teachCard) return;
    var blocked = state.group && NO_WITH_TEACHER_GROUPS.indexOf(state.group) >= 0;
    teachCard.classList.toggle('is-disabled', blocked);
    teachCard.setAttribute('aria-disabled', blocked ? 'true' : 'false');
    if (blocked && state.tariff === 'with_teacher') {
      state.tariff = 'self_paced';
      var selfCard = document.querySelector('#chit-tariffs [data-tariff="self_paced"]');
      if (selfCard) {
        document.querySelectorAll('#chit-tariffs .pick-card').forEach(function(c) {
          c.classList.toggle('is-active', c === selfCard);
        });
      }
    }
  }

  function cohortScheduleHtml(index) {
    var dates = {
      'wind': ['7 сентября', '14 сентября', '21 сентября', '28 сентября'],
      'garden': ['7 сентября', '14 сентября', '21 сентября', '28 сентября'],
      'rus-6-9': ['5 октября', '12 октября', '19 октября', '26 октября'],
      'rus-10-12': ['5 октября', '12 октября', '19 октября', '26 октября']
    };
    var list = dates[state.group];
    if (!list || !list[index]) return '';
    return '<span class="tale-btn__meta">откроется ' + list[index] + ' · понедельник</span>';
  }

  function stageLabelFor(stage) {
    if (isCohortGroup()) return 'Модуль · 4 занятия';
    if (isEarlyGroup()) return STAGE_LABEL_EARLY[stage] || ('Модуль ' + stage);
    return STAGE_LABEL[stage] || stage;
  }

  function applyEnrollDefaults() {
    // Сразу заполняем форму: так не теряются на пустых шагах.
    // Класс и основной тариф; для «С преподавателем» — блок 2 (кроме early).
    if (!state.group) {
      state.group = 'grade-1';
      var gBtn = document.querySelector('#chit-groups-basic [data-group="grade-1"]');
      if (gBtn) {
        document.querySelectorAll('#chit-groups-basic .pill, #chit-groups-extra .pill, #chit-groups-early .pill, #chit-groups-cohort .pill').forEach(function(p) {
          p.classList.toggle('is-active', p === gBtn);
        });
      }
    }
    if (!state.tariff) {
      state.tariff = 'self_paced';
      var tCard = document.querySelector('#chit-tariffs [data-tariff="self_paced"]');
      if (tCard) {
        document.querySelectorAll('#chit-tariffs .pick-card').forEach(function(c) {
          c.classList.toggle('is-active', c === tCard);
        });
      }
    }
    if (!state.stage) {
      state.stage = (state.tariff === 'with_teacher' && WITH_TEACHER_STAGE1_CLOSED && !isEarlyGroup() && !isCohortGroup()) ? '2' : '1';
      document.querySelectorAll('#chit-stages .pill').forEach(function(p) {
        p.classList.toggle('is-active', p.getAttribute('data-stage') === state.stage);
      });
    }
    showDateBox();
    renderTales();
    syncHidden();
    refreshTariffAvailability();
  }
  var elSummary = document.getElementById('chit-summary');
  var elDateBox = document.getElementById('chit-date-box');
  var elPreview = document.getElementById('chit-block-preview');
  var elTales = document.getElementById('chit-tales');
  var hidMid = document.getElementById('module_id');
  var hidStage = document.getElementById('chosen_stage');
  var hidTale = document.getElementById('chosen_tale_number');
  var payBtn = document.getElementById('chit-pay-btn');

  function formatPrice(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ' ₽';
  }

  function isTariffReadyForPay() {
    var ready = state.group && state.tariff;
    if (state.tariff === 'single') ready = ready && state.stage && state.taleNum;
    else if (state.tariff) ready = ready && state.stage;
    return !!ready;
  }

  var promoQuotePrice = null;
  var promoQuotePending = false;
  var promoQuoteTimer = null;

  function resetTcartPromoState() {
    if (!window.tcart) return;
    delete window.tcart.promocode;
    delete window.tcart.prodamount_withdiscount;
    delete window.tcart.prodamount_discountsum;
  }

  function refreshTcartTotals() {
    if (typeof window.tcart__updateTotalProductsinCartObj === 'function') {
      window.tcart__updateTotalProductsinCartObj();
    }
    if (typeof window.tcart__calcPromocode === 'function' && window.tcart && typeof window.tcart.amount === 'number') {
      window.tcart.amount = window.tcart__calcPromocode(window.tcart.amount);
    }
    if (typeof window.tcart__reDrawTotal === 'function') {
      window.tcart__reDrawTotal();
    }
    if (typeof window.tcart__saveLocalObj === 'function') {
      window.tcart__saveLocalObj();
    }
  }

  function findPromoControls() {
    var input = document.querySelector('.t706 .t-inputpromocode, .t706__orderform .t-inputpromocode, .t706__cartwin .t-inputpromocode');
    if (!input) return null;
    var wrapper = input.closest('.t-inputpromocode__wrapper');
    var btn = wrapper
      ? wrapper.querySelector('.t-inputpromocode__btn')
      : document.querySelector('.t706 .t-inputpromocode__btn');
    return btn ? { input: input, btn: btn } : null;
  }

  function canPreviewPromoQuote() {
    return !!findPromoControls();
  }

  function readQuotedPriceFromTcart() {
    if (!window.tcart || !window.tcart.promocode || window.tcart.promocode.message !== 'OK') return null;
    if (typeof window.tcart.prodamount_withdiscount === 'number' && window.tcart.prodamount_withdiscount >= 0) {
      return Math.round(window.tcart.prodamount_withdiscount);
    }
    if (typeof window.tcart.amount === 'number' && window.tcart.amount >= 0) {
      return Math.round(window.tcart.amount);
    }
    return null;
  }

  function updatePayButton() {
    if (!payBtn) return;
    var ready = isTariffReadyForPay();
    var base = ready && state.tariff ? TARIFF_PRICE[state.tariff] : 0;
    if (ready && base) {
      payBtn.disabled = false;
      var price = promoQuotePrice != null ? promoQuotePrice : base;
      if (promoQuotePending && getPromoCodeValue()) {
        payBtn.textContent = 'Оплатить — ' + formatPrice(base) + '…';
      } else {
        payBtn.textContent = 'Оплатить — ' + formatPrice(price);
      }
    } else {
      payBtn.disabled = true;
      payBtn.textContent = 'Оплатить';
      promoQuotePrice = null;
      promoQuotePending = false;
    }
  }

  function schedulePromoQuoteRefresh() {
    if (promoQuoteTimer) clearTimeout(promoQuoteTimer);
    promoQuoteTimer = setTimeout(refreshPromoQuote, 700);
  }

  function refreshPromoQuote() {
    promoQuoteTimer = null;
    if (!isTariffReadyForPay()) {
      promoQuotePrice = null;
      promoQuotePending = false;
      updatePayButton();
      return;
    }
    var code = getPromoCodeValue();
    if (!code) {
      lastAppliedPromo = '';
      promoQuotePrice = null;
      promoQuotePending = false;
      updatePayButton();
      return;
    }
    if (!canPreviewPromoQuote()) {
      promoQuotePrice = null;
      promoQuotePending = false;
      updatePayButton();
      return;
    }
    promoQuotePending = true;
    updatePayButton();
    ensureCatalogBridge();
    waitTcartReady(function() {
      if (!addProductDirect(state.tariff)) {
        promoQuotePending = false;
        promoQuotePrice = null;
        updatePayButton();
        return;
      }
      lastAppliedPromo = '';
      applyPromoCodeFromForm();
      var attempts = 0;
      function poll() {
        attempts += 1;
        refreshTcartTotals();
        var quoted = readQuotedPriceFromTcart();
        if (quoted != null) {
          promoQuotePrice = quoted;
          promoQuotePending = false;
          updatePayButton();
          return;
        }
        if (window.tcart && window.tcart.promocode && window.tcart.promocode.message && window.tcart.promocode.message !== 'OK') {
          promoQuotePrice = null;
          promoQuotePending = false;
          updatePayButton();
          return;
        }
        if (attempts >= 30) {
          promoQuotePending = false;
          promoQuotePrice = null;
          updatePayButton();
          return;
        }
        setTimeout(poll, 250);
      }
      setTimeout(poll, 350);
    });
  }

  var CART_FIELD_ALIASES = {
    parent_name: ['parent_name', 'Name', 'name', 'nm', 'your_name'],
    parent_email: ['parent_email', 'Email', 'email'],
    parent_telegram: ['parent_telegram', 'Phone', 'phone', 'tel', 'your_phone'],
    child_name: ['child_name', 'childname'],
    child_birth_date: ['child_birth_date', 'birth_date', 'childbirthdate'],
    child_age: ['child_age', 'childage'],
    promo_code: ['promo_code', 'promocode', 'promo'],
    notification_channel: ['notification_channel'],
    module_id: ['module_id'],
    chosen_stage: ['chosen_stage'],
    chosen_tale_number: ['chosen_tale_number']
  };
  var lastAppliedPromo = '';

  function ageFromBirthDate(isoDate) {
    if (!isoDate) return '';
    var parts = String(isoDate).split('-');
    if (parts.length !== 3) return '';
    var birth = new Date(+parts[0], +parts[1] - 1, +parts[2]);
    if (isNaN(birth.getTime())) return '';
    var today = new Date();
    var age = today.getFullYear() - birth.getFullYear();
    var monthDelta = today.getMonth() - birth.getMonth();
    if (monthDelta < 0 || (monthDelta === 0 && today.getDate() < birth.getDate())) age -= 1;
    return age >= 0 ? String(age) : '';
  }

  function setInputValue(dst, v) {
    if (!dst || dst.closest('#chit-main')) return;
    if (dst.value === v) return;
    dst.value = v;
    try { dst.dispatchEvent(new Event('input', { bubbles: true })); } catch (e) {}
    try { dst.dispatchEvent(new Event('change', { bubbles: true })); } catch (e) {}
  }

  function pushField(name, val) {
    var v = val == null ? '' : String(val);
    var names = CART_FIELD_ALIASES[name] || [name];
    if (names.indexOf(name) < 0) names.unshift(name);
    names.forEach(function(fieldName) {
      var sels = [
        '.t706 input[name="' + fieldName + '"]:not([type="checkbox"])',
        '.t706 select[name="' + fieldName + '"]',
        '.t706 textarea[name="' + fieldName + '"]',
        '.t-store input[name="' + fieldName + '"]:not([type="checkbox"])',
        '.t-store select[name="' + fieldName + '"]',
        '.t-store textarea[name="' + fieldName + '"]',
        'form[data-formcart="y"] input[name="' + fieldName + '"]:not([type="checkbox"])',
        'form[data-formcart="y"] select[name="' + fieldName + '"]'
      ];
      sels.forEach(function(sel) {
        document.querySelectorAll(sel).forEach(function(dst) {
          setInputValue(dst, v);
        });
      });
    });
  }

  function getPromoCodeValue() {
    var el = document.querySelector('#chit-main [name="promo_code"]');
    return el ? String(el.value || '').trim() : '';
  }

  function promoAlreadyApplied(code) {
    if (!code || !window.tcart || typeof window.tcart.promocode !== 'object') return false;
    var promo = window.tcart.promocode;
    if (promo.message !== 'OK') return false;
    var saved = String(promo.code || promo.promocode || '').trim();
    return saved.toLowerCase() === code.toLowerCase();
  }

  function applyPromoCodeFromForm() {
    var code = getPromoCodeValue();
    if (!code) {
      lastAppliedPromo = '';
      return false;
    }
    if (code === lastAppliedPromo && promoAlreadyApplied(code)) return true;
    var controls = findPromoControls();
    if (!controls) return false;
    pushField('promo_code', code);
    setInputValue(controls.input, code);
    controls.btn.style.display = 'table-cell';
    try { controls.input.dispatchEvent(new Event('input', { bubbles: true })); } catch (e) {}
    try { controls.input.dispatchEvent(new Event('change', { bubbles: true })); } catch (e) {}
    try { controls.btn.click(); } catch (e) {}
    lastAppliedPromo = code;
    return true;
  }

  function syncCartAfterOpen() {
    syncToCartForm();
    applyPromoCodeFromForm();
    [150, 400, 900, 1600].forEach(function(ms) {
      setTimeout(function() {
        syncToCartForm();
        applyPromoCodeFromForm();
      }, ms);
    });
  }

  function watchCartModal() {
    var cartWin = document.querySelector('.t706__cartwin');
    if (!cartWin || cartWin._chitWatch) return;
    cartWin._chitWatch = true;
    var obs = new MutationObserver(function() {
      var visible = cartWin.style.display !== 'none' && cartWin.offsetParent !== null;
      if (visible) syncCartAfterOpen();
    });
    obs.observe(cartWin, { attributes: true, attributeFilter: ['style', 'class'] });
  }

  function pushCheckbox(name, checked) {
    var sels = [
      '.t706 input[name="' + name + '"][type="checkbox"]',
      '.t-store input[name="' + name + '"][type="checkbox"]',
      'form[data-formcart="y"] input[name="' + name + '"][type="checkbox"]'
    ];
    sels.forEach(function(sel) {
      document.querySelectorAll(sel).forEach(function(cb) {
        if (cb.closest('#chit-main')) return;
        if (!!cb.checked === !!checked) return;
        cb.checked = !!checked;
        try { cb.dispatchEvent(new Event('change', { bubbles: true })); } catch (e) {}
      });
    });
  }

  function catalogBlocksOnPage() {
    if (document.querySelector('[data-record-type="205"], [data-record-type="762"]')) return true;
    var cards = document.querySelectorAll(
      '.js-store-product[data-product-gen-uid], .js-product[data-product-uid], .t-store__card'
    );
    for (var i = 0; i < cards.length; i++) {
      if (!cards[i].closest('#chit-catalog-bridge')) return true;
    }
    return false;
  }

  function findStoreProductCard(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p || !p.uid) return null;
    var cards = document.querySelectorAll(
      '.js-store-product[data-product-gen-uid], .js-product[data-product-gen-uid], .js-product[data-product-uid]'
    );
    for (var i = 0; i < cards.length; i++) {
      var card = cards[i];
      if (card.closest('#chit-catalog-bridge')) continue;
      var genUid = card.getAttribute('data-product-gen-uid') || card.getAttribute('data-product-uid');
      if (genUid && String(genUid) === String(p.uid)) return card;
    }
    return null;
  }

  function triggerStoreBuy(tariff) {
    var card = findStoreProductCard(tariff);
    if (!card) return false;
    var rec = card.closest('.t-rec');
    var root = rec || card;
    var btn = root.querySelector(
      'a[href^="#order"], a.t762__btn, .js-store-prod-buy-btn, .t-store__prod-popup__btn, .t-store__card__btn'
    );
    if (!btn) return false;
    btn.click();
    try { window.dispatchEvent(new HashChangeEvent('hashchange')); } catch (e) { window.dispatchEvent(new Event('hashchange')); }
    return true;
  }

  var STORE_REC_TYPES = ['762', '205', '200', '210', '215', '405'];
  var STORE_REC_IDS = ['rec2380183631', 'rec2380172391', 'rec2380172421'];

  function applyStoreHide(el) {
    if (!el || el.closest('#chit-main') || el.querySelector('#chit-main')) return;
    if (el.getAttribute && el.getAttribute('data-record-type') === '396') return;
    el.classList.add('chit-store-hidden');
    el.setAttribute('aria-hidden', 'true');
    el.style.setProperty('display', 'none', 'important');
    el.style.setProperty('position', 'absolute', 'important');
    el.style.setProperty('left', '-99999px', 'important');
    el.style.setProperty('height', '0', 'important');
    el.style.setProperty('min-height', '0', 'important');
    el.style.setProperty('max-height', '0', 'important');
    el.style.setProperty('padding', '0', 'important');
    el.style.setProperty('margin', '0', 'important');
    el.style.setProperty('overflow', 'hidden', 'important');
    el.style.setProperty('visibility', 'hidden', 'important');
    el.style.setProperty('opacity', '0', 'important');
    el.style.setProperty('pointer-events', 'none', 'important');
  }

  function isStoreRec(rec) {
    if (!rec || !rec.classList || !rec.classList.contains('t-rec')) return false;
    if (rec.closest('#chit-main') || rec.querySelector('#chit-main')) return false;
    if (rec.getAttribute('data-record-type') === '396') return false;
    if (STORE_REC_IDS.indexOf(rec.id) >= 0) return true;
    var recType = rec.getAttribute('data-record-type');
    if (recType && STORE_REC_TYPES.indexOf(recType) >= 0) return true;
    if (rec.querySelector('.t-store, .js-store-product, .js-product[data-product-gen-uid], .t-store__card-one')) return true;
    var text = rec.textContent || '';
    if (/SKU0001|SKU0002|SKU0003/i.test(text) && /(?:Артикул|1[\s\u00a0]*490|1[\s\u00a0]*990|4[\s\u00a0]*990)/i.test(text)) return true;
    return false;
  }

  function chitEnsureMainVisible() {
    document.querySelectorAll('#allrecords .t-rec').forEach(function(rec) {
      if (!rec.querySelector('#chit-main')) return;
      rec.classList.remove('chit-store-hidden');
      rec.removeAttribute('aria-hidden');
      ['display', 'position', 'left', 'height', 'min-height', 'max-height', 'padding', 'margin', 'overflow', 'visibility', 'opacity', 'pointer-events'].forEach(function(prop) {
        rec.style.removeProperty(prop);
      });
    });
    var main = document.getElementById('chit-main');
    if (main) {
      main.style.removeProperty('display');
      main.style.removeProperty('visibility');
    }
  }

  function hideCatalogBlocks() {
    chitEnsureMainVisible();
    document.querySelectorAll('#allrecords .t-rec').forEach(function(rec) {
      if (isStoreRec(rec)) applyStoreHide(rec);
    });
    [
      '.t-store',
      '.t-store__prod-popup',
      '#rec2380183631',
      '#rec2380172391',
      '#rec2380172421'
    ].forEach(function(sel) {
      document.querySelectorAll(sel).forEach(applyStoreHide);
    });
  }

  function clearOrderHash() {
    if (window.location.hash && window.location.hash.indexOf('#order') === 0) {
      history.replaceState(null, '', window.location.pathname + window.location.search);
    }
  }

  function bindStoreScrollGuard() {
    if (window._chitScrollGuardBound) return;
    window._chitScrollGuardBound = true;
    var busy = false;
    var guardScheduled = false;
    function guard() {
      if (busy || guardScheduled) return;
      guardScheduled = true;
      requestAnimationFrame(function() {
        guardScheduled = false;
        if (busy) return;
        var needsFix = false;
        document.querySelectorAll('#allrecords .t-rec').forEach(function(rec) {
          if (rec.closest('#chit-main') || rec.querySelector('#chit-main')) return;
          if (rec.getAttribute('data-record-type') === '396') return;
          var text = rec.textContent || '';
          if (!/SKU0001|SKU0002|SKU0003/i.test(text) || !/Артикул/i.test(text)) return;
          var rect = rec.getBoundingClientRect();
          if (rect.height > 30 && rect.top < window.innerHeight * 0.9) {
            needsFix = true;
            applyStoreHide(rec);
          }
        });
        if (needsFix) {
          busy = true;
          clearOrderHash();
          scrollToProgram();
          setTimeout(function() { busy = false; }, 700);
        }
      });
    }
    window.addEventListener('scroll', guard, { passive: true });
  }

  function bindStoreClickBlock() {
    document.addEventListener('click', function(e) {
      var btn = e.target.closest('.js-store-prod-btn, .t-store__card__btn, .t-store__prod-popup-btn, a[href*="#order:"]');
      if (!btn || btn.closest('#chit-main')) return;
      var rec = btn.closest('.t-rec');
      if (!rec || !isStoreRec(rec)) return;
      e.preventDefault();
      e.stopPropagation();
      applyStoreHide(rec);
      scrollToProgram();
    }, true);
  }

  function scrollToProgram() {
    var program = document.getElementById('program');
    if (program) {
      program.scrollIntoView({ behavior: 'smooth', block: 'start' });
      if (window.location.hash !== '#program') {
        history.replaceState(null, '', window.location.pathname + window.location.search + '#program');
      }
      return;
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function bindCartCloseHandler() {
    function onCartClosed() {
      hideCatalogBlocks();
      clearOrderHash();
      scrollToProgram();
    }
    document.addEventListener('click', function(e) {
      if (e.target.closest('.t706__close, .t706__cartwin-close, .t706__cartwin-close-button, .t706__carticon-close, .t706__close-icon')) {
        setTimeout(onCartClosed, 150);
        setTimeout(onCartClosed, 600);
      }
    });
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') setTimeout(onCartClosed, 200);
    });
    window.addEventListener('hashchange', function() {
      hideCatalogBlocks();
      if (document.querySelector('.t706__cartwin_showed, .t706__cartwin_active, .t706__cartwin-wrapper_showed')) return;
      var h = window.location.hash || '';
      if (h.indexOf('#order') === 0 || h.indexOf('#opencart') >= 0) return;
      if (h.length > 1) {
        try {
          if (document.querySelector(h)) return;
        } catch (err) {}
      }
      setTimeout(onCartClosed, 100);
    });
  }

  function watchLazyBlocks() {
    var root = document.getElementById('allrecords');
    if (!root || root._chitLazyWatch) return;
    root._chitLazyWatch = true;
    var obs = new MutationObserver(function() {
      hideCatalogBlocks();
      watchCartModal();
      checkSt100Block();
    });
    obs.observe(root, { childList: true, subtree: true });
  }

  function isBrokenStoreProduct(card) {
    if (!card) return true;
    var nameEl = card.querySelector('.js-product-name');
    var name = nameEl ? nameEl.textContent.trim() : '';
    var price = parseProductPrice(card.querySelector('.js-store-prod-price-val, .js-product-price'));
    if (/studio headphones/i.test(name)) return true;
    if (price > 0 && price < 1000) return true;
    return false;
  }

  function reinitCatalogProducts(attempt) {
    if (typeof window.t_store_oneProduct_init !== 'function') {
      if ((attempt || 0) < 20) {
        setTimeout(function() { reinitCatalogProducts((attempt || 0) + 1); }, 250);
      }
      return;
    }
    document.querySelectorAll('.t-rec[data-record-type="762"], .t-rec[data-record-type="205"]').forEach(function(rec) {
      var card = rec.querySelector('.js-store-product[data-product-gen-uid], .js-product[data-product-gen-uid]');
      if (!card) return;
      var uid = card.getAttribute('data-product-gen-uid');
      if (!uid) return;
      var recId = rec.id ? rec.id.replace(/^rec/, '') : '';
      if (!recId) return;
      try {
        window.t_store_oneProduct_init(recId, {
          productuid: uid,
          productgenuid: uid,
          previewmode: 'no'
        });
      } catch (e) {}
    });
  }

  function hasConfiguredUids() {
    return Object.keys(ORDER_PRODUCTS).some(function(key) {
      return !!(ORDER_PRODUCTS[key].uid);
    });
  }

  function parseProductPrice(el) {
    if (!el) return 0;
    var raw = el.getAttribute('data-product-price-range-val') || el.textContent || '';
    return parseInt(String(raw).replace(/\D/g, ''), 10) || 0;
  }

  function resolveProductUid(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p) return '';
    var card = findStoreProductCard(tariff);
    if (card) {
      var pageUid = card.getAttribute('data-product-gen-uid') || card.getAttribute('data-product-uid');
      if (pageUid) return String(pageUid);
    }
    if (p.uid) return String(p.uid);
    var cards = document.querySelectorAll('.js-product[data-product-uid], [data-product-uid]');
    for (var i = 0; i < cards.length; i++) {
      var c = cards[i];
      if (c.closest('#chit-catalog-bridge')) continue;
      var uid = c.getAttribute('data-product-uid');
      if (!uid) continue;
      var nameEl = c.querySelector('.js-product-name');
      var name = nameEl ? nameEl.textContent.trim() : '';
      var price = parseProductPrice(c.querySelector('.js-product-price, .js-catalog-prod-price-val, .js-store-prod-price-val'));
      if (name === p.title || price === p.price) {
        p.uid = String(uid);
        return p.uid;
      }
    }
    return '';
  }

  function showCatalogSetupAlert() {
    alert(
      'Не удалось добавить товар в корзину.\n\n' +
      'На главной нужны 3 карточки товара из каталога (ST205 или блок «Товар» T762) ' +
      'с Product ID из CSV. После настройки — «Опубликовать».\n\n' +
      'Если на карточке «Studio Headphones» или цена 100 — товар из каталога не подтянулся, ' +
      'откройте блок заново и выберите услугу из каталога.\n\n' +
      'Подробнее: docs/tilda-zero-main/TILDA-CATALOG-LINK.md'
    );
  }

  function showPaymentNotReadyAlert() {
    alert(
      'Страница оплаты ещё не настроена в Tilda.\n\n' +
      'Один раз создайте chitatelstvo.ru/oplata (см. PAY-PAGE.md):\n' +
      'ST100 + 3× ST205 с Product ID.\n\n' +
      'На главной блоки товара не нужны — оплата только на /oplata.'
    );
  }

  function isPaymentCatalogReady() {
    return catalogBlocksOnPage();
  }

  function checkCatalogBlock() {
    var warn = document.getElementById('chit-catalog-warning');
    if (!warn) return;
    if (isOnPayPage()) {
      warn.hidden = isPaymentCatalogReady();
    } else {
      warn.hidden = true;
    }
  }

  function waitTcartReady(cb, attempt) {
    if (typeof window.tcart__addProduct === 'function' && window.tcart) {
      cb();
      return;
    }
    if ((attempt || 0) >= 40) return;
    setTimeout(function() { waitTcartReady(cb, (attempt || 0) + 1); }, 150);
  }

  function clearTcart() {
    if (!window.tcart) window.tcart = { products: [], amount: 0, total: 0, prodamount: 0 };
    window.tcart.products = [];
    window.tcart.amount = 0;
    window.tcart.total = 0;
    window.tcart.prodamount = 0;
    resetTcartPromoState();
    if (typeof window.tcart__updateTotalProductsinCartObj === 'function') {
      window.tcart__updateTotalProductsinCartObj();
    }
    if (typeof window.tcart__saveLocalObj === 'function') {
      window.tcart__saveLocalObj();
    }
    if (typeof window.tcart__reDrawCartIcon === 'function') {
      window.tcart__reDrawCartIcon();
    }
    if (typeof window.tcart__reDrawProducts === 'function') {
      window.tcart__reDrawProducts();
    }
  }

  function addProductDirect(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p || typeof window.tcart__addProduct !== 'function') return false;
    var uid = resolveProductUid(tariff);
    if (!uid) return false;
    if (!window.tcart) window.tcart = { products: [], amount: 0, total: 0, prodamount: 0 };
    clearTcart();
    var item = {
      name: p.title,
      price: p.price,
      amount: p.price,
      quantity: 1,
      recid: ST100_RECID,
      sku: p.sku || '',
      uid: uid,
      lid: p.lid || uid
    };
    window.tcart__addProduct(item);
    window.tcart.updated = Math.floor(Date.now() / 1000);
    if (typeof window.tcart__updateTotalProductsinCartObj === 'function') {
      window.tcart__updateTotalProductsinCartObj();
    }
    if (typeof window.tcart__saveLocalObj === 'function') {
      window.tcart__saveLocalObj();
    }
    if (typeof window.tcart__reDrawCartIcon === 'function') {
      window.tcart__reDrawCartIcon();
    }
    if (typeof window.tcart__reDrawProducts === 'function') {
      window.tcart__reDrawProducts();
    }
    if (typeof window.tcart__reDrawTotal === 'function') {
      window.tcart__reDrawTotal();
    }
    return !!(window.tcart.products && window.tcart.products.length);
  }

  function cartHasItems() {
    if (window.tcart && window.tcart.products && window.tcart.products.length > 0) return true;
    var counter = document.querySelector('.js-carticon-counter, .t706__carticon-counter');
    if (counter) {
      var n = parseInt(String(counter.textContent || '').replace(/\D/g, ''), 10);
      if (n > 0) return true;
    }
    var list = document.querySelector('.t706__cartwin-products');
    if (list && list.querySelector('.t706__product, .t706__cartitem, [data-product-id]')) return true;
    return false;
  }

  function openCartModal() {
    syncToCartForm();
    if (typeof window.tcart__openCart === 'function') {
      window.tcart__openCart();
    } else if (window.tcart && typeof window.tcart.open === 'function') {
      window.tcart.open();
    } else {
      var icon = document.querySelector('.t706__carticon');
      if (icon) icon.click();
    }
    if (typeof window.tcart__reDrawProducts === 'function') {
      window.tcart__reDrawProducts();
    }
    if (typeof window.tcart__reDrawTotal === 'function') {
      window.tcart__reDrawTotal();
    }
    watchCartModal();
    syncCartAfterOpen();
    setTimeout(function() {
      hideCatalogBlocks();
      clearOrderHash();
    }, 250);
    return true;
  }

  function fillCartFormAggressive() {
    var form = document.querySelector('.t706__orderform form, form[data-formcart="y"]');
    if (!form || form.closest('#chit-main')) return;

    function src(name) {
      var el = document.querySelector('#chit-main [name="' + name + '"]');
      return el ? el.value : '';
    }

    var parentName = src('parent_name');
    var parentEmail = src('parent_email');
    var parentTelegram = src('parent_telegram');
    var childName = src('child_name');
    var childBirthDate = src('child_birth_date');
    var childAge = ageFromBirthDate(childBirthDate) || src('child_age');

    form.querySelectorAll('input[type="email"]').forEach(function(el) {
      if (parentEmail) setInputValue(el, parentEmail);
    });

    form.querySelectorAll('input[type="tel"], .t-input-phonemask__value').forEach(function(el) {
      if (parentTelegram) setInputValue(el, parentTelegram);
    });

    var textInputs = [];
    form.querySelectorAll('input[type="text"], input:not([type]), textarea').forEach(function(el) {
      if (el.type === 'hidden' || el.closest('.t-input-phonemask')) return;
      textInputs.push(el);
    });

    if (parentName && textInputs[0]) setInputValue(textInputs[0], parentName);
    if (childName && textInputs[1]) setInputValue(textInputs[1], childName);
    if (childBirthDate && textInputs[2]) setInputValue(textInputs[2], childBirthDate);
    else if (childAge && textInputs[2]) setInputValue(textInputs[2], childAge);

    form.querySelectorAll('input[type="hidden"]').forEach(function(el) {
      var n = el.name || '';
      if (n === 'module_id' && hidMid) setInputValue(el, hidMid.value);
      if (n === 'chosen_stage' && hidStage) setInputValue(el, hidStage.value);
      if (n === 'chosen_tale_number' && hidTale) setInputValue(el, hidTale.value);
    });
  }

  function syncToCartForm() {
    pushField('module_id', hidMid ? hidMid.value : '');
    pushField('chosen_stage', hidStage ? hidStage.value : '');
    pushField('chosen_tale_number', hidTale ? hidTale.value : '');
    pushField('notification_channel', 'email');
    pushField('promo_code', getPromoCodeValue());
    ['parent_name', 'parent_email', 'parent_telegram', 'child_name', 'child_birth_date'].forEach(function(name) {
      var el = document.querySelector('#chit-main [name="' + name + '"]');
      if (el) pushField(name, el.value);
    });
    var birthEl = document.querySelector('#chit-main [name="child_birth_date"]');
    if (birthEl && birthEl.value) {
      pushField('child_age', ageFromBirthDate(birthEl.value));
    }
    fillCartFormAggressive();
    pushCheckbox('legal_consent', true);
  }

  function findSt100Root() {
    return document.querySelector('.t706, form[data-formcart="y"]');
  }

  function checkSt100Block() {
    var warn = document.getElementById('chit-st100-warning');
    if (!warn) return;
    // Оплата на /oplata — служебную плашку родителям не показываем
    warn.hidden = true;
    warn.setAttribute('hidden', '');
    warn.style.setProperty('display', 'none', 'important');
    if (warn.parentNode) warn.parentNode.removeChild(warn);
  }

  function bindContactSync() {
    ['parent_name', 'parent_email', 'parent_telegram', 'child_name', 'child_birth_date', 'promo_code'].forEach(function(name) {
      var el = document.querySelector('#chit-main [name="' + name + '"]');
      if (!el) return;
      function syncContact() {
        pushField(name, el.value);
        if (name === 'child_birth_date') pushField('child_age', ageFromBirthDate(el.value));
      }
      el.addEventListener('input', syncContact);
      el.addEventListener('change', syncContact);
    });
  }

  function scrollToCheckout() {
    var st100 = findSt100Root();
    if (st100) {
      st100.scrollIntoView({ behavior: 'smooth', block: 'start' });
      return;
    }
    var warn = document.getElementById('chit-st100-warning');
    if (warn && !warn.hidden) warn.scrollIntoView({ behavior: 'smooth', block: 'center' });
    else document.getElementById('program').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function collectCheckoutPayload(tariff) {
    function val(name) {
      var el = document.querySelector('#chit-main [name="' + name + '"]');
      return el ? el.value : '';
    }
    return {
      tariff: tariff,
      module_id: hidMid ? hidMid.value : '',
      chosen_stage: hidStage ? hidStage.value : '',
      chosen_tale_number: hidTale ? hidTale.value : '',
      parent_name: val('parent_name'),
      parent_email: val('parent_email'),
      parent_telegram: val('parent_telegram'),
      child_name: val('child_name'),
      child_birth_date: val('child_birth_date'),
      child_age: ageFromBirthDate(val('child_birth_date')) || val('child_age'),
      promo_code: val('promo_code'),
      notification_channel: 'email'
    };
  }

  function redirectToPayPage(tariff) {
    var p = ORDER_PRODUCTS[tariff];
    if (!p || !PAY_PAGE_URL) {
      showPaymentNotReadyAlert();
      return;
    }
    var payload = collectCheckoutPayload(tariff);
    try {
      sessionStorage.setItem('chit_checkout', JSON.stringify(payload));
    } catch (e) {}
    var qs = new URLSearchParams();
    Object.keys(payload).forEach(function(key) {
      var v = payload[key];
      if (v !== undefined && v !== null && String(v).trim() !== '') qs.set(key, String(v));
    });
    var url = PAY_PAGE_URL;
    var query = qs.toString();
    if (query) url += (url.indexOf('?') >= 0 ? '&' : '?') + query;
    window.location.href = url;
  }

  function openCart(tariff) {
    if (!window.chitValidateProgram()) return;
    if (usesPayPageRedirect()) {
      redirectToPayPage(tariff);
      return;
    }
    orderConfigReady.finally(function() {
      syncToCartForm();
      waitTcartReady(function() {
        clearTcart();
        if (addProductDirect(tariff) && cartHasItems()) {
          openCartModal();
          return;
        }
        var hashes = buildOrderHashes(tariff);
        var hashIdx = 0;
        var hashWait = 0;

        function openWhenReady() {
          syncToCartForm();
          if (cartHasItems()) {
            openCartModal();
            return;
          }
          if (hashIdx < hashes.length) {
            triggerOrderHash(hashes[hashIdx]);
            hashWait += 1;
            if (hashWait >= 10 || cartHasItems()) {
              if (cartHasItems()) {
                openCartModal();
                return;
              }
              hashIdx += 1;
              hashWait = 0;
            }
            setTimeout(openWhenReady, 350);
            return;
          }
          alert('Не удалось добавить тариф. Проверьте Product ID в блоках ST205 и опубликуйте сайт.');
        }

        openWhenReady();
      });
    });
  }

  function syncToTildaForm() {
    syncToCartForm();
  }

  function syncHidden() {
    hidMid.value = (state.group && state.tariff && MODULES[state.group]) ? MODULES[state.group][state.tariff] : '';
    hidStage.value = state.stage || '';
    hidTale.value = state.tariff === 'single' && state.taleNum ? String(state.taleNum) : '';
    syncToTildaForm();
    syncToCartForm();
    if (!state.group || !state.tariff) {
      elSummary.classList.add('is-empty');
      elSummary.innerHTML = '<span class="summary-empty">Выберите класс и формат</span>';
      updatePayButton();
      return;
    }
    elSummary.classList.remove('is-empty');
    var html = '<strong>' + MODULES[state.group].label + '</strong> · ' + TARIFF_LABEL[state.tariff];
    if (state.tariff === 'single') {
      if (state.stage && state.taleNum) {
        html += '<br>' + stageLabelFor(state.stage) + ' · ' + TALES[state.group][state.stage][state.taleNum - 1];
        html += '<br>' + formatPrice(TARIFF_PRICE.single) + ' · урок на платформе';
        if (!isEarlyGroup()) {
          var meetLine = singleMeetingAddonLine(state.stage, state.taleNum);
          if (meetLine.available) {
            html += '<br>дополнительно можно докупить групповое занятие-квест с преподавателем: ' + meetLine.date + ' · ' + MEETING_ADDON_PRICE + ' ₽';
          }
        }
      } else if (state.stage) {
        html += '<br><span class="summary-empty">Выберите сказку</span>';
      } else {
        html += '<br><span class="summary-empty">Выберите блок и сказку</span>';
      }
    } else if (state.stage) {
      if (isEarlyGroup()) {
        html += '<br>' + stageLabelFor(state.stage);
        if (state.tariff === 'with_teacher') html += ' + живые встречи';
      } else {
        html += '<br>' + stageLabelFor(state.stage) + ' · 4 сказки';
        if (state.tariff === 'with_teacher') html += ' + 4 встречи';
      }
    } else {
      html += '<br><span class="summary-empty">' + (isEarlyGroup() ? 'Выберите модуль' : 'Выберите блок программы') + '</span>';
    }
    elSummary.innerHTML = html;
    updatePayButton();
    schedulePromoQuoteRefresh();
  }

  function renderTales() {
    elTales.innerHTML = '';
    elPreview.style.display = 'none';
    if (!state.group || !state.stage) return;
    var list = TALES[state.group] && TALES[state.group][state.stage];
    if (!list || !list.length) return;
    var early = usesLessonLabels(state.group);
    var unitCap = early ? 'Урок' : 'Сказка';
    var countLabel = isEarlyGroup() ? 'все 8 уроков' : (isCohortGroup() ? 'все 4 урока' : 'все 4 сказки');
    if (state.tariff === 'single') {
      elTales.style.display = 'grid';
      elTales.innerHTML = '<p class="tales-prompt">Нажмите на ' + (early ? 'урок' : 'сказку') + ', чтобы выбрать ' + (early ? 'его' : 'её') + ' для оплаты:</p>';
      list.forEach(function(title, i) {
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'tale-btn' + (state.taleNum === i + 1 ? ' is-active' : '');
        var sched = isCohortGroup() ? cohortScheduleHtml(i) : (isEarlyGroup() ? earlyScheduleHtml(i, state.tariff) : taleScheduleHtml(state.stage, i, state.tariff));
        btn.innerHTML =
          '<span class="tale-num">' + (i + 1) + '</span>' +
          '<span class="tale-btn__body">' +
            '<span class="tale-btn__title">' + title + '</span>' +
            sched +
          '</span>';
        btn.onclick = function() { state.taleNum = i + 1; renderTales(); syncHidden(); };
        elTales.appendChild(btn);
      });
      return;
    }
    elTales.style.display = 'none';
    elPreview.style.display = 'block';
    elPreview.innerHTML =
      '<div class="block-preview__banner">✓ В тариф уже входят ' + countLabel + ' — выбирать не нужно</div>' +
      '<div class="block-preview__title">Программа этого модуля' +
      (state.tariff === 'with_teacher' ? (early ? ' · встречи 3, 10, 17 и 24 сентября' : ' · встречи с преподавателем') : '') +
      '</div>' +
      '<div class="block-preview__cards">' +
      list.map(function(t, i) {
        var sched = isCohortGroup() ? cohortScheduleHtml(i) : (isEarlyGroup() ? earlyScheduleHtml(i, state.tariff) : taleScheduleHtml(state.stage, i, state.tariff));
        return '<div class="block-preview__card">' +
          '<div class="block-preview__num">' + unitCap + ' ' + (i + 1) + ' · входит</div>' +
          '<div class="block-preview__name">' + t + '</div>' +
          sched +
        '</div>';
      }).join('') +
      '</div>' +
      '<p class="block-preview__next">Дальше заполните контакты и нажмите «Записаться» ↓</p>';
  }

  function showDateBox() {
    elDateBox.classList.toggle('is-visible', !!state.tariff);
    var hint = document.getElementById('chit-step3-hint');
    if (hint) hint.hidden = state.tariff !== 'single';
    var guide = document.getElementById('chit-step3-guide');
    var onlyOneStage = state.tariff === 'with_teacher' && WITH_TEACHER_STAGE1_CLOSED && !isEarlyGroup() && !isCohortGroup();
    if (guide) {
      if (isEarlyGroup()) {
        guide.textContent = state.tariff === 'single'
          ? 'Нажмите на один урок в списке — его и оплатите.'
          : 'В тарифе уже все 8 уроков модуля — выбирать уроки не нужно.';
      } else if (isCohortGroup()) {
        guide.textContent = state.tariff === 'single'
          ? 'Нажмите на один урок в списке — его и оплатите.'
          : 'В тарифе уже все 4 урока модуля — выбирать уроки не нужно.';
      } else if (state.tariff === 'single') {
        guide.textContent = onlyOneStage
          ? 'Нажмите на одну сказку в списке — её и оплатите.'
          : 'Выберите блок, затем нажмите на одну сказку в списке — её и оплатите.';
      } else if (onlyOneStage) {
        // Одна дата уже выбрана — не просим «выберите дату старта»
        guide.textContent = 'Список ниже — программа блока: все 4 сказки уже входят в тариф, выбирать не нужно.';
      } else {
        guide.textContent = 'Выберите блок. Список ниже — все 4 сказки уже входят в тариф.';
      }
    }
    refreshStageAvailability();
    updateEarlyEnrollUi();
  }

  function updateEarlyEnrollUi() {
    var early = isEarlyGroup();
    var cohort = isCohortGroup();
    var root = document.getElementById('chit-main');
    if (root) {
      root.classList.toggle('is-early-course', early);
      root.classList.toggle('is-cohort-course', cohort);
    }
    var stage1 = document.querySelector('#chit-stages [data-stage="1"]');
    var stage2 = document.querySelector('#chit-stages [data-stage="2"]');
    if (stage1) {
      stage1.textContent = early ? 'Модуль 1 · 8 уроков' : (cohort ? 'Модуль · 4 урока' : 'Блок 1 · сказки 1–4');
    }
    if (stage2) {
      stage2.hidden = early || cohort;
      stage2.style.setProperty('display', (early || cohort) ? 'none' : '', 'important');
    }
    if ((early || cohort) && state.stage !== '1') {
      state.stage = '1';
      state.taleNum = state.tariff === 'single' ? (state.taleNum || 1) : 0;
      document.querySelectorAll('#chit-stages .pill').forEach(function(p) {
        p.classList.toggle('is-active', p.getAttribute('data-stage') === '1');
      });
    }
    var singleHint = document.querySelector('#chit-tariffs [data-tariff="single"] .pick-card__hint');
    if (singleHint) {
      singleHint.textContent = (early || cohort) ? '1 урок онлайн, без встречи' : '1 сказка онлайн, без встречи';
    }
    var selfHint = document.querySelector('#chit-tariffs [data-tariff="self_paced"] .pick-card__hint');
    if (selfHint) {
      selfHint.textContent = early ? '8 уроков · свой темп, без встреч' : (cohort ? '4 урока · свой темп, без встреч' : '4 сказки · 499 ₽ за сказку, без встреч');
    }
    var teachHint = document.querySelector('#chit-tariffs [data-tariff="with_teacher"] .pick-card__hint');
    if (teachHint) {
      teachHint.textContent = early ? '8 уроков + 4 встречи по чт: 3, 10, 17, 24 сен' : (cohort ? '4 урока + встречи с преподавателем' : '4 сказки + встречи по четвергам');
    }
    refreshTariffAvailability();
  }

  function refreshStageAvailability() {
    var stage1 = document.querySelector('#chit-stages [data-stage="1"]');
    var stage2 = document.querySelector('#chit-stages [data-stage="2"]');
    var note = document.getElementById('chit-stage1-closed-note');
    var root = document.getElementById('chit-main');
    var closed = state.tariff === 'with_teacher' && WITH_TEACHER_STAGE1_CLOSED && !isEarlyGroup() && !isCohortGroup();
    if (root) root.classList.toggle('is-with-teacher-stage1-closed', closed);
    if (stage1) {
      // Скрываем блок 1 для «С преподавателем» (не для early)
      stage1.hidden = closed;
      stage1.style.setProperty('display', closed ? 'none' : '', 'important');
      stage1.classList.toggle('is-disabled', closed);
      stage1.disabled = closed;
      stage1.setAttribute('aria-disabled', closed ? 'true' : 'false');
      stage1.title = closed ? 'Блок 1 с преподавателем сейчас недоступен' : '';
      if (closed) stage1.classList.remove('is-active');
    }
    if (note) note.hidden = !closed;
    if (closed && state.stage !== '2') {
      state.stage = '2';
      state.taleNum = 0;
      if (stage2) stage2.classList.add('is-active');
      document.querySelectorAll('#chit-stages .pill').forEach(function(p) {
        p.classList.toggle('is-active', p.getAttribute('data-stage') === '2');
      });
      renderTales();
      syncHidden();
    }
  }

  function onGroupClick(btn) {
    state.group = btn.getAttribute('data-group');
    // Дату старта не сбрасываем — иначе кнопка этапа остаётся «выбранной»,
    // а список сказок не рисуется (state.stage пустой).
    state.taleNum = 0;
    document.querySelectorAll('#chit-groups-basic .pill, #chit-groups-extra .pill, #chit-groups-early .pill, #chit-groups-cohort .pill').forEach(function(p) {
      p.classList.toggle('is-active', p === btn);
    });
    if (isEarlyGroup() || isCohortGroup()) {
      state.stage = '1';
    } else if (!state.stage) {
      state.stage = '2';
    }
    document.querySelectorAll('#chit-stages .pill').forEach(function(p) {
      p.classList.toggle('is-active', p.getAttribute('data-stage') === state.stage);
    });
    if (state.tariff === 'single' && state.stage) state.taleNum = 1;
    refreshTariffAvailability();
    refreshStageAvailability();
    showDateBox();
    renderTales();
    syncHidden();
  }
  document.getElementById('chit-groups-basic').onclick = function(e) { var b = e.target.closest('[data-group]'); if (b) onGroupClick(b); };
  document.getElementById('chit-groups-extra').onclick = function(e) { var b = e.target.closest('[data-group]'); if (b) onGroupClick(b); };
  var groupsEarly = document.getElementById('chit-groups-early');
  if (groupsEarly) {
    groupsEarly.onclick = function(e) { var b = e.target.closest('[data-group]'); if (b) onGroupClick(b); };
  }
  var groupsCohort = document.getElementById('chit-groups-cohort');
  if (groupsCohort) {
    groupsCohort.onclick = function(e) { var b = e.target.closest('[data-group]'); if (b) onGroupClick(b); };
  }
  document.getElementById('chit-tariffs').onclick = function(e) {
    var card = e.target.closest('[data-tariff]'); if (!card) return;
    state.tariff = card.getAttribute('data-tariff');
    if (state.tariff !== 'single') state.taleNum = 0;
    else if (state.stage && !state.taleNum) state.taleNum = 1;
    document.querySelectorAll('#chit-tariffs .pick-card').forEach(function(c) { c.classList.toggle('is-active', c === card); });
    // Сразу закрываем этап 1 для «С преподавателем», до отрисовки дат
    refreshStageAvailability();
    refreshTariffAvailability();
    showDateBox(); renderTales(); syncHidden();
  };
  document.getElementById('chit-stages').onclick = function(e) {
    var btn = e.target.closest('[data-stage]'); if (!btn || btn.disabled || btn.classList.contains('is-disabled') || btn.hidden) return;
    if (state.tariff === 'with_teacher' && WITH_TEACHER_STAGE1_CLOSED && !isEarlyGroup() && !isCohortGroup() && btn.getAttribute('data-stage') === '1') {
      alert('На тарифе «С преподавателем» блок 1 сейчас недоступен. Выберите блок 2.');
      return;
    }
    state.stage = btn.getAttribute('data-stage'); state.taleNum = 0;
    if (state.tariff === 'single') state.taleNum = 1;
    document.querySelectorAll('#chit-stages .pill').forEach(function(p) { p.classList.toggle('is-active', p === btn); });
    renderTales(); syncHidden();
  };

  if (payBtn) {
    payBtn.addEventListener('click', function() {
      openCart(state.tariff);
    });
  }

  var promoInput = document.querySelector('#chit-main [name="promo_code"]');
  if (promoInput) {
    promoInput.addEventListener('input', schedulePromoQuoteRefresh);
    promoInput.addEventListener('change', schedulePromoQuoteRefresh);
  }

  document.querySelectorAll('[data-tariff-jump]').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      var tariff = btn.getAttribute('data-tariff-jump');
      var card = document.querySelector('#chit-tariffs [data-tariff="' + tariff + '"]');
      if (card) card.click();
      var paid = document.getElementById('chit-enroll-paid') || document.getElementById('program');
      if (paid) paid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });

  (function initCatalogEnroll() {
    var root = document.getElementById('chit-main');
    var lockEl = document.getElementById('chit-enroll-course');
    var lockTitle = document.getElementById('chit-enroll-course-title');
    var lockMeta = document.getElementById('chit-enroll-course-meta');
    var changeBtn = document.getElementById('chit-enroll-change');
    var stepTariffLabel = document.getElementById('chit-step-tariff-label');
    var courseLocked = false;

    function setCourseLock(title, meta, locked) {
      courseLocked = !!locked;
      if (root) root.classList.toggle('is-course-locked', courseLocked);
      if (lockEl) lockEl.hidden = !courseLocked;
      if (lockTitle) lockTitle.textContent = title || '';
      if (lockMeta) {
        lockMeta.textContent = meta || '';
        lockMeta.hidden = !meta;
      }
      if (stepTariffLabel) {
        stepTariffLabel.innerHTML = courseLocked
          ? '<em>далее</em> · выберите тариф'
          : '<em>шаг 2</em> · выберите тариф';
      }
    }

    function applyCourseGroup(group) {
      if (!group) return;
      var gBtn = document.querySelector(
        '#chit-groups-basic [data-group="' + group + '"], #chit-groups-extra [data-group="' + group + '"], #chit-groups-early [data-group="' + group + '"], #chit-groups-cohort [data-group="' + group + '"]'
      );
      if (gBtn) onGroupClick(gBtn);
      else if (MODULES[group]) {
        state.group = group;
        if (isEarlyGroup(group) || isCohortGroup(group)) state.stage = '1';
        refreshTariffAvailability();
        refreshStageAvailability();
        showDateBox();
        renderTales();
        syncHidden();
      }
    }

    function applyDefaultTariff() {
      var tCard = document.querySelector('#chit-tariffs [data-tariff="self_paced"]');
      if (tCard) tCard.click();
      else {
        state.tariff = 'self_paced';
        refreshStageAvailability();
        showDateBox();
        renderTales();
        syncHidden();
      }
    }

    var fareModal = document.getElementById('fare-modal');
    var fareCourseEl = document.getElementById('fare-modal-course');
    var fareNoteEl = document.getElementById('fare-modal-note');
    var fareContinueBtn = document.getElementById('fare-modal-continue');
    var fareTrack = document.getElementById('fare-modal-track');
    var ctx = { group: '', enroll: 'lead', title: '', meta: '', tariff: 'self_paced' };

    function scrollToPaidEnroll() {
      var paid = document.getElementById('chit-enroll-paid') || document.getElementById('program');
      if (paid) paid.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    function refreshModalTariffs() {
      if (!fareTrack) return;
      var blocked = ctx.group && NO_WITH_TEACHER_GROUPS.indexOf(ctx.group) >= 0;
      fareTrack.querySelectorAll('[data-fare="with_teacher"]').forEach(function(card) {
        card.classList.toggle('is-disabled', blocked);
        card.disabled = blocked;
        card.setAttribute('aria-disabled', blocked ? 'true' : 'false');
      });
      if (blocked && ctx.tariff === 'with_teacher') setModalFare('self_paced');
    }

    function setModalFare(tariff) {
      ctx.tariff = tariff || 'self_paced';
      if (!fareTrack) return;
      fareTrack.querySelectorAll('.fare-card').forEach(function(card) {
        var on = card.getAttribute('data-fare') === ctx.tariff;
        card.classList.toggle('is-selected', on);
        card.setAttribute('aria-checked', on ? 'true' : 'false');
      });
    }

    function openFareModal(card) {
      if (!fareModal || !card) return;
      ctx.group = card.getAttribute('data-group') || '';
      ctx.enroll = card.getAttribute('data-enroll') || (ctx.group ? 'pay' : 'lead');
      ctx.title = card.getAttribute('data-course-title') || '';
      ctx.meta = card.getAttribute('data-course-meta') || '';
      setModalFare('self_paced');
      refreshModalTariffs();
      if (fareCourseEl) {
        fareCourseEl.textContent = ctx.title + (ctx.meta ? ' · ' + ctx.meta : '');
      }
      if (fareNoteEl) {
        fareNoteEl.textContent = ctx.enroll === 'pay'
          ? 'Выберите тариф — затем откроется короткая форма записи'
          : 'Для этой программы пока заявка — оплата откроется после старта набора';
      }
      if (fareContinueBtn) {
        fareContinueBtn.textContent = ctx.enroll === 'pay' ? 'Продолжить запись' : 'Оставить заявку';
      }
      fareModal.classList.add('is-open');
      fareModal.setAttribute('aria-hidden', 'false');
      document.body.classList.add('fare-modal-open');
    }

    function closeFareModal() {
      if (!fareModal) return;
      fareModal.classList.remove('is-open');
      fareModal.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('fare-modal-open');
    }

    function continueFromFareModal() {
      closeFareModal();
      if (ctx.enroll === 'pay' && ctx.group) {
        setCourseLock(ctx.title, ctx.meta, true);
        applyCourseGroup(ctx.group);
        var tCard = document.querySelector('#chit-tariffs [data-tariff="' + ctx.tariff + '"]');
        if (tCard) tCard.click();
        else {
          state.tariff = ctx.tariff;
          refreshTariffAvailability();
          refreshStageAvailability();
          showDateBox();
          renderTales();
          syncHidden();
        }
        scrollToPaidEnroll();
        return;
      }
      var fakeCard = document.createElement('div');
      fakeCard.setAttribute('data-course-title', ctx.title);
      fakeCard.setAttribute('data-course-meta', ctx.meta);
      fakeCard.setAttribute('data-group', ctx.group);
      startLeadFromCard(fakeCard, ctx.tariff);
    }

    function startLeadFromCard(card, tariff) {
      var title = card.getAttribute('data-course-title') || '';
      var meta = card.getAttribute('data-course-meta') || '';
      var group = card.getAttribute('data-group') || '';
      var trialSlug = card.getAttribute('data-trial-slug') || '';
      try {
        sessionStorage.setItem('chit_lead_course', JSON.stringify({
          title: title,
          meta: meta,
          tariff: tariff || 'self_paced',
          group: group,
          trialSlug: trialSlug
        }));
      } catch (err) {}
      var lead = document.getElementById('lead');
      if (lead) lead.scrollIntoView({ behavior: 'smooth', block: 'start' });
      var age = document.getElementById('lead_child_age');
      if (age && meta && !age.value) {
        var m = meta.match(/(\d+\s*[–-]\s*\d+\s*лет|\d+\s*класс)/i);
        if (m) age.placeholder = m[1];
      }
    }

    function startPayFromCard(card) {
      openFareModal(card);
    }

    function handleCourseCard(card) {
      if (!card) return;
      openFareModal(card);
    }

    document.addEventListener('click', function(e) {
      var detail = e.target.closest('[data-course-detail]');
      if (detail) return;

      if (e.target.closest('[data-fare-close]')) {
        e.preventDefault();
        closeFareModal();
        return;
      }

      var openBtn = e.target.closest('[data-open-tariffs]');
      var courseCard = e.target.closest('#course-catalog .course-card');
      if (openBtn || (courseCard && !e.target.closest('a') && !e.target.closest('[data-qz-open]'))) {
        if (openBtn) e.preventDefault();
        if (courseCard) {
          e.preventDefault();
          handleCourseCard(courseCard);
        }
        return;
      }
    });

    if (fareTrack) {
      fareTrack.addEventListener('click', function(e) {
        var fareCard = e.target.closest('[data-fare]');
        if (!fareCard || fareCard.disabled || fareCard.classList.contains('is-disabled')) return;
        setModalFare(fareCard.getAttribute('data-fare'));
      });
    }

    if (fareContinueBtn) {
      fareContinueBtn.addEventListener('click', continueFromFareModal);
    }

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && fareModal && fareModal.classList.contains('is-open')) closeFareModal();
    });

    function applyPendingEnrollGroup() {
      var preGroup = '';
      try { preGroup = sessionStorage.getItem('chit_enroll_group') || ''; } catch (e) {}
      if (!preGroup || !MODULES[preGroup]) return;
      try { sessionStorage.removeItem('chit_enroll_group'); } catch (e2) {}
      var card = document.querySelector('#course-catalog [data-group="' + preGroup + '"]');
      if (card) {
        setCourseLock(
          card.getAttribute('data-course-title') || MODULES[preGroup].label || '',
          card.getAttribute('data-course-meta') || '',
          true
        );
      }
      applyCourseGroup(preGroup);
      scrollToPaidEnroll();
    }

    try {
      if (window.location.hash === '#program' || window.location.hash === '#enroll') {
        applyPendingEnrollGroup();
      }
    } catch (e) {}

    window.addEventListener('hashchange', function() {
      if (window.location.hash === '#program' || window.location.hash === '#enroll') {
        applyPendingEnrollGroup();
      }
    });

    if (changeBtn) {
      changeBtn.addEventListener('click', function() {
        setCourseLock('', '', false);
        var programs = document.getElementById('programs');
        if (programs) programs.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    }
  })();

  document.addEventListener('DOMContentLoaded', function() {
    syncToCartForm();
  });

  function chitValidateCatalogPayment() {
    syncToCartForm();
    hideCatalogBlocks();
    if (isOnPayPage() && !isPaymentCatalogReady()) {
      showPaymentNotReadyAlert();
      return false;
    }
    return true;
  }

  document.addEventListener('click', function(e) {
    var cartBtn = e.target.closest('.t706 .t-submit, .t706 button[type="submit"], .t-store__submit-btn');
    if (cartBtn) {
      if (!window.chitValidateProgram() || !chitValidateCatalogPayment()) {
        e.preventDefault();
        e.stopPropagation();
        return;
      }
      syncToCartForm();
      pushCheckbox('legal_consent', true);
    }
  }, true);

  document.addEventListener('submit', function(e) {
    var form = e.target;
    if (!form || !form.closest) return;
    if (form.closest('.t706') || form.closest('.t-form') || form.closest('.t-store')) {
      if (!window.chitValidateProgram() || !chitValidateCatalogPayment()) {
        e.preventDefault();
        e.stopPropagation();
      } else {
        syncToCartForm();
        pushCheckbox('legal_consent', true);
      }
    }
  }, true);

  window.chitValidateProgram = function() {
    if (!hidMid.value) { alert('Выберите класс и формат.'); document.getElementById('program').scrollIntoView({behavior:'smooth'}); return false; }
    if (state.tariff === 'with_teacher' && WITH_TEACHER_STAGE1_CLOSED && !isEarlyGroup() && !isCohortGroup() && state.stage === '1') {
      alert('На тарифе «С преподавателем» блок 1 сейчас недоступен. Выберите блок 2.');
      elDateBox.classList.add('is-visible');
      return false;
    }
    if (state.tariff === 'single' && (!hidStage.value || !hidTale.value)) {
      alert(isEarlyGroup() || isCohortGroup() ? 'Выберите урок для оплаты.' : 'Выберите дату и сказку.');
      elDateBox.classList.add('is-visible');
      return false;
    }
    if (state.tariff !== 'single' && !hidStage.value) { alert('Выберите дату старта.'); elDateBox.classList.add('is-visible'); return false; }
    var parentName = document.querySelector('#chit-main [name="parent_name"]');
    var parentEmail = document.querySelector('#chit-main [name="parent_email"]');
    var childName = document.querySelector('#chit-main [name="child_name"]');
    var childBirth = document.querySelector('#chit-main [name="child_birth_date"]');
    if (parentName && !parentName.value.trim()) { alert('Укажите имя родителя.'); parentName.focus(); return false; }
    if (parentEmail && !parentEmail.value.trim()) { alert('Укажите email.'); parentEmail.focus(); return false; }
    if (childName && !childName.value.trim()) { alert('Укажите имя ребёнка.'); childName.focus(); return false; }
    if (childBirth && !childBirth.value.trim()) { alert('Укажите день рождения ребёнка.'); childBirth.focus(); return false; }
    if (!findSt100Root()) {
      if (usesPayPageRedirect()) {
        syncToTildaForm();
        syncToCartForm();
        return true;
      }
      alert('Блок оплаты ST100 не найден на странице. Добавьте его в Tilda под Zero Block (см. ST100_SETUP.md).');
      checkSt100Block();
      scrollToCheckout();
      return false;
    }
    syncToTildaForm();
    syncToCartForm();
    return true;
  };

  bindContactSync();
  bindCartCloseHandler();
  bindStoreScrollGuard();
  bindStoreClickBlock();
  hideCatalogBlocks();
  watchLazyBlocks();
  checkSt100Block();
  orderConfigReady.finally(checkSt100Block);
  checkCatalogBlock();
  watchCartModal();
  refreshStageAvailability();
  applyEnrollDefaults();

  function chitTrialAgeHint(age) {
    if (age === '4-6') return '5';
    if (age === '5-7') return '6';
    if (age === '6-8') return '7';
    if (age === '9-11') return '10';
    return '';
  }

  document.querySelectorAll('a[data-trial-slug], button[data-trial-slug], #chit-trial [data-trial-slug]').forEach(function(card) {
    card.addEventListener('click', function() {
      try {
        var age = card.getAttribute('data-trial-age') || '';
        sessionStorage.setItem('chit_trial', JSON.stringify({
          age: age,
          slug: card.getAttribute('data-trial-slug') || '',
          title: card.getAttribute('data-trial-title') || ''
        }));
        var hintAge = chitTrialAgeHint(age);
        if (hintAge) sessionStorage.setItem('chit_trial_age_hint', hintAge);
      } catch (err) {}
    });
  });

  [500, 1500, 3500].forEach(function(ms) {
    setTimeout(function() {
      hideCatalogBlocks();
      refreshStageAvailability();
    }, ms);
  });
  setTimeout(function() {
    hideCatalogBlocks();
    checkSt100Block();
    checkCatalogBlock();
    watchCartModal();
    refreshStageAvailability();
  }, 1500);
})();

(function initInteractive() {
  var HERO_QUOTES = [
    { q: '«Книги нужны, чтобы детям стало чуть менее одиноко — нашёлся кто-то, кто их понимает»', c: 'мы строим курс на этом же — понять героя, его чувства и поступки' },
    { q: '«Читать — значит мечтать чужими головами»', c: 'каждый урок — погружение в мир героя' },
    { q: '«Сказка — ложь, да в ней намёк…»', c: 'учимся находить смысл между строк' }
  ];
  var quoteIdx = 0;
  var quoteEl = document.getElementById('quote-hero');
  var quoteText = document.getElementById('quote-hero-text');
  var quoteCite = document.getElementById('quote-hero-cite');
  if (quoteEl && quoteText) {
    quoteEl.addEventListener('click', function() {
      quoteEl.classList.add('is-fading');
      setTimeout(function() {
        quoteIdx = (quoteIdx + 1) % HERO_QUOTES.length;
        quoteText.textContent = HERO_QUOTES[quoteIdx].q;
        if (quoteCite) quoteCite.textContent = HERO_QUOTES[quoteIdx].c;
        quoteEl.classList.remove('is-fading');
      }, 300);
    });
  }

  var BOOK_TEXTS = [
    '<strong style="color:var(--blue)">Разовое</strong> — одна сказка на платформе (<span class="hero-book-text__nb">799&nbsp;₽</span>)<span class="hero-book-text__line">Свой темп на платформе · живые встречи — дополнительно</span>',
    '<strong style="color:var(--blue)">12 программ</strong> · старт в любой день<span class="hero-book-text__line">Свой темп на платформе · живые встречи — дополнительно</span>',
    '<strong style="color:var(--blue)">Один блок</strong> программы<span class="hero-book-text__line">Свой темп на платформе · живые встречи — дополнительно</span>'
  ];
  var bookStack = document.querySelector('.book-stack');
  var bookText = document.getElementById('hero-book-text');
  var heroShowcase = document.getElementById('hero-books');
  if (bookStack && bookText) {
    bookStack.addEventListener('click', function(e) {
      var book = e.target.closest('.book');
      if (!book) return;
      var idx = parseInt(book.getAttribute('data-idx'), 10);
      bookStack.querySelectorAll('.book').forEach(function(b) { b.classList.remove('is-active'); });
      book.classList.add('is-active');
      if (heroShowcase) heroShowcase.classList.add('is-active');
      bookText.classList.add('is-fading');
      setTimeout(function() {
        bookText.innerHTML = BOOK_TEXTS[idx] || BOOK_TEXTS[1];
        bookText.classList.remove('is-fading');
      }, 200);
    });
  }

  document.addEventListener('click', function(e) {
    var card = e.target.closest('.tale-card');
    if (!card || e.target.closest('a')) return;
    var open = card.classList.contains('is-open');
    document.querySelectorAll('.tale-card.is-open').forEach(function(c) { c.classList.remove('is-open'); });
    if (!open) card.classList.add('is-open');
  });
  document.addEventListener('keydown', function(e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    var card = e.target.closest('.tale-card');
    if (!card) return;
    e.preventDefault();
    card.click();
  });

  var logo = document.getElementById('site-logo');
  if (logo) {
    logo.addEventListener('click', function() {
      logo.classList.remove('is-sparkle');
      requestAnimationFrame(function() {
        requestAnimationFrame(function() {
          logo.classList.add('is-sparkle');
        });
      });
    });
  }

  var revealEls = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05, rootMargin: '0px' });
    revealEls.forEach(function(el) { obs.observe(el); });
  } else {
    revealEls.forEach(function(el) { el.classList.add('is-visible'); });
  }
  setTimeout(function() {
    revealEls.forEach(function(el) { el.classList.add('is-visible'); });
  }, 1500);

  (function initFinalCtaScroll() {
    var section = document.getElementById('final-cta');
    if (!section) return;
    section.classList.add('is-active');
  })();

  (function initFeedbackTab() {
    var tab = document.getElementById('feedback-tab');
    var toggle = document.getElementById('feedback-tab-toggle');
    var panel = document.getElementById('feedback-tab-panel');
    if (!tab || !toggle || !panel) return;

    function setOpen(open) {
      tab.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      panel.setAttribute('aria-hidden', open ? 'false' : 'true');
    }

    toggle.addEventListener('click', function() {
      setOpen(!tab.classList.contains('is-open'));
    });

    document.addEventListener('click', function(e) {
      if (!tab.contains(e.target)) setOpen(false);
    });

    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') setOpen(false);
    });

    panel.querySelectorAll('a[href^="#"]').forEach(function(link) {
      link.addEventListener('click', function() {
        setOpen(false);
      });
    });
  })();

  (function initPlatformTabs() {
    var tabs = document.querySelectorAll('#platform-tabs .platform-tab');
    if (!tabs.length) return;
    tabs.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var panelId = btn.getAttribute('data-panel');
        tabs.forEach(function(t) {
          var on = t === btn;
          t.classList.toggle('is-active', on);
          t.setAttribute('aria-selected', on ? 'true' : 'false');
        });
        document.querySelectorAll('.platform-panel').forEach(function(panel) {
          var match = panel.id === 'platform-panel-' + panelId;
          panel.classList.toggle('is-active', match);
          if (match) panel.removeAttribute('hidden');
          else panel.setAttribute('hidden', '');
        });
      });
    });
  })();

  (function initCourseCovers() {
    var covers = [
      ['[data-group="early-letters"]', 'https://api.chitatelstvo.ru/assets/course-cover-letters.jpg?v=20260822g'],
      ['[data-group="early-stories"]', 'https://api.chitatelstvo.ru/assets/course-cover-stories.jpg?v=20260822g'],
      ['[data-group="grade-1"]', 'https://api.chitatelstvo.ru/assets/course-cover-grade-1.jpg'],
      ['[data-group="grade-2"]', 'https://api.chitatelstvo.ru/assets/course-cover-grade-2.jpg'],
      ['[data-group="grade-3"]', 'https://api.chitatelstvo.ru/assets/course-cover-grade-3.jpg'],
      ['[data-group="grade-4"]', 'https://api.chitatelstvo.ru/assets/course-cover-grade-4.jpg'],
      ['[data-group="extra-6-8"]', 'https://api.chitatelstvo.ru/assets/course-cover-extra-6-8.jpg'],
      ['[data-group="extra-9-11"]', 'https://api.chitatelstvo.ru/assets/course-cover-extra-9-11.jpg'],
      ['[data-group="wind"], [data-course-title="Ветер в ивах"]', 'https://api.chitatelstvo.ru/assets/course-cover-wind.jpg'],
      ['[data-group="garden"], [data-course-title="Таинственный сад"]', 'https://api.chitatelstvo.ru/assets/course-cover-garden.jpg'],
      ['[data-group="rus-6-9"], [data-course-title="Русские сказки"][data-course-meta="6–9 лет · старт 5 октября"]', 'https://api.chitatelstvo.ru/assets/course-cover-rus-6-9.jpg'],
      ['[data-group="rus-10-12"], [data-course-title="Русские сказки"][data-course-meta="10–12 лет · старт 5 октября"]', 'https://api.chitatelstvo.ru/assets/course-cover-rus-10-12.jpg']
    ];
    covers.forEach(function(item) {
      var media = null;
      item[0].split(',').some(function(sel) {
        media = document.querySelector('#course-catalog .course-card' + sel.trim() + ' .course-card__media');
        return !!media;
      });
      if (!media) return;
      media.style.backgroundImage = 'url("' + item[1] + '")';
      media.style.backgroundSize = 'cover';
      var earlyCover = item[0].indexOf('early-letters') >= 0 || item[0].indexOf('early-stories') >= 0;
      media.style.backgroundPosition = earlyCover ? 'center center' : 'center 45%';
      var img = media.querySelector('img');
      if (!img) {
        img = document.createElement('img');
        img.alt = '';
        img.width = 800;
        img.height = 500;
        img.loading = 'lazy';
        media.appendChild(img);
      }
      if (img.getAttribute('src') !== item[1]) img.src = item[1];
      img.style.objectPosition = earlyCover ? 'center center' : '';
    });
  })();

  (function initCourseFilters() {
    var filters = document.querySelectorAll('#course-filters .course-filter');
    var cards = document.querySelectorAll('#course-catalog .course-card');
    if (!filters.length || !cards.length) return;
    filters.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var kind = btn.getAttribute('data-filter') || 'all';
        filters.forEach(function(f) {
          var on = f === btn;
          f.classList.toggle('is-active', on);
          f.setAttribute('aria-pressed', on ? 'true' : 'false');
        });
        cards.forEach(function(card) {
          var cardKind = card.getAttribute('data-kind') || '';
          var show = kind === 'all' || cardKind === kind;
          card.classList.toggle('is-hidden', !show);
        });
      });
    });
  })();

  (function initLeadForm() {
    var form = document.getElementById('chit-lead-form');
    if (!form) return;
    var note = document.getElementById('chit-lead-note');
    var API_BASE = (window.CHIT_API_BASE || 'https://api.chitatelstvo.ru').replace(/\/$/, '');
    var LEAD_FORM_NAME = 'Консультация';

    function setLeadNote(text, ok) {
      if (!note) return;
      note.hidden = !text;
      note.textContent = text || '';
      if (ok) note.classList.add('is-ok');
      else note.classList.remove('is-ok');
    }

    function findLeadTildaForm() {
      var forms = document.querySelectorAll('form.js-form-proccess, form.t-form');
      var i;
      var formEl;
      var nameInp;
      var fname;
      var needle = LEAD_FORM_NAME.toLowerCase();
      for (i = 0; i < forms.length; i++) {
        formEl = forms[i];
        if (formEl.closest('.t706') || formEl.closest('.t-store') || formEl.id === 'chit-lead-form') continue;
        nameInp = formEl.querySelector('input[name="tildaspec-formname"]');
        fname = (nameInp && nameInp.value ? nameInp.value : '').trim();
        if (!fname) continue;
        var low = fname.toLowerCase();
        if (fname === LEAD_FORM_NAME || low === needle ||
            low.indexOf('консультац') >= 0 || low.indexOf('подобрать') >= 0 ||
            low.indexOf('lead') >= 0) {
          return formEl;
        }
      }
      return null;
    }

    function setTildaField(tildaForm, names, value) {
      names.forEach(function (name) {
        tildaForm.querySelectorAll('[name="' + name + '"]').forEach(function (el) {
          if (el.type === 'checkbox' || el.type === 'radio' || el.type === 'submit' || el.type === 'button') return;
          if (el.type === 'hidden' && (el.name === 'formservices[]' || /^tildaspec/.test(el.name))) return;
          el.value = value;
          try {
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
          } catch (err) {}
        });
      });
    }

    function submitLeadViaTilda(payload) {
      var tildaForm = findLeadTildaForm();
      if (!tildaForm) return Promise.reject(new Error('no-tilda-form'));

      setTildaField(tildaForm, ['Name', 'name', 'Input', 'parent_name'], payload.name);
      setTildaField(tildaForm, ['Email', 'email', 'parent_email', 'E-mail'], payload.email);
      setTildaField(tildaForm, ['Phone', 'phone', 'tel', 'Telegram', 'parent_phone'], payload.phone);
      setTildaField(tildaForm, ['Input_2', 'Input2', 'age', 'Age', 'child_age'], payload.age);
      var comment = payload.comment || '';
      setTildaField(tildaForm, [
        'Textarea', 'Comments', 'Comment', 'comment', 'Message', 'message', 'course', 'Course'
      ], comment);
      var areas = tildaForm.querySelectorAll('textarea');
      if (areas.length && comment) {
        areas[0].value = comment;
        try { areas[0].dispatchEvent(new Event('input', { bubbles: true })); } catch (err) {}
      }

      return new Promise(function (resolve, reject) {
        var done = false;
        var timer;
        function finish(ok, err) {
          if (done) return;
          done = true;
          clearTimeout(timer);
          tildaForm.removeEventListener('tildaform:aftersuccess', onOk);
          if (ok) resolve();
          else reject(err || new Error('tilda-fail'));
        }
        function onOk() { finish(true); }
        tildaForm.addEventListener('tildaform:aftersuccess', onOk);
        timer = setTimeout(function () {
          var success = tildaForm.querySelector('.js-successbox');
          var successVisible = success && success.offsetParent !== null &&
            window.getComputedStyle(success).display !== 'none';
          if (successVisible || tildaForm.classList.contains('js-send-form-success')) finish(true);
          else finish(false, new Error('tilda-timeout'));
        }, 8000);
        var btn = tildaForm.querySelector(
          'button[type="submit"], .t-submit, input[type="submit"], .t-btnflex_type_submit'
        );
        try {
          if (btn) btn.click();
          else if (typeof tildaForm.requestSubmit === 'function') tildaForm.requestSubmit();
          else tildaForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
        } catch (err) {
          finish(false, err);
        }
      });
    }

    form.addEventListener('submit', function(e) {
      e.preventDefault();
      var name = (form.querySelector('#lead_parent_name') || {}).value || '';
      var email = (form.querySelector('#lead_parent_email') || {}).value || '';
      var phone = (form.querySelector('#lead_parent_phone') || {}).value || '';
      var age = (form.querySelector('#lead_child_age') || {}).value || '';
      var childName = (form.querySelector('#lead_child_name') || {}).value || 'Ребёнок';
      var saved = null;
      try {
        saved = JSON.parse(sessionStorage.getItem('chit_lead_course') || 'null');
      } catch (err) {}
      var trialSlug = (saved && saved.trialSlug) || '';
      if (!trialSlug && saved && saved.group === 'early-letters') trialSlug = 'early-letters-trial-lesson-01';
      if (!trialSlug && saved && saved.group === 'early-stories') trialSlug = 'early-stories-trial-lesson-01';
      if (!trialSlug && saved && /Буквы оживают/i.test(saved.title || '')) trialSlug = 'early-letters-trial-lesson-01';
      if (!trialSlug && saved && /Первые истории/i.test(saved.title || '')) trialSlug = 'early-stories-trial-lesson-01';

      if (trialSlug) {
        var ageNum = parseInt(String(age).replace(/\D+/g, ''), 10);
        var payload = {
          parent_name: name,
          parent_email: email,
          phone: phone,
          child_name: childName,
          child_age: ageNum || null,
          trial_slug: trialSlug,
          trial_title: (saved && saved.title) || ''
        };
        fetch(API_BASE + '/api/early/trial', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
          .then(function(r) { return r.json().then(function(j) { return { ok: r.ok, j: j }; }); })
          .then(function(res) {
            if (note) {
              note.hidden = false;
              note.textContent = (res.j && res.j.message) || 'Заявка отправлена.';
              if (res.j && res.j.lesson_url) {
                note.innerHTML = (res.j.message || 'Пробный открыт.') +
                  ' <a href="' + res.j.lesson_url + '">Открыть урок</a>';
              }
            }
          })
          .catch(function() {
            if (note) {
              note.hidden = false;
              note.textContent = 'Не удалось отправить. Напишите на info@chitatelstvo.ru';
            }
          });
        return;
      }

      var courseLine = '';
      if (saved && saved.title) {
        courseLine = 'Программа: ' + saved.title +
          (saved.meta ? ' (' + saved.meta + ')' : '') +
          (saved.tariff ? '\nТариф: ' + saved.tariff : '') + '\n';
      }
      var comment =
        'Консультация / помощь с выбором курса\n' +
        courseLine +
        'Имя родителя: ' + name + '\n' +
        'Email: ' + email + '\n' +
        'Телефон: ' + phone + '\n' +
        'Возраст ребёнка: ' + age + '\n';

      setLeadNote('Отправляем…', false);
      submitLeadViaTilda({ name: name, email: email, phone: phone, age: age, comment: comment })
        .then(function () {
          setLeadNote('Спасибо! Заявка отправлена — ответим на email или телефон.', true);
          form.reset();
        })
        .catch(function () {
          var mailto =
            'mailto:info@chitatelstvo.ru' +
            '?subject=' + encodeURIComponent('Консультация · Читательство') +
            '&body=' + encodeURIComponent(comment);
          setLeadNote('Откроется письмо — или напишите на info@chitatelstvo.ru.', false);
          window.location.href = mailto;
        });
    });
  })();

  fixTildaLayout();
  window.addEventListener('resize', fixTildaLayout);
  window.addEventListener('load', fixTildaLayout);
})();
});
