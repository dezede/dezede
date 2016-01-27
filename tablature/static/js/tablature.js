function Pagination ($pagination, switchPageHandler) {
  this.$pagination = $pagination;
  this.switchPageHandler = switchPageHandler;
  this.current = 0;
  this.margin = 2;  // Number of page links
                    // around current page and ends.
}

Pagination.prototype.setNumPages = function (numPages) {
  var last = numPages - 1;
  if (last != this.last) {
    var toPage = 0;
    if (typeof this.last === 'undefined') {
      toPage = this.current;
    }
    this.last = last;
    this.switchToPage(toPage, true);
  }
};

Pagination.prototype.pageOutOfBounds = function (i) {
  return (i < 0) || (i > this.last);
};

Pagination.prototype.createPageLink = function (i, content) {
  if (typeof content === 'undefined') {
    content = i + 1;
  }
  var $item = $('<li><a href=#>' + content + '</a></li>');
  this.$pagination.append($item);
  if (this.pageOutOfBounds(i)) {
    $item.addClass('disabled');
  }
  var $link = $item.find('a');
  if (i == this.current) {
    $item.addClass('active');
    $link.append('<span class="sr-only">(current)</span>');
  }
  $link.click(function (e) {
    e.preventDefault();
    this.switchToPage(i);
  }.bind(this));
};

Pagination.prototype.createPageLinks = function () {
  var i;
  var minStart = 0;
  var maxStart = Math.min(this.margin, this.last);
  var maxEnd = this.last;
  var minEnd = Math.max(maxStart, maxEnd - this.margin);
  var minMid = Math.max(maxStart, this.current - this.margin);
  var maxMid = Math.min(minEnd, this.current + this.margin);

  this.createPageLink(this.current - 1,
                      '<i class="fa fa-angle-left"></i>');
  for (i = minStart; i < maxStart; i++) {
    this.createPageLink(i)
  }
  if (minMid > maxStart) {
    this.createPageLink(-1, '…');
  }
  for (i = minMid; i >= 0 && i <= maxMid; i++) {
    this.createPageLink(i);
  }
  if (maxMid < minEnd) {
    this.createPageLink(-1, '…');
  }
  for (i = minEnd+1; i <= maxEnd; i++) {
    this.createPageLink(i);
  }
  this.createPageLink(this.current + 1,
                      '<i class="fa fa-angle-right"></i>');
};

Pagination.prototype.switchToPage = function (i, force) {
  if (typeof force === 'undefined') {
    force = false;
  }
  if (((i != this.current) && !this.pageOutOfBounds(i)) || force) {
    this.current = i;
    this.update();
    this.switchPageHandler();
  }
};

Pagination.prototype.update = function () {
  this.$pagination.empty();
  this.createPageLinks();
};

function Table ($container, columns, columnsWidths, sortables, filters,
                resultsPerPage, resultsString, sortableString, filterString,
                clearFilterString) {
  this.$container = $container;
  this.$tableContainer = $container.find('.table-responsive');
  this.$table = this.$tableContainer.find('table');
  this.$head = this.$table.find('thead');
  this.$results = this.$table.find('tbody');
  this.$input = $container.find('input');
  this.$input.parents('form').submit(function (e) {
    e.preventDefault();
    this.update();
  }.bind(this));
  this.$count = $container.find('.count');
  this.$spinner = $container.find('.spinner');
  this.columns = columns;
  this.columnsWidths = columnsWidths;
  this.sortables = sortables;
  this.$sortablesArray = [];
  this.filters = filters;
  this.$filtersArray = [];
  this.resultsString = resultsString;
  this.sortableString = sortableString;
  this.filterString = filterString;
  this.clearFilterString = clearFilterString;
  this.orderings = [];
  this.sortIcons = {
    '-1': 'fa-sort-desc', '0': 'fa-sort', '1': 'fa-sort-asc'
  };
  this.filterChoices = [];
  this.createHeaders();
  this.count = 0;
  this.resultsPerPage = resultsPerPage;
  this.pagination = new Pagination(
    $container.find('.pagination'), this.update.bind(this));

  $(document).keydown(
    this.onKeyDown.bind(this)
  ).keyup(
    this.onKeyUp.bind(this)
  );

  $(window).resize(this.updateGrabbable.bind(this));
  this.pageX = 0;
  this.$results.mousedown(this.onGrab.bind(this));
  $(document).mousemove(this.onMove.bind(this));
  $(document).mouseup(this.onUnGrab.bind(this));

  this.setData();
  this.update();
}

