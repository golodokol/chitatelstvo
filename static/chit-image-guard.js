/**
 * Запрет перетаскивания и сохранения картинок (ПКМ) на ученических страницах.
 * Не мешает drag-and-drop в заданиях ordering — там тащится .chit-order-card, не img.
 */
(function () {
  if (!document.body) return;
  var protectedPage = document.body.classList.contains('chit-student')
    || document.body.classList.contains('chit-course-page');
  if (!protectedPage) return;

  function protectImg(img) {
    if (!img || img.tagName !== 'IMG') return;
    img.setAttribute('draggable', 'false');
  }

  function protectAll(root) {
    var scope = root && root.querySelectorAll ? root : document;
    scope.querySelectorAll('img').forEach(protectImg);
  }

  document.addEventListener(
    'contextmenu',
    function (event) {
      if (event.target && event.target.tagName === 'IMG') event.preventDefault();
    },
    true
  );

  document.addEventListener(
    'dragstart',
    function (event) {
      if (event.target && event.target.tagName === 'IMG') event.preventDefault();
    },
    true
  );

  protectAll(document);

  if (typeof MutationObserver !== 'undefined') {
    new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        mutation.addedNodes.forEach(function (node) {
          if (node.nodeType !== 1) return;
          if (node.tagName === 'IMG') protectImg(node);
          else protectAll(node);
        });
      });
    }).observe(document.body, { childList: true, subtree: true });
  }
})();
