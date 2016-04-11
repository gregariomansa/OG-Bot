﻿import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
from scraper import *

from enum import Enum

DEFENSES_DATA = {
    
        
        "rl" : DefenseItem(401, "Rocket Launcher"),
        "ll" : DefenseItem(402, "Light Laser"),
        "hl" : DefenseItem(403, "Heavy Laser"),
        "gc" : DefenseItem(404, "Gauss Cannon"),
        "ic" : DefenseItem(405, "Ion Cannon"),
        "pt" : DefenseItem(406, "Plasma Turret"),
        "ssd" : DefenseItem(407, "Small Shield Dome"),
        "lsd" : DefenseItem(408, "Large Shield Dome"),
        "im" : DefenseItem(502, "Interplanetary Missile"),
        "abm" : DefenseItem(503, "Anti-Ballistic Missile"),
        
        "401" : DefenseItem(401, "Rocket Launcher"),
        "402" : DefenseItem(402, "Light Laser"),
        "403" : DefenseItem(403, "Heavy Laser"),
        "404" : DefenseItem(404, "Gauss Cannon"),
        "405" : DefenseItem(405, "Ion Cannon"),
        "406" : DefenseItem(406, "Plasma Turret"),
        "407" : DefenseItem(407, "Small Shield Dome"),
        "408" : DefenseItem(408, "Large Shield Dome"),
        "502" : DefenseItem(502, "Interplanetary Missile"),
        "503" : DefenseItem(503, "Anti-Ballistic Missile")
        
    }

class Defenses(Enum):
    RocketLauncher = "rl"
    LightLaser = "ll"
    HeavyLaser = "hl"
    GaussCannon = "gc"
    IonCannon = "ic"
    PlasmaTurrent = "pt"

class Defense(Scraper):
    def get_defenses(self, planet = None):
        """
        Get defenses for the given planet
        """
        self.logger.info('Getting defense data')
        url = self.url_provider.get_page_url('defense', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        defense_buttons = soup(attrs={'class' : "detail_button"})
        
        defenses = []
        for def_button in defense_buttons:
            id = def_button['ref']
            defense_data = DEFENSES_DATA.get(id)
            amount_info = "".join(def_button.find("span", {"class" : "level"})
                            .findAll(text=True, recursive=False)[1])
            amount = int(re.sub("[^0-9]", "", amount_info))
            item = DefenseItem(defense_data.id, defense_data.name)
            defenses.append(ItemAction(item, amount))

        return defenses

    def auto_build_defenses(self, planet = None):
        """
        Build some defenses for the given planet
        """
        
        items = [ItemAction(DEFENSES_DATA.get(Defenses.PlasmaTurrent.value), '20'),
                 ItemAction(DEFENSES_DATA.get(Defenses.GaussCannon.value), '50'),
                 ItemAction(DEFENSES_DATA.get(Defenses.IonCannon.value), '10'),
                 ItemAction(DEFENSES_DATA.get(Defenses.HeavyLaser.value), '10'),
                 ItemAction(DEFENSES_DATA.get(Defenses.LightLaser.value), '3000'),
                 ItemAction(DEFENSES_DATA.get(Defenses.RocketLauncher.value), '3000')]
               
        self.logger.info('Auto building defenses')
        self.redirect_to_page(planet)
        for defense in items:
            self.build_defense_item(defense, planet)
           

    def redirect_to_page(self, planet = None):
        """
        Redirect to defense page for the given planet
        """
        url = self.url_provider.get_page_url('defense', planet)
        self.logger.info("Redirecting to page %s" % url)
        self.open_url(url)

    def build_defense(self, defense, amount, planet = None):
        """
        Redirect to the defense page and build the defense item
        
        defense parameter must be an Defense object
        
        """

        self.redirect_to_page(planet)

        try:
            self.build_defense_item(defense, planet)
        except Exception as e:
            self.logger.info('Error building defense')
            self.logger.info(e)

    def build_defense_item(self, item_action, planet = None):
        self.logger.info("building %s %s(s) on planet %s" % (item_action.amount, item_action.item.name, planet.name))
        self.logger.info("Writing data to form")
        self.browser.select_form(name='form')
        self.browser.form.new_control('text','menge',{'value': item_action.amount})
        self.browser.form.fixup()
        self.browser['menge'] = item_action.amount
        self.browser.form.new_control('text','type',{'value' : item_action.item.id})
        self.browser.form.fixup()
        self.browser['type'] = str(item_action.item.id)
        self.browser.form.new_control('text','modus',{'value':'1'})
        self.browser.form.fixup()
        self.browser['modus'] = '1'
        self.logger.info("Submitting build defense request")
        self.submit_request()
