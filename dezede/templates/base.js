{# Gestion des tooltips #}
function tooltips_delete($container) {
  if (typeof $container === 'undefined') {
    $container = $('body');
  }
  $container.find('[data-original-title]').tooltip('destroy');
}

function tooltips_create($container) {
  if (typeof $container === 'undefined') {
    $container = $('body');
  }
  $container.find('[title]').tooltip({container: $container});
}

function tooltips_reload($container) {
  tooltips_delete($container);
  tooltips_create($container);
}

tooltips_reload();
{# Fin de la gestion des tooltips #}


{# Tabs switch on page load #}
var url = document.location.toString();
if (url.match('#')) {
    $('.nav-tabs a[href="#' + url.split('#')[1] + '"]').tab('show');
}

$('.nav-tabs a').on('shown.bs.tab', function (e) {
    window.location.hash = e.target.hash;
});
{# End of tabs switch on page load#}


{# Gestion des boutons changeant d’état quand on clique dessus #}
$('*[data-loading-text]').click(function () {
  $(this).button('loading');
});
{# Fin de la gestion des boutons changeant d’état quand on clique dessus #}


{# Google Analytics #}
var _gaq = _gaq || [];
_gaq.push(['_setAccount', 'UA-37152824-1']);
_gaq.push(['_setDomainName', 'dezede.org']);
_gaq.push(['_trackPageview']);

(function() {
  var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
  ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
  var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
})();
{# Fin de Google Analytics #}

{# Gestion du changement de langue #}
$('.language-link').click(function (e) {
  e.preventDefault();
  var $form = $('#language-form');
  $form.find('input[name="language"]').val($(this).data('language'));
  $form.submit();
});
{# Fin de la gestion du changement de langue #}
