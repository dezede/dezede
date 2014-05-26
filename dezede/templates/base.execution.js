{# Gestion des tooltips #}
tooltips_reload();
{# Fin de la gestion des tooltips #}

{# Gestion des boutons changeant d’état quand on clique dessus #}
$('*[data-loading-text]').click(function () {
  $(this).button('loading');
});
{# Fin de la gestion des boutons changeant d’état quand on clique dessus #}