Table.prototype.createSortable = function (column, $flex, i) {
  this.orderings.push(0);

  if (!this.sortables[i]) {
    this.$sortablesArray.push(null);
    return;
  }

  var $sortable = $('<div class="sortable"></div>')
    .attr({title: this.sortableString, tabindex: 0});
  this.$sortablesArray.push($sortable);
  $flex.append($sortable);

  var $icon = $('<i class="fa fa-sort"></i>');
  $sortable.append($icon);
  $sortable.click(function () {
    if (this.orderings[i] == 1) {
      this.orderings[i] = -1;
    } else {
      this.orderings[i] += 1;
    }
    this.update();
  }.bind(this));
};

Table.prototype.updateSortables = function () {
  this.$sortablesArray.forEach(function ($sortable, i) {
    if ($sortable === null) {
      return;
    }
    var $icon = $sortable.find('i');
    $icon.attr('class', 'fa');
    $sortable.toggleClass('active', this.orderings[i] != 0);
    $icon.addClass(this.sortIcons[this.orderings[i].toString()]);
  }.bind(this));
};

Table.prototype.createFilter = function ($flex, i) {
  if (this.filters[i].length == 0) {
    this.filterChoices.push(null);
    this.$filtersArray.push(null);
    return;
  }

  var $filter = $('<div class="filter dropdown"></div>');
  this.$filtersArray.push($filter);
  $flex.append($filter);
  var $filterButton = $('<span class="filter-button"></span>');
  $filter.append($filterButton);

  $filterButton
    .append($('<i class="fa fa-filter"></i>'))
    .attr({
      title: this.filterString,
      'data-toggle': 'dropdown', 'aria-haspopup': true, 'aria-expanded': false,
      tabindex: 0
    });

  var $menu = $('<ul class="dropdown-menu" role="menu"></ul>');
  if ((i+1) > (this.columns.length / 2)) {
    $menu.addClass('pull-right');
  }
  $filter.append($menu);
  var $clearFilter = $(
    '<li class="clear-filter">' +
    '<a href="#">' + this.clearFilterString + '</a>' +
    '</li>' +
    '<li class="divider" role="separator"></li>');
  $clearFilter.hide();
  $menu.append($clearFilter);
  $clearFilter.click(function (e) {
    e.preventDefault();
    $menu.find('li.active').click();
  });
  this.filters[i].forEach(function (data) {
    var value = data[0], verbose = data[1];
    var $choice = $('<li><a href="#">' + verbose + '</a></li>');
    $menu.append($choice);
    $choice.click(function (e) {
      e.preventDefault();
      if (this.filterChoices[i] == value) {
        this.filterChoices[i] = null;
      } else {
        this.filterChoices[i] = value;
      }
      this.update();
    }.bind(this))
  }.bind(this));
};

Table.prototype.updateFilters = function () {
  this.$filtersArray.forEach(function ($filter, i) {
    if ($filter === null) {
      return;
    }
    var $menu = $filter.find('.dropdown-menu');
    var $clearFilter = $filter.find('.clear-filter, .divider');
    $filter.removeClass('active');
    $clearFilter.hide();
    $menu.find('li.active').removeClass('active');
    $menu.find('li').not($clearFilter).each(function (nthChoice, choice) {
      if (this.filterChoices[i] == this.filters[i][nthChoice][0]) {
        $(choice).addClass('active');
        $clearFilter.show();
        $filter.addClass('active');
      }
    }.bind(this));
  }.bind(this));
};

Table.prototype.createHeaders = function () {
  var $tr = $('<tr></tr>');
  this.$head.append($tr);
  this.columns.forEach(function (column, i) {
    var $cell = $(
      '<th style="min-width: ' + this.columnsWidths[i] + ';"></th>');
    $tr.append($cell);
    var $flex = $('<div class="flex"></div>');
    $cell.append($flex);
    if (column != '') {
      $flex.append($('<div class="column-name">' + column + '</div>'));
    }

    this.createSortable(column, $flex, i);
    this.createFilter($flex, i);
  }.bind(this));
};

Table.prototype.getNumPages = function () {
  return Math.ceil(this.count / this.resultsPerPage);
};

Table.prototype.setCount = function (count) {
  this.count = count;
  this.pagination.setNumPages(this.getNumPages());
  this.$count.empty().html(this.count + ' ' + this.resultsString);
};

