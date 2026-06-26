// Free-text autocompletion for libretto Wagtail admin forms.
//
// Loaded globally on the Wagtail admin (insert_global_admin_js hook). For any
// <input data-autocomplete-url="..."> it fetches the top matches for what the
// user typed and fills the associated <datalist> so the browser shows them as
// native suggestions. Uses event delegation, so inputs added later (e.g. new
// inline rows) work without extra wiring. See AjaxAutocompleteInput in
// libretto/forms.py.
(function () {
  'use strict';

  var DEBOUNCE_MS = 200;
  var timers = new WeakMap();

  function updateDatalist(input) {
    var url = input.getAttribute('data-autocomplete-url');
    var listId = input.getAttribute('list');
    if (!url || !listId) {
      return;
    }
    var datalist = document.getElementById(listId);
    if (!datalist) {
      return;
    }
    var q = input.value.trim();
    if (!q) {
      datalist.innerHTML = '';
      return;
    }
    fetch(url + '&q=' + encodeURIComponent(q), {
      credentials: 'same-origin',
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(function (response) {
        return response.ok ? response.json() : { results: [] };
      })
      .then(function (data) {
        var results = (data && data.results) || [];
        var fragment = document.createDocumentFragment();
        results.forEach(function (value) {
          var option = document.createElement('option');
          option.value = value;
          fragment.appendChild(option);
        });
        datalist.innerHTML = '';
        datalist.appendChild(fragment);
      })
      .catch(function () {});
  }

  document.addEventListener('input', function (event) {
    var input = event.target;
    if (!input || !input.matches || !input.matches('[data-autocomplete-url]')) {
      return;
    }
    var existing = timers.get(input);
    if (existing) {
      clearTimeout(existing);
    }
    timers.set(input, setTimeout(function () {
      updateDatalist(input);
    }, DEBOUNCE_MS));
  });
})();
