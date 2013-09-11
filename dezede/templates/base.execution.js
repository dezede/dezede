{# Gestion des tooltips #}
tooltips_reload();
{# Fin de la gestion des tooltips #}

{# Gestion des cadres d’alerte #}
$('.alert').alert();
{# Fin de la gestion des cadres d’alerte #}

$('*[data-loading-text]').click(function () {
  $(this).button('loading');
});
