/* Citius sub-pages: copy buttons on code blocks. */
(function () {
  'use strict';

  // copy buttons
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pre = btn.parentElement.querySelector('pre');
      var text = pre ? pre.innerText : '';
      var done = function (ok) {
        btn.textContent = ok ? 'Copied' : 'Select and copy';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
      } else { done(false); }
    });
  });

})();
