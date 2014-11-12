function Reader ($div) {
  this.$div = $div;
  this.$container = this.$div.find('.img-container');
  this.$img = this.$container.find('img');
  this.$zoom = this.$div.find('.zoom');
  this.$save = this.$div.find('.save');
  this.$print = this.$div.find('.print');
  this.$prev = this.$div.find('.prev');
  this.$next = this.$div.find('.next');

  this.current = 0;
  this.X = 0;
  this.Y = 0;
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

  this.changeImage(0);

  $(document).keydown(function (e) {
    if (!this.$div.is(':visible')) {
      return;
    }

    if (e.keyCode == 37) {
      this.previous(e);
    } else if (e.keyCode == 39) {
      this.next(e);
    }
  }.bind(this));
};

Reader.prototype.toggleZoom = function (e) {
  e.preventDefault();
  if (this.$container.hasClass('zoomed')) {
    this.unzoom();
  } else {
    this.zoom(e);
  }
};

Reader.prototype.zoom = function (e) {
  var previousWidth = this.$img.width(), previousHeight = this.$img.height();
  this.currentSize = 'medium';
  this.changeImage(0);
  this.$container.addClass('zoomed');
  this.$img.load(function () {
    this.$container.scrollLeft((e.offsetX * this.$img.width() / previousWidth)
                         - this.$container.width() / 2);
    this.$container.scrollTop((e.offsetY * this.$img.height() / previousHeight)
                        - this.$container.height() / 2);
  }.bind(this));
  this.$zoom.find('.fa').removeClass('fa-search-plus').addClass('fa-search-minus');
};

Reader.prototype.unzoom = function () {
  if (this.$img.hasClass('dragged')) {
    this.undrag();
    if (this.moving) {
      this.moving = false;
      return;
    }
  }
  this.$container.removeClass('zoomed')
  this.currentSize = 'small';
  this.changeImage(0);
  this.$zoom.find('.fa').removeClass('fa-search-minus').addClass('fa-search-plus');
};

Reader.prototype.save = function () {
  var images = this.$div.data('images'),
      src = images[this.current]['original'];
  this.$save.attr('href', src);
  this.$save.attr('download', src.replace(/^.*[\\\/]/, ''));
};

Reader.prototype.print = function (e) {
  e.preventDefault();
  var popup = window.open();
  popup.document.write(
    '<style>img { max-width: 100%; max-height: 100%; }</style>'
    + this.$img[0].outerHTML
  );
  popup.print();
  popup.close()
};

Reader.prototype.changeImage = function (inc) {
  var images = this.$div.data('images'), current = this.current;
  current += inc;
  if (current < 0 || current >= images.length ) {
    return;
  }
  this.$img.attr('src', images[current][this.currentSize]);
  this.current = current;
  if (current == 0) {
    this.$prev.addClass('invisible');
  } else {
    this.$prev.removeClass('invisible');
  }
  if (current == (images.length - 1)) {
    this.$next.addClass('invisible');
  } else {
    this.$next.removeClass('invisible');
  }
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
  if (this.$container.hasClass('zoomed')) {
    this.X = this.$container.scrollLeft() + e.pageX;
    this.Y = this.$container.scrollTop() + e.pageY;
    this.$img.addClass('dragged');
  }
};

Reader.prototype.undrag = function () {
  this.$img.removeClass('dragged');
};

Reader.prototype.move = function (e) {
  if (this.$img.hasClass('dragged')) {
    this.moving = true;
    this.$container.scrollLeft(parseInt(this.X) - e.pageX);
    this.$container.scrollTop(parseInt(this.Y) - e.pageY);
  }
};
