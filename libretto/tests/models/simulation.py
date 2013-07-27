# coding: utf-8

from __future__ import unicode_literals
import os
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
import johnny.cache
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Firefox


PATH = os.path.abspath(os.path.dirname(__file__))


class SeleniumTest(LiveServerTestCase):
    fixtures = [
        os.path.join(PATH, 'fixtures/accounts.hierarchicuser.json'),
    ]

    def _pre_setup(self):
        johnny.cache.disable()
        self.screenshot_id = 0
        super(SeleniumTest, self)._pre_setup()

    @classmethod
    def setUpClass(cls):
        cls.selenium = Firefox()
        cls.selenium.set_window_size(1366, 768)
        super(SeleniumTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTest, cls).tearDownClass()

    def abs_url(self, relative_url):
        return self.live_server_url + relative_url

    def log_as_superuser(self):
        """
        Se connecte automatiquement avec un compte superutilisateur.
        """
        username = 'name'
        password = 'password'

        self.selenium.get(self.abs_url(reverse('admin:index')))
        username_input = self.selenium.find_element_by_name('username')
        username_input.send_keys(username)
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys(password + Keys.RETURN)

    def rewrite_site(self):
        """
        Réécrit l'objet Site préexistant pour qu'il contienne comme nom de
        domaine l'adresse du serveur de test.
        """
        self.selenium.get(self.abs_url(reverse('admin:index')))
        # self.selenium.find_element_by_css_selector(
        #     '#module_5 .module_title').click()
        self.selenium.find_element_by_xpath(
            '//*[contains(text(),"Utilisateurs et groupes")]').click()
        self.selenium.find_element_by_link_text('Sites').click()
        self.selenium.find_element_by_link_text('example.com').click()

        domain = self.selenium.find_element_by_name('domain')
        domain.clear()
        domain.send_keys(self.live_server_url[7:])

        name = self.selenium.find_element_by_name('name')
        name.clear()
        name.send_keys(self.live_server_url[7:])

        self.selenium.find_element_by_name('_save').click()

    def screenshot(self):
        """
        Prend une capture d'écran avec un nom de fichier autoincrémenté.
        """
        self.screenshot_id += 1
        self.selenium.save_screenshot(
            'screenshots/test%s.png' % self.screenshot_id)

    def switch(self):
        """
        Passe d'une fenêtre ou onglet à l'autre quand il n'y en a que deux.
        """
        other_window_handles = [h for h in self.selenium.window_handles
                                if h != self.current_window_handle]
        self.assertEqual(len(other_window_handles), 1)
        self.selenium.switch_to_window(other_window_handles[0])
        self.current_window_handle = other_window_handles[0]

    def write_to_tinymce(self, field_name, content):
        """
        Écrit ``content`` dans le widget TinyMCE du champ de formulaire nommé
        ``field_name``.
        """
        self.selenium.switch_to_frame(
            self.selenium.find_element_by_id('id_%s_ifr' % field_name))
        self.selenium.find_element_by_id('tinymce').send_keys(content)
        self.selenium.switch_to_default_content()

    def click_tinymce_button(self, field_name, button_name):
        """
        Clique sur le bouton nommé ``button_name`` du widget TinyMCE du
        champ de formulaire nommé ``field_name``.
        """
        self.selenium.find_element_by_id(
            'id_%s_%s' % (field_name, button_name)).click()

    def setUp(self):
        # Ce paramètre résoud étrangement plein de problèmes de Firefox…
        self.selenium.implicitly_wait(1)

        self.current_window_handle = self.selenium.current_window_handle
        self.log_as_superuser()
        self.rewrite_site()

    def testSimulation(self):
        # Décide d'ajouter une nouvelle source.
        self.selenium.get(self.abs_url(reverse('admin:index')))
        self.selenium.find_element_by_link_text('Sources').click()
        self.selenium.find_element_by_link_text('Ajouter source').click()
        self.screenshot()

        # Remplit deux champs.
        self.selenium.find_element_by_name('nom').send_keys('L’épisodique')
        self.selenium.find_element_by_name('date').send_keys('1/1/1901')

        # Ajoute un nouveau type de source.
        self.selenium.find_element_by_id('add_id_type').click()
        self.switch()
        self.selenium.find_element_by_name(
            'nom').send_keys('annonce' + Keys.RETURN)
        self.switch()

        # Teste la saisie dans TinyMCE ainsi que le bouton de petites capitales
        # fait maison.
        self.write_to_tinymce(
            'contenu', 'Aujourd’hui, quelques œuvres du maître ')
        self.click_tinymce_button('contenu', 'smallcaps')
        self.write_to_tinymce('contenu', 'Vivaldi')
        self.click_tinymce_button('contenu', 'smallcaps')
        self.write_to_tinymce('contenu', '.')

        # Enregistre.
        self.selenium.find_element_by_name('_continue').click()
        self.screenshot()

        # Regarde le résultat dans la partie visible.
        self.selenium.find_element_by_link_text('Voir sur le site').click()
        self.switch()
        self.screenshot()

        # Supprime la source…
        self.selenium.find_element_by_link_text('Supprimer').click()
        self.selenium.find_element_by_css_selector(
            'input[value="Oui, j\'en suis sûr."]').click()
        # … avant de finalement la restaurer avec django-reversion.
        self.selenium.find_element_by_link_text(
            'Récupérer sources supprimés').click()
        self.selenium.find_element_by_css_selector(
            '#grp-change-history a').click()
        self.selenium.find_element_by_name('_save').click()
        self.screenshot()