Table.prototype.setData = function () {
  document.location.hash.slice(1).split('&').forEach(function (kv) {
    var t = kv.split('=');
    var k = t[0], v = t[1];
    if (k == 'q') {
      this.$input.val(decodeURIComponent(v));
    } else if (k == 'orderings') {
      this.orderings = decodeURIComponent(v).split(',').map(
        function (s, _) { return parseInt(s); });
    } else if (k == 'choices') {
      this.filterChoices = decodeURIComponent(v).split(',').map(
        function (s, _) {
          if (s === '') {
            return null;
          }
          return decodeURIComponent(s);
        });
    } else if (k == 'page') {
      this.pagination.current = parseInt(decodeURIComponent(v));
    }
  }.bind(this));
};

Table.prototype.getData = function () {
  return {
    q: this.$input.val(),
    orderings: this.orderings.join(),
    choices: this.filterChoices.map(function (s, _) {
        if (s === null) {
          return '';
        }
        return encodeURIComponent(s);
      }).join(),
    page: this.pagination.current
  };
};

Table.prototype.updateLocationHash = function (queryData) {
  var queryString = '';
    for (var k in queryData) {
      if (queryData.hasOwnProperty(k)) {
        if(queryString != "") {
          queryString += "&";
        }
        queryString += k + '=' + encodeURIComponent(queryData[k]);
      }
    }
    document.location.hash = queryString;
};

Table.prototype.onKeyDown = function (e) {
  if (this.$input.is(':focus')) {
      return;
  }
  var boundKeys = [33, 34, 35, 36, 37, 39];
  if (boundKeys.indexOf(e.keyCode) != -1) {
    e.preventDefault();
  }
};

Table.prototype.onKeyUp = function (e) {
  if (this.$input.is(':focus')) {
    return;
  }
  var newPage = null;
  if (e.keyCode == 36) {  // Home key
    newPage = 0;
  } else if (e.keyCode == 37) {  // Left arrow key
    newPage = this.pagination.current - 1;
  } else if (e.keyCode == 39) {  // Right arrow key
    newPage = this.pagination.current + 1;
  } else if (e.keyCode == 33) {  // Page up key
    newPage = Math.max(this.pagination.current - 5, 0);
  } else if (e.keyCode == 34) {  // Page down key
    newPage = Math.min(this.pagination.current + 5, this.pagination.last);
  } else if (e.keyCode == 35) {  // End key
    newPage = this.pagination.last;
  }
  if (newPage !== null) {
    e.preventDefault();
    this.pagination.switchToPage(newPage);
  }
};

Table.prototype.updateGrabbable = function () {
  this.$results.toggleClass(
    'grabbable',
    this.$tableContainer.prop('scrollWidth') > this.$tableContainer.width());
};

Table.prototype.onGrab = function (e) {
  var isLeftClick = e.which == 1;
  if (isLeftClick && this.$results.hasClass('grabbable')) {
    this.$results.addClass('grabbing');
    this.pageX = e.pageX;
  }
};

Table.prototype.onMove = function (e) {
  if (!this.$results.hasClass('grabbing')) {
    return;
  }
  e.preventDefault();
  var $tableContainer = this.$table.parent();
  if (e.pageX != this.pageX) {
    $tableContainer.scrollLeft($tableContainer.scrollLeft()
                               + (this.pageX - e.pageX));
    this.pageX = e.pageX;
  }
};

Table.prototype.onUnGrab = function () {
  this.$results.removeClass('grabbing');
};

Table.prototype.update = function () {
  if (typeof this.currentAjax !== 'undefined') {
    this.currentAjax.abort();
  }
  this.$results.find('[data-original-title]').tooltip('destroy');
  this.updateSortables();
  this.updateFilters();
  this.$spinner.show();
  var queryData = this.getData();
  this.currentAjax = $.ajax({
    data: queryData
  }).done(function (data) {
    this.setCount(data['count']);
    this.$results.empty();
    data['results'].forEach(function (dataRow) {
      var $row = $('<tr></tr>');
      this.$results.append($row);
      dataRow.forEach(function (value) {
        $row.append('<td>' + value + '</td>');
      });
    }.bind(this));
    this.updateGrabbable();
    this.$container.find('[title]').tooltip(
      {container: 'body', trigger: 'hover'});
    this.updateLocationHash(queryData);
    this.$spinner.hide();
  }.bind(this));
};
