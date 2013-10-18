{% load url from future %}
{% load i18n %}

function load_source_content(object, pk) {
  var inner = $($(object).attr('href') + ' .panel-body');
  inner.html('{% trans 'Chargement…' %}');
  $.ajax({
    url: '{% url 'source_content' %}',
    data: {pk: pk}
  }).done(function (data) {
    inner.html(data);
    $(object).removeAttr('onmouseover');
  });
}
