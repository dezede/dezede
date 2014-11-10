function changeImage ($reader, inc) {
  var images = $reader.data('images');
  var current = $reader.data('current');
  if (typeof current == 'undefined') {
    current = -1;
  }
  current += inc;
  if (current < 0 || current >= images.length ) {
    return;
  }
  $reader.find('.reader img').attr('src', images[current]);
  $reader.data('current', current);
  if (current == 0) {
    $reader.find('.prev').addClass('disabled');
  } else {
    $reader.find('.prev').removeClass('disabled');
  }
  if (current == (images.length - 1)) {
    $reader.find('.next').addClass('disabled');
  } else {
    $reader.find('.next').removeClass('disabled');
  }
}

function createReader($reader) {
  $reader.find('.btn.zoom').off().click(function (e) {
    e.preventDefault();
    $reader.find('.reader').toggleClass('zoomed');
    $(this).find('.fa').toggleClass('fa-search-plus').toggleClass('fa-search-minus');
  });

  $reader.find('.prev').off().click(function (e) {
    e.preventDefault();
    changeImage($reader, -1);
  });
  $reader.find('.next').off().click(function (e) {
    e.preventDefault();
    changeImage($reader, 1);
  }).click();

  $reader.find('.reader img').off().dblclick(function () {
    $(this).parents('.reader-wrapper').find('.btn.zoom').click();
  }).mousedown(function (e) {
    e.preventDefault();
    var $div = $(this).parent();
    if ($div.hasClass('zoomed')) {
      $(this).data('X', $div.scrollLeft() + e.pageX);
      $(this).data('Y', $div.scrollTop() + e.pageY);
      $(this).addClass('dragged');
    }
  }).mouseup(function () {
    $(this).removeClass('dragged');
  }).mousemove(function (e) {
    if ($(this).hasClass('dragged')) {
      var $div = $(this).parent();
      $div.scrollLeft(parseInt($(this).data('X')) - e.pageX);
      $div.scrollTop(parseInt($(this).data('Y')) - e.pageY);
    }
  }).mouseout(function() {
    $(this).removeClass('dragged');
  }).focusout(function() {
    $(this).removeClass('dragged');
  });

  $(document).keydown(function (e) {
    if (!$reader.is(':visible')) {
      return;
    }

    if (e.keyCode == 37) {
      e.preventDefault();
      changeImage($reader, -1);
    } else if (e.keyCode == 39) {
      e.preventDefault();
      changeImage($reader, 1);
    }
  });
}
