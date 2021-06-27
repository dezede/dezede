(function ($) {
  var $side = $('#sidebar');
  $side.affix({
    offset: {
      top: function() {
        var offset_top = $side.offset().top;
        var navbar_height = $('nav.navbar').outerHeight(true);
        return (this.top = (offset_top - navbar_height));
      },
      bottom: function() {
        return (this.bottom = $('#footer').outerHeight(true));
      }
    }
  });
})(jQuery);
