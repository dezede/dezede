# coding: utf-8

from __future__ import unicode_literals
import os
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver import PhantomJS, Firefox
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select


PATH = os.path.abspath(os.path.dirname(__file__))


class SeleniumTest(StaticLiveServerTestCase):
    cleans_up_after_itself = True
    fixtures = [
        os.path.join(PATH, 'fixtures/accounts.hierarchicuser.json'),
    ]

    def _pre_setup(self):
        self.screenshot_id = 0
        super(SeleniumTest, self)._pre_setup()

    @classmethod
    def setUpClass(cls):
        driver_name = os.environ.get('SELENIUM_DRIVER', 'PhantomJS')
        assert driver_name in ('Firefox', 'PhantomJS')
        if driver_name == 'Firefox':
            cls.selenium = Firefox()
        elif driver_name == 'PhantomJS':
            cls.selenium = PhantomJS()

        # La réponse du serveur et l'interprétation peuvent être lents.
        timeout = 60
        cls.selenium.implicitly_wait(timeout)
        cls.selenium.set_script_timeout(timeout)
        cls.selenium.set_page_load_timeout(timeout)

        cls.selenium.set_window_size(1366, 768)
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

    def switch(self, i=None):
        """
        Passe d'une fenêtre ou onglet à l'autre quand il n'y en a que deux.
        """
        other_window_handles = [h for h in self.selenium.window_handles
                                if h != self.current_window_handle]
        if i is None:
            self.assertEqual(len(other_window_handles), 1)
        self.current_window_handle = other_window_handles[i or 0]
        self.selenium.switch_to.window(self.current_window_handle)

    def get_screenshot_filename(self, i=None):
        return os.path.join(PATH, 'test%s.png' % (i or self.screenshot_id))

    def screenshot(self):
        """
        Prend une capture d'écran avec un nom de fichier autoincrémenté.
        """
        self.screenshot_id += 1
        # FIXME: Ceci est un workaround pour éviter que PhantomJS
        # redimensionne la fenêtre intempestivement.
        self.selenium.set_window_size(1366, 768)
        self.selenium.save_screenshot(self.get_screenshot_filename())

    def write_to_tinymce(self, field_name, content):
        """
        Écrit ``content`` dans le widget TinyMCE du champ de formulaire nommé
        ``field_name``.
        """
        self.selenium.switch_to.frame(self.get_by_id('id_%s_ifr' % field_name))
        self.get_by_id('tinymce').send_keys(content)
        self.selenium.switch_to.default_content()

    def click_tinymce_button(self, field_name, button_name):
        """
        Clique sur le bouton nommé ``button_name`` du widget TinyMCE du
        champ de formulaire nommé ``field_name``.
        """
        self.get_by_id('id_%s_%s' % (field_name, button_name)).click()

    def autocomplete(self, element, query, link_text):
        ActionChains(self.selenium).move_to_element(
            element.find_element_by_css_selector('input:first-of-type')
        ).click().send_keys(query + Keys.DOWN).perform()
        self.get_link(link_text).click()

    def save(self, input_name='_save'):
        try:
            self.get_by_name(input_name).click()
        except NoSuchElementException:
            self.screenshot()
            raise

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
        password_input.send_keys(password)
        self.get_by_css('input[value="Connexion"]').click()

    def setUp(self):
        self.current_window_handle = self.selenium.current_window_handle

        site = Site.objects.get_current()
        site.domain = self.live_server_url[7:]
        site.save()

        self.log_as_superuser()

    def testSimulation(self):
        # Décide d'ajouter une nouvelle source.
        self.selenium.get(self.abs_url(reverse('admin:index')))
        self.get_link('Sources').click()
        self.get_link('Ajouter source').click()

        # Remplit deux champs.
        self.get_by_name('titre').send_keys('L’épisodique')
        self.get_by_name('date').send_keys('1/1/1901')

        # Ajoute un nouveau type de source.
        self.get_by_id('add_id_type').click()
        with self.new_popup():
            self.get_by_name('nom').send_keys('annonce')

        # Teste la saisie dans TinyMCE ainsi que le bouton de petites capitales
        # fait maison.
        self.get_by_xpath('//*[text()="Transcription"]').click()
        self.write_to_tinymce(
            'transcription', 'Aujourd’hui, quelques œuvres du maître ')
        self.click_tinymce_button('transcription', 'smallcaps')
        self.write_to_tinymce('transcription', 'Vivaldi')
        self.click_tinymce_button('transcription', 'smallcaps')
        self.write_to_tinymce('transcription', '.')

        # Ajoute un événement et tous les objets lui étant lié.
        self.get_by_xpath('//*[text()="Événements liés"]').click()
        self.get_link('Ajouter un objet événement lié supplémentaire').click()
        self.get_by_css('.evenement .related-lookup').click()
        with self.new_popup():
            self.get_link('Ajouter événement').click()

            self.get_by_name('debut_date').send_keys('1/1/1901')

            # Créé le lieu de l'ancrage de début.
            self.get_by_css('.debut_lieu .related-lookup').click()
            with self.new_popup(add='lieu ou institution'):
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
                auteur = self.get_by_id('auteurs0')

                # Créé l'individu auteur de l'œuvre.
                auteur.find_element_by_css_selector(
                    '.individu .related-lookup').click()
                with self.new_popup(add='individu'):
                    self.get_by_name('nom').send_keys('Vivaldi')
                    self.get_by_name('prenoms').send_keys('Antonio')

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
                    'auteurs0')
                self.autocomplete(
                    auteur.find_element_by_css_selector('.grp-td.individu'),
                    'viv', 'Vivaldi (Antonio)')
                self.autocomplete(
                    auteur.find_element_by_css_selector('.grp-td.profession'),
                    'com', 'Compositeur')

            # Ajoute une distribution à cet élément de programme.
            programme2.find_element_by_css_selector(
                '.distribution .related-lookup').click()
            with self.new_popup(add='élément de distribution'):
                # Ajoute l'individu de cette distribution.
                self.get_by_css('.individu .related-lookup').click()
                with self.new_popup(add='individu'):
                    self.get_by_name('nom').send_keys('Désile')
                    select = Select(self.get_by_name('titre'))
                    select.select_by_visible_text('Mlle')

                # Ajoute la partie de cette distribution.
                self.get_by_css('.partie .related-lookup').click()
                with self.new_popup(add='rôle ou instrument'):
                    self.get_by_id('id_type_0').click()
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
                    self.get_by_css('.individu'),
                    'dés', 'Mademoiselle Désile')
                # Ajoute un autre individu de cette distribution.
                self.get_by_css('.individu .related-lookup').click()
                with self.new_popup(add='individu'):
                    self.get_by_name('nom').send_keys('Balensi')
                    self.get_by_xpath(
                        '//*[text()="Informations complémentaires"]').click()
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
        self.get_by_css('input[value="Oui, je suis sûr"]').click()
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
