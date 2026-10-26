from hashlib import sha1

from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext
from wagtail import hooks

from .models import BasePageNoImage

SESSION_KEY = 'correspondence_warnings_shown'


def describe(autorite) -> str:
    return (f'{autorite} ({autorite._meta.verbose_name}, '
            f'état « {autorite.etat.nom} »)')


def get_warnings(page) -> list[str]:
    warnings = []
    autorites = page.get_unpublished_autorites()
    if autorites:
        warnings.append(gettext(
            'Attention : cette page fait référence à des personnes ou des '
            'lieux non publiés : %(autorites)s. '
            'Publiez-les ou retirez-les de la page.'
        ) % {'autorites': ', '.join(map(describe, autorites))})
    liens = page.get_unpublished_links()
    if liens:
        warnings.append(gettext(
            'Attention : le texte de cette page contient des liens vers des '
            'fiches non publiées : %(autorites)s. '
            'Ces liens mènent à une page introuvable pour certains lecteurs.'
        ) % {'autorites': ', '.join(map(describe, liens))})
    return warnings


# The first click on Publish shows the warnings and publishes nothing. The
# same warnings on a second click mean the editor read them, so it publishes.
@hooks.register('before_publish_page')
def confirm_unpublished_autorites(request, page):
    if not isinstance(page, BasePageNoImage):
        return None
    warnings = get_warnings(page)
    shown = request.session.get(SESSION_KEY, {})
    key = str(page.pk)
    digest = sha1('\n'.join(warnings).encode()).hexdigest()
    if not warnings or shown.get(key) == digest:
        if key in shown:
            request.session[SESSION_KEY] = {
                k: v for k, v in shown.items() if k != key}
        return None
    request.session[SESSION_KEY] = {**shown, key: digest}
    for warning in warnings:
        messages.warning(request, warning)
    messages.warning(request, gettext(
        'La page n’a pas été publiée. Cliquez à nouveau sur « Publier » '
        'pour la publier malgré tout.'))
    return redirect('wagtailadmin_pages:edit', page.pk)
