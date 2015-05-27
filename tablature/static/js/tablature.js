function Pagination ($pagination, numPages, switchPageHandler) {
  this.initialisation = true;
  this.$pagination = $pagination;
  this.switchPageHandler = switchPageHandler;
  this.current = 0;
  this.margin = 2;  // Number of page links
                    // around current page and ends.
  this.setNumPages(numPages);
  $(document).keydown(function (e) {
    var boundKeys = [33, 34, 35, 36, 37, 39];
    if (boundKeys.indexOf(e.keyCode) != -1) {
      e.preventDefault();
    }
  }).keyup(function (e) {
    var newPage = null;
    if (e.keyCode == 36) {  // Home key
      newPage = 0;
    } else if (e.keyCode == 37) {  // Left arrow key
      newPage = this.current - 1;
    } else if (e.keyCode == 39) {  // Right arrow key
      newPage = this.current + 1;
    } else if (e.keyCode == 33) {  // Page up key
      newPage = Math.max(this.current - 5, 0);
    } else if (e.keyCode == 34) {  // Page down key
      newPage = Math.min(this.current + 5, this.last);
    } else if (e.keyCode == 35) {  // End key
      newPage = this.last;
    }
    if (newPage !== null) {
      e.preventDefault();
      this.switchToPage(newPage);
    }
  }.bind(this));
  this.initialisation = false;
}

Pagination.prototype.setNumPages = function (numPages) {
  var last = numPages - 1;
  if (last != this.last) {
    this.last = last;
    this.switchToPage(0, true);
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
    if (!this.initialisation) {
      this.switchPageHandler();
    }
  }
};

Pagination.prototype.update = function () {
  this.$pagination.empty();
  this.createPageLinks();
};

function Table ($container, columns, sortables, filters,
                resultsPerPage, resultsString) {
  this.$container = $container;
  this.$table = $container.find('table');
  this.$head = this.$table.find('thead');
  this.$results = this.$table.find('tbody');
  this.$input = $container.find('input');
  this.$input.parents('form').submit(function (e) {
    e.preventDefault();
    this.update();
  }.bind(this));
  this.$count = $('#count');
  this.columns = columns;
  this.sortables = sortables;
  this.filters = filters;
  this.resultsString = resultsString;
  this.orderings = [];
  this.sortIcons = {
    '-1': 'fa-sort-desc', '0': 'fa-sort', '1': 'fa-sort-asc'
  };
  this.filterChoices = [];
  this.createHeaders();
  this.count = 0;
  this.resultsPerPage = resultsPerPage;
  this.pagination = new Pagination(
    $container.find('.pagination'),
    this.getNumPages(),
    this.update.bind(this));
  this.update();
}

Table.prototype.createSortable = function (column, $cell, i) {
  this.orderings.push(0);
  var columnName = '<span class="column-name">' + column + '</span>';

  if (!this.sortables[i]) {
    $cell.append($('<div class="unsortable">' + columnName + '</div>'));
    return;
  }

  var $sortable = $('<div class="sortable" tabindex="0">'
                    + columnName + '</div>');
  $cell.append($sortable);
  var $icon = $('<i class="fa fa-sort"></i>');
  $sortable.append($icon);
  $sortable.click(function () {
    $icon.removeClass(this.sortIcons[this.orderings[i].toString()]);
    if (this.orderings[i] == 1) {
      this.orderings[i] = -1;
    } else {
      this.orderings[i] += 1;
    }
    $icon.addClass(this.sortIcons[this.orderings[i].toString()]);
    this.update();
  }.bind(this));
};

Table.prototype.createFilter = function ($cell, i) {
  if (this.filters[i].length == 0) {
    this.filterChoices.push(null);
    return;
  }

  var $filter = $(
    '<span class="filter dropdown">' +
    '  <span class="filter-button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" tabindex="0">' +
    '    <i class="fa fa-filter"></i>' +
    '  </span>' +
    '  <ul class="dropdown-menu pull-right" role="menu" aria-labelledby="dLabel">' +
    '  </ul>' +
    '</span>');
  var $filterList = $filter.find('ul');
  this.filters[i].forEach(function (data) {
    var value = data[0], verbose = data[1];
    var $choice = $('<li><a href="#">' + verbose + '</a></li>');
    $filterList.append($choice);
    $choice.click(function (e) {
      e.preventDefault();
      $filterList.find('li').removeClass('active');
      if (this.filterChoices[i] == value) {
        this.filterChoices[i] = null;
        $filter.removeClass('active');
      } else {
        $choice.addClass('active');
        $filter.addClass('active');
        this.filterChoices[i] = value;
      }
      this.update();
    }.bind(this))
  }.bind(this));
  $cell.append($filter);
};

Table.prototype.createHeaders = function () {
  var $tr = $('<tr></tr>');
  this.$head.append($tr);
  this.columns.forEach(function (column, i) {
    var $cell = $('<th></th>');
    $tr.append($cell);

    this.createSortable(column, $cell, i);
    this.createFilter($cell, i);
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

Table.prototype.getData = function () {
  return {
    q: this.$input.val(),
    orderings: this.orderings.join(),
    choices: this.filterChoices.join(),
    page: this.pagination.current
  };
};

Table.prototype.update = function () {
  if (typeof this.currentAjax !== 'undefined') {
    this.currentAjax.abort();
  }
  this.currentAjax = $.ajax({
    data: this.getData()
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
  }.bind(this));
};
