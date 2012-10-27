{# Gestion des tooltips #}
if($.cookie("tooltips_placement") == null) {
  $.cookie("tooltips_placement", "left", {path: '/'});
}
get_tooltips_options = function() {
  return {placement: $.cookie("tooltips_placement")};};


var tooltips = $('*[title], *[data-original-title]');
tooltips_disable = function() {
  $.cookie("tooltips_enabled", "false", {path: '/'});
  tooltips.tooltip('destroy');
};
tooltips_enable = function() {
  $.cookie("tooltips_enabled", "true", {path: '/'});
  tooltips.tooltip(get_tooltips_options());
};


var tooltips_enabled = $.cookie("tooltips_enabled");
tooltips_enable();
if(tooltips_enabled == "false") {
  tooltips_disable();
}


tooltips_reload = function() {tooltips_disable(); tooltips_enable();};
tooltips_placement = function(dir) {
  $.cookie("tooltips_placement", dir, {path: '/'});
  tooltips_reload();
};
{# Fin de la gestion des tooltips #}


{# Gestion des cadres d’alerte #}
$('.alert').alert();
{# Fin de la gestion des cadres d’alerte #}
