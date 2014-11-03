{% load url from future %}
{% load i18n %}

function load_source_content(object, pk) {
  var inner = $($(object).attr('href') + ' .panel-body');
  inner.html('<div class="text-center">' +
             '<i class="fa fa-spinner fa-spin fa-5x"></i></div>');
  $.ajax({
    url: '{% url 'source_content' %}',
    data: {pk: pk}
  }).done(function (data) {
    inner.html(data);
    $(object).removeAttr('onclick');
    tooltip_reload();
  });
}
