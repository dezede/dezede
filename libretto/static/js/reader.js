function Reader ($div, images) {
  this.$div = $div;
  this.$container = this.$div.find('.img-container');
  this.$img = this.$container.find('img');
  this.$zoom = this.$div.find('.zoom');
  this.$save = this.$div.find('.save');
  this.$print = this.$div.find('.print');
  this.$prev = this.$div.find('.prev');
  this.$next = this.$div.find('.next');
  this.$spinner = this.$div.find('.spinner-container');
  this.$page = this.$div.find('input[name="page"]');

  this.images = images;
  this.current = 0;
  this.zoomed = false;
  this.dragged = false;
  this.zoomX = 0;
  this.zoomY = 0;
  this.currentSize = 'small';
  this.moving = false;

  this.$img.off().click(this.toggleZoom.bind(this)
  ).mousedown(this.drag.bind(this)
  ).mousemove(this.move.bind(this)
  ).mouseout(this.undrag.bind(this)
  ).focusout(this.undrag.bind(this));

  this.$zoom.off().click(this.toggleZoom.bind(this));
  this.$save.off().click(this.save.bind(this));
  this.$print.off().click(this.print.bind(this));

  this.$prev.off().click(this.previous.bind(this));
  this.$next.off().click(this.next.bind(this));
  $(document).keydown(this.keydown.bind(this));

  this.$page.change(function () {
    this.current = this.limitPage(this.$page.val() - 1);
    this.changeImage(0);
  }.bind(this));

  this.changeImage(0);

  this.$page.attr('max', this.images.length);
  this.$div.find('.count').text('/ ' + this.images.length);
}

Reader.prototype.toggleZoom = function (e) {
  e.preventDefault();
  if (this.zoomed) {
    this.unzoom();
  } else {
    this.zoom(e);
  }
};

Reader.prototype.zoom = function (e) {
  var previousWidth = this.$img.width(), previousHeight = this.$img.height();
  var offsetX = e.pageX - this.$img.offset()['left'];
  var offsetY = e.pageY - this.$img.offset()['top'];

  this.currentSize = 'medium';
  this.changeImage(0, function () {
    this.zoomed = true;
    this.$container.addClass('zoomed').scrollLeft(
      (offsetX * this.$img.width() / previousWidth)
      - this.$container.width() / 2).scrollTop(
      (offsetY * this.$img.height() / previousHeight)
      - this.$container.height() / 2);
    this.$zoom.find('.fa').removeClass('fa-search-plus').addClass('fa-search-minus');
  }.bind(this));
};

Reader.prototype.unzoom = function () {
  if (this.dragged) {
    this.undrag();
    if (this.moving) {
      this.moving = false;
      return;
    }
  }
  this.zoomed = false;
  this.$container.removeClass('zoomed');
  this.currentSize = 'small';
  this.$zoom.find('.fa').removeClass('fa-search-minus').addClass('fa-search-plus');
};

Reader.prototype.save = function () {
  var src = this.images[this.current]['original'];
  this.$save.attr('href', src).attr('download', src.replace(/^.*[\\\/]/, ''));
};

Reader.prototype.print = function (e) {
  e.preventDefault();
  var popup = window.open();
  popup.document.write(
    '<html><head>'
    + '<style>img { max-width: 100%; max-height: 100%; }</style>'
    + '</head><body>'
    + '<img src="' + this.images[this.current]['original'] + '"'
    + ' onload="window.print(); window.close();" /></body></html>'
  );
};

Reader.prototype.wait = function () {
  this.$spinner.removeClass('hidden');
};

Reader.prototype.unwait = function () {
  this.$spinner.addClass('hidden');
};

Reader.prototype.updateControls = function () {
  if (this.current == 0) {
    this.$prev.addClass('invisible');
  } else {
    this.$prev.removeClass('invisible');
  }
  if (this.current == (this.images.length - 1)) {
    this.$next.addClass('invisible');
  } else {
    this.$next.removeClass('invisible');
  }
  this.$page.val(this.current+1);
};

Reader.prototype.limitPage = function (i) {
  if (i < 0) {
    return 0;
  }
  if (i >= this.images.length) {
    return this.images.length - 1;
  }
  return i;
};

Reader.prototype.changeImage = function (inc, loadHandler) {
  var current = this.limitPage(this.current + inc);
  if (inc != 0 && current == this.current) {
    return;
  }
  this.current = current;

  var completeLoadHandler = function () {
    this.unwait();
    if (typeof loadHandler != 'undefined') {
      loadHandler();
    }
    this.$img.unbind('load');
  }.bind(this);

  this.wait();
  var src = this.images[current][this.currentSize];
  if (this.$img.attr('src') != src) {
    this.$img.attr('src', src).load(completeLoadHandler);
  } else {
    completeLoadHandler();
  }
  this.updateControls();
};

Reader.prototype.previous = function (e) {
  e.preventDefault();
  this.changeImage(-1);
};

Reader.prototype.next = function (e) {
  e.preventDefault();
  this.changeImage(1);
};

Reader.prototype.drag = function (e) {
  e.preventDefault();
  if (this.zoomed) {
    this.dragged = true;
    this.zoomX = this.$container.scrollLeft() + e.pageX;
    this.zoomY = this.$container.scrollTop() + e.pageY;
    this.$img.addClass('dragged');
  }
};

Reader.prototype.undrag = function () {
  this.dragged = false;
  this.$img.removeClass('dragged');
};

Reader.prototype.move = function (e) {
  if (this.dragged) {
    this.moving = true;
    this.$container.scrollLeft(
      this.zoomX - e.pageX).scrollTop(
      this.zoomY - e.pageY);
  }
};

Reader.prototype.keydown = function (e) {
  if (!this.$div.is(':visible')) {
    return;
  }

  if (e.keyCode == 37) {
    this.previous(e);
  } else if (e.keyCode == 39) {
    this.next(e);
  }
};
