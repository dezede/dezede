(function($) {
  var $widget = $('.date-range-widget');
  var $slider = $widget.find('.slider');
  var $start = $widget.find('.start');
  var $end = $widget.find('.end');
  var min_year = $widget.data('min-year');
  var max_year = $widget.data('max-year');

  var bounded_value = function(value, bound) {
    var new_val = Math.min(Math.max(min_year, value), max_year);
    var bound_value = $slider.slider('values', bound);
    if(bound == 0) {
      new_val = Math.max(new_val, bound_value);
    }
    if(bound == 1) {
      new_val = Math.min(new_val, bound_value);
    }
    return new_val;
  };

  $slider.slider({
    range: true,
    min: min_year,
    max: max_year,
    values: [$start.val(), $end.val()],
    slide: function(event, ui) {
      $start.val(ui.values[0]);
      $end.val(ui.values[1]);
    }
  });
  $start.change(function() {
    var new_val = bounded_value($(this).val(), 1);
    $slider.slider('values', 0, new_val);
    $(this).val(new_val);
  });
  $end.change(function() {
    var new_val = bounded_value($(this).val(), 0);
    $slider.slider('values', 1, new_val);
    $(this).val(new_val);
  });
})(jQuery);
