# coding: utf-8

from __future__ import unicode_literals
import os
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from selenium.webdriver import ActionChains
from selenium.webdriver import PhantomJS, Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


PATH = os.path.abspath(os.path.dirname(__file__))


# Ces réglages permettent étrangement d'être épargné d'un bug d'autant plus
# étrange : Firefox se déconnecte intempestivement quand le mode DEBUG est
# globalement False.  INTERNAL_IPS vide permet de désactiver la debug toolbar.
@override_settings(
    DEBUG=True, INTERNAL_IPS=(),
    CELERY_ALWAYS_EAGER=True, CELERY_EAGER_PROPAGATES_EXCEPTIONS=True)
class SeleniumTest(LiveServerTestCase):
    cleans_up_after_itself = True
    fixtures = [
        os.path.join(PATH, 'fixtures/accounts.hierarchicuser.json'),
    ]

    def _pre_setup(self):
        cache.clear()
        self.screenshot_id = 0
        super(SeleniumTest, self)._pre_setup()

    @classmethod
    def setUpClass(cls):
        try:
            cls.selenium = PhantomJS()
        except:
            cls.selenium = Firefox(timeout=60)
        cls.selenium.set_window_size(1366, 768)
        cls.wait = WebDriverWait(cls.selenium, 10)
        super(SeleniumTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTest, cls).tearDownClass()

    def abs_url(self, relative_url):
        return self.live_server_url + relative_url

    def get_link(self, link_text):
        return self.selenium.find_element_by_link_text(link_text)

    def get_by_name(self, name):
        return self.selenium.find_element_by_name(name)

    def get_by_id(self, id_):
        return self.selenium.find_element_by_id(id_)

    def get_by_css(self, css_selector):
        return self.selenium.find_element_by_css_selector(css_selector)

    def get_by_xpath(self, xpath):
        return self.selenium.find_element_by_xpath(xpath)

    def scroll_and_click(self, element):
        ActionChains(self.selenium).move_to_element(
            element).click_and_hold().release().perform()

    def wait_until_ready(self):
        self.wait.until(lambda driver: driver.execute_script(
            'return document.readyState;') == 'complete')

    def switch(self, i=None):
        """
        Passe d'une fenêtre ou onglet à l'autre quand il n'y en a que deux.
        """
        other_window_handles = [h for h in self.selenium.window_handles
                                if h != self.current_window_handle]
        if i is None:
            self.assertEqual(len(other_window_handles), 1)
        self.selenium.switch_to_window(other_window_handles[i or 0])
        self.current_window_handle = other_window_handles[i or 0]

    def get_screenshot_filename(self, i=None):
        return os.path.join(PATH, 'test%s.png' % (i or self.screenshot_id))

    def screenshot(self):
        """
        Prend une capture d'écran avec un nom de fichier autoincrémenté.
        """
        self.screenshot_id += 1
        self.wait_until_ready()
        self.selenium.save_screenshot(self.get_screenshot_filename())

    def write_to_tinymce(self, field_name, content):
        """
        Écrit ``content`` dans le widget TinyMCE du champ de formulaire nommé
        ``field_name``.
        """
        self.selenium.switch_to_frame(
            self.get_by_id('id_%s_ifr' % field_name))
        self.get_by_id('tinymce').send_keys(content)
        self.selenium.switch_to_default_content()

    def click_tinymce_button(self, field_name, button_name):
        """
        Clique sur le bouton nommé ``button_name`` du widget TinyMCE du
        champ de formulaire nommé ``field_name``.
        """
        self.get_by_id(
            'id_%s_%s' % (field_name, button_name)).click()

    def autocomplete(self, element, query, link_text):
        ActionChains(self.selenium).move_to_element(
            element.find_element_by_css_selector('input:first-child')
        ).click().send_keys(query + Keys.DOWN).perform()
        self.get_link(link_text).click()

    def save(self, input_name='_save'):
        self.get_by_name(input_name).click()

    def save_popup(self):
        self.save()
        self.switch(-1)

    def new_popup(self, add=None):
        parent_self = self

        class NewPopup(object):
            def __enter__(self):
                parent_self.switch(-1)
                if add is not None:
                    parent_self.get_link('Ajouter ' + add).click()

            def __exit__(self, exc_type, exc_val, exc_tb):
                parent_self.save_popup()

        return NewPopup()

    def show_on_site(self):
        self.get_link('Voir sur le site').click()
        self.selenium.close()
        self.switch()

    def log_as_superuser(self):
        """
        Se connecte automatiquement avec un compte superutilisateur.
        """
        username = 'name'
        password = 'password'

        self.selenium.get(self.abs_url(reverse('admin:index')))
        username_input = self.get_by_name('username')
        username_input.send_keys(username)
        password_input = self.get_by_name('password')
        password_input.send_keys(password + Keys.RETURN)

    def rewrite_site(self):
        """
        Réécrit l'objet Site préexistant pour qu'il contienne comme nom de
        domaine l'adresse du serveur de test.
        """
        self.get_by_xpath(
            '//*[text()="Utilisateurs et groupes"]').click()
        self.get_link('Sites').click()
        self.get_link('example.com').click()

        domain = self.get_by_name('domain')
        domain.clear()
        domain.send_keys(self.live_server_url[7:])

        name = self.get_by_name('name')
        name.clear()
        name.send_keys(self.live_server_url[7:])

        self.get_by_name('_save').click()

    def setUp(self):
        # La réponse du serveur et l'interprétation peuvent être lents.
        self.selenium.implicitly_wait(10)
        self.selenium.set_page_load_timeout(10)

        self.current_window_handle = self.selenium.current_window_handle

        self.log_as_superuser()
        self.rewrite_site()

    def testSimulation(self):
        # Décide d'ajouter une nouvelle source.
        self.selenium.get(self.abs_url(reverse('admin:index')))
        self.get_link('Sources').click()
        self.get_link('Ajouter source').click()

        # Remplit deux champs.
        self.get_by_name('nom').send_keys('L’épisodique')
        self.get_by_name('date').send_keys('1/1/1901')

        # Ajoute un nouveau type de source.
        self.get_by_id('add_id_type').click()
        with self.new_popup():
            self.get_by_name('nom').send_keys('annonce')

        # Teste la saisie dans TinyMCE ainsi que le bouton de petites capitales
        # fait maison.
        self.write_to_tinymce(
            'contenu', 'Aujourd’hui, quelques œuvres du maître ')
        self.click_tinymce_button('contenu', 'smallcaps')
        self.write_to_tinymce('contenu', 'Vivaldi')
        self.click_tinymce_button('contenu', 'smallcaps')
        self.write_to_tinymce('contenu', '.')

        # Ajoute un événement et tous les objets lui étant lié.
        self.get_by_css('.evenements .related-lookup').click()
        with self.new_popup():
            self.get_link('Ajouter événement').click()

            # Créé son ancrage de début.
            self.get_by_css('.ancrage_debut .related-lookup').click()
            with self.new_popup(add='ancrage spatio-temporel'):
                self.get_by_name('date').send_keys('1/1/1901')

                # Créé le lieu de l'ancrage de début.
                self.get_by_css('.lieu .related-lookup').click()
                with self.new_popup(add='lieu ou institution'):
                    self.save()  # Choisit "lieu" parmi les polymorphes.
                    self.get_by_name('nom').send_keys('Rouen')

                    # Créé la nature du lieu de l'ancrage de début.
                    self.get_by_css('.nature .add-another').click()
                    with self.new_popup():
                        self.get_by_name('nom').send_keys('ville')
                        self.get_by_name('referent').click()
                    select = Select(self.get_by_name('nature'))
                    select.select_by_visible_text('ville')

            # Ajoute un élément de programme.

            def open_new_element_de_programme(id, open=False, scroll=True):
                self.get_link('Ajouter un objet élément de programme '
                              'supplémentaire').click()
                programme = self.get_by_id('programme%s' % id)
                if open:
                    handler = programme.find_element_by_class_name(
                        'grp-collapse-handler')
                    if scroll:
                        self.scroll_and_click(handler)
                    else:
                        handler.click()
                return programme

            programme0 = open_new_element_de_programme(0, open=True,
                                                       scroll=False)
            programme0.find_element_by_css_selector(
                '.grp-cell.autre input').send_keys('Présentation du programme')

            # Ajoute un autre élément de programme.
            programme1 = open_new_element_de_programme(1)

            # Créé l'œuvre de l'élément de programme.
            programme1.find_element_by_css_selector(
                '.grp-cell.oeuvre .related-lookup').click()
            with self.new_popup(add='œuvre'):
                self.get_by_name('prefixe_titre').send_keys('la')
                self.get_by_name('titre').send_keys('senna festeggiante')
                self.get_link(
                    'Ajouter un objet auteur supplémentaire').click()
                auteur = self.get_by_id(
                    'libretto-auteur-content_type-object_id0')

                # Créé l'individu auteur de l'œuvre.
                auteur.find_element_by_css_selector(
                    '.individu .related-lookup').click()
                with self.new_popup(add='individu'):
                    self.get_by_name('nom').send_keys('Vivaldi')

                    # Créé le prénom de l'individu.
                    self.get_by_css(
                        '.grp-cell.prenoms .related-lookup').click()
                    with self.new_popup(add='prénom'):
                        self.get_by_name('prenom').send_keys('Antonio')

                    select = Select(self.get_by_name('titre'))
                    select.select_by_visible_text('M.')

                # Créé la profession de l'auteur.
                auteur.find_element_by_css_selector(
                    '.profession .related-lookup').click()
                with self.new_popup(add='profession'):
                    self.get_by_name('nom').send_keys('compositeur')

            # Ajoute un troisième élément de programme.
            programme2 = open_new_element_de_programme(2)

            # Créé l'œuvre de l'élément de programme.
            programme2.find_element_by_css_selector(
                '.grp-cell.oeuvre .related-lookup').click()
            with self.new_popup(add='œuvre'):
                self.get_by_name('prefixe_titre').send_keys('la')
                self.get_by_name('titre').send_keys('Gloria e Himeneo')
                self.get_link('Ajouter un objet auteur supplémentaire').click()
                auteur = self.get_by_id(
                    'libretto-auteur-content_type-object_id0')
                self.autocomplete(
                    auteur.find_element_by_css_selector('.individu'),
                    'viv', 'Vivaldi (Antonio)')
                self.autocomplete(
                    auteur.find_element_by_css_selector('.profession'),
                    'com', 'Compositeur')

            # Ajoute une distribution à cet élément de programme.
            programme2.find_element_by_css_selector(
                '.distribution .related-lookup').click()
            with self.new_popup(add='élément de distribution'):
                # Ajoute l'individu de cette distribution.
                self.get_by_css('.individus .related-lookup').click()
                with self.new_popup(add='individu'):
                    self.get_by_name('nom').send_keys('Désile')
                    select = Select(self.get_by_name('titre'))
                    select.select_by_visible_text('Mlle')

                # Ajoute le pupitre de cette distribution.
                self.get_by_css('.pupitre .related-lookup').click()
                with self.new_popup(add='pupitre'):
                    self.get_by_css('.partie .related-lookup').click()
                    with self.new_popup(add='rôle ou instrument'):
                        self.get_by_xpath(
                            '//label[text()=" instrument"]/input').click()
                        self.save()
                        self.get_by_name('nom').send_keys('violon')
                        self.get_by_css('.professions .related-lookup').click()
                        with self.new_popup(add='profession'):
                            self.get_by_name('nom').send_keys('violoniste')

            # Ajoute un quatrième élément de programme.
            programme3 = open_new_element_de_programme(3)

            # Ajoute une distribution à cet élément de programme.
            programme3.find_element_by_css_selector(
                '.distribution .related-lookup').click()
            with self.new_popup(add='élément de distribution'):
                self.autocomplete(
                    self.get_by_css('.individus'),
                    'dés', 'Mademoiselle Désile')
                # Ajoute un autre individu de cette distribution.
                self.get_by_css('.individus .related-lookup').click()
                with self.new_popup(add='individu'):
                    self.get_by_name('nom').send_keys('Balensi')
                    self.get_by_name('pseudonyme').send_keys('petite renarde')
                    select = Select(self.get_by_name('titre'))
                    select.select_by_visible_text('Mlle')

        # Enregistre.
        self.save('_continue')
        self.screenshot()

        # Regarde le résultat dans la partie visible.
        self.show_on_site()
        self.screenshot()

        # Supprime la source…
        self.get_by_css('.page-header '
                        'a[data-original-title="Supprimer"]').click()
        self.get_by_css('input[value="Oui, j\'en suis sûr."]').click()
        # … avant de finalement la restaurer avec django-reversion.
        self.get_link('Récupérer sources supprimés').click()
        self.get_by_css('#grp-change-history a').click()
        self.save()
        self.screenshot()

        # Vérifie si tout a été restauré correctement.
        self.show_on_site()
        self.screenshot()
        self.assertEqual(open(self.get_screenshot_filename(2), 'rb').read(),
                         open(self.get_screenshot_filename(4), 'rb').read())
        self.get_by_css('.data-table a').click()
        self.screenshot()
