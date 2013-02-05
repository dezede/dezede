{% load url from future %}
{% load i18n %}

load_source_content = function(object, pk) {
  var inner = $($(object).attr('href') + ' .accordion-inner');
  inner.html('{% trans 'Chargement…' %}');
  $.ajax({
    url: '{% url 'source_content' %}',
    data: {pk: pk}
  }).done(function (data) {
    inner.html(data);
    $(object).removeAttr('onmouseover');
  });
};
