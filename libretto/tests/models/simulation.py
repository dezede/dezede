# coding: utf-8

from __future__ import unicode_literals
import os
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait


PATH = os.path.abspath(os.path.dirname(__file__))


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
        cls.selenium = WebDriver()
        cls.selenium.set_window_size(1366, 768)
        cls.wait = WebDriverWait(cls.selenium, 10)
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
        self.selenium.find_element_by_xpath(
            '//*[text()="Utilisateurs et groupes"]').click()
        self.selenium.find_element_by_link_text('Sites').click()
        self.selenium.find_element_by_link_text('example.com').click()

        domain = self.selenium.find_element_by_name('domain')
        domain.clear()
        domain.send_keys(self.live_server_url[7:])

        name = self.selenium.find_element_by_name('name')
        name.clear()
        name.send_keys(self.live_server_url[7:])

        self.selenium.find_element_by_name('_save').click()

    def wait_until_ready(self):
        self.wait.until(lambda driver: WebDriver.execute_script(
            driver, 'return document.readyState;') == 'complete')

    def get_screenshot_filename(self, i=None):
        return os.path.join(PATH, 'test%s.png' % (i or self.screenshot_id))

    def screenshot(self):
        """
        Prend une capture d'écran avec un nom de fichier autoincrémenté.
        """
        self.screenshot_id += 1
        self.wait_until_ready()
        self.selenium.save_screenshot(self.get_screenshot_filename())

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

    def scroll_and_click(self, element):
        ActionChains(self.selenium).move_to_element(
            element).click_and_hold().release().perform()

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

    def save(self, input_name='_save'):
        self.selenium.find_element_by_name(input_name).click()

    def show_on_site(self):
        self.selenium.find_element_by_link_text('Voir sur le site').click()
        self.selenium.close()
        self.switch()

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
        self.selenium.find_element_by_link_text('Sources').click()
        self.selenium.find_element_by_link_text('Ajouter source').click()

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

        # Ajoute un événement et tous les objets lui étant lié.
        self.selenium.find_element_by_id('lookup_id_evenements').click()
        self.switch()
        self.selenium.find_element_by_link_text('Ajouter événement').click()
        self.selenium.find_element_by_id('lookup_id_ancrage_debut').click()
        self.switch(-1)
        # Créé son ancrage de début.
        self.selenium.find_element_by_link_text(
            'Ajouter ancrage spatio-temporel').click()
        self.selenium.find_element_by_name('date').send_keys('1/1/1901')
        self.selenium.find_element_by_id('lookup_id_lieu').click()
        self.switch(-1)
        # Créé le lieu de l'ancrage de début.
        self.selenium.find_element_by_link_text(
            'Ajouter lieu ou institution').click()
        self.save()
        self.selenium.find_element_by_name('nom').send_keys('Rouen')
        self.selenium.find_element_by_id('add_id_nature').click()
        self.switch(-1)
        # Créé le type du lieu de l'ancrage de début.
        self.selenium.find_element_by_name('nom').send_keys('ville')
        self.selenium.find_element_by_name('referent').click()
        self.save()
        self.switch(-1)
        select = Select(self.selenium.find_element_by_name('nature'))
        select.select_by_visible_text('ville')
        self.save()
        self.switch(-1)
        self.save()
        self.switch(-1)
        # Ajoute un élément de programme.
        self.selenium.find_element_by_link_text(
            'Ajouter un objet Élément De Programme supplémentaire').click()
        programme0 = self.selenium.find_element_by_id('programme0')
        programme0.find_element_by_class_name('grp-collapse-handler').click()
        programme0.find_element_by_css_selector(
            '.grp-cell.autre input').send_keys('Présentation du programme')
        # Ajoute un autre élément de programme.
        self.selenium.find_element_by_link_text(
            'Ajouter un objet Élément De Programme supplémentaire').click()
        programme1 = self.selenium.find_element_by_id('programme1')
        self.scroll_and_click(
            programme1.find_element_by_class_name('grp-collapse-handler'))
        programme1.find_element_by_css_selector(
            '.grp-cell.oeuvre .related-lookup').click()
        self.switch(-1)
        # Créé l'œuvre de l'élément de programme.
        self.selenium.find_element_by_link_text('Ajouter œuvre').click()
        self.selenium.find_element_by_name('prefixe_titre').send_keys('la')
        self.selenium.find_element_by_name('titre').send_keys(
            'senna festeggiante')
        self.selenium.find_element_by_link_text(
            'Ajouter un objet Auteur supplémentaire').click()
        auteur = self.selenium.find_element_by_id(
            'libretto-auteur-content_type-object_id0')
        auteur.find_element_by_css_selector(
            '.individu .related-lookup').click()
        self.switch(-1)
        # Créé l'individu auteur de l'œuvre.
        self.selenium.find_element_by_link_text('Ajouter individu').click()
        self.selenium.find_element_by_name('nom').send_keys('Vivaldi')
        select = Select(self.selenium.find_element_by_name('titre'))
        self.selenium.find_element_by_css_selector(
            '.grp-cell.prenoms .related-lookup').click()
        self.switch(-1)
        # Créé le prénom de l'individu.
        self.selenium.find_element_by_link_text('Ajouter prénom').click()
        self.selenium.find_element_by_name('prenom').send_keys('Antonio')
        self.save()
        self.switch(-1)
        select.select_by_visible_text('M.')
        self.save()
        self.switch(-1)
        auteur.find_element_by_css_selector(
            '.profession .related-lookup').click()
        self.switch(-1)
        # Créé la profession de l'auteur.
        self.selenium.find_element_by_link_text('Ajouter profession').click()
        self.selenium.find_element_by_name('nom').send_keys('compositeur')
        self.save()
        self.switch(-1)
        self.save()
        self.switch(-1)
        # Ajoute un troisième élément de programme.
        self.selenium.find_element_by_link_text(
            'Ajouter un objet Élément De Programme supplémentaire').click()
        programme2 = self.selenium.find_element_by_id('programme2')
        self.scroll_and_click(
            programme2.find_element_by_class_name('grp-collapse-handler'))
        programme2.find_element_by_css_selector(
            '.grp-cell.oeuvre .related-lookup').click()
        self.switch(-1)
        # Créé l'œuvre de l'élément de programme.
        self.selenium.find_element_by_link_text('Ajouter œuvre').click()
        self.selenium.find_element_by_name('prefixe_titre').send_keys('la')
        self.selenium.find_element_by_name('titre').send_keys(
            'Gloria e Himeneo')
        self.selenium.find_element_by_link_text(
            'Ajouter un objet Auteur supplémentaire').click()
        auteur = self.selenium.find_element_by_id(
            'libretto-auteur-content_type-object_id0')
        auteur.find_element_by_css_selector(
            '.individu input').send_keys('Viv')
        self.selenium.find_element_by_link_text('Vivaldi (Antonio)').click()
        auteur.find_element_by_css_selector(
            '.profession input').send_keys('com')
        self.selenium.find_element_by_link_text('Compositeur').click()
        self.save()
        self.switch(-1)
        self.save()
        self.switch(-1)

        # Enregistre.
        self.save('_continue')
        self.screenshot()

        # Regarde le résultat dans la partie visible.
        self.show_on_site()
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
        self.save()
        self.screenshot()

        # Vérifie si tout a été restauré correctement.
        self.show_on_site()
        self.screenshot()
        self.assertEqual(open(self.get_screenshot_filename(2), 'rb').read(),
                         open(self.get_screenshot_filename(4), 'rb').read())
        self.selenium.find_element_by_css_selector('.data-table a').click()
        self.screenshot()
