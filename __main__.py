from __future__ import annotations
from requests import get
from random import choice
from gologin import GoLogin
import pandas as pd
import time
from selenium import webdriver
from collections.abc import Iterable, Iterator
from typing import Any, List

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait

from logger import logger

LOGGER = logger('rudos')


class Data(Iterator):
    _url = ('https://docs.google.com/spreadsheets/d/1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw'
             '/export?format=csv&id=1zaxjdu9ESYy2MCNuDow0_5PnZpwEsyrdTQ_kk0PMZbw&gid=479200214')
    _position: int = 0

    def __init__(self, value) -> None:
        df = pd.read_csv(Data._url)
        self._collection = (df[value].dropna().tolist())

    def __next__(self):
        try:
            value = self._collection[self._position]
            self._position += 1
        except IndexError:
            raise StopIteration()
        return value


class Rudos:
    def __init__(self, profile_id, **kwargs):
        self.gl = GoLogin(dict(token=kwargs['gologin_key']))
        self.gl.setProfileId(profile_id)
        self.debugger_address = self.gl.start()
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", self.debugger_address)
        self.driver = webdriver.Chrome(options=options)

    def auth(self, login: str, password: str):
        LOGGER.info('login: {}, password : {}'.format(login, password))
        URL = 'https://ua.joblum.com/login'
        self.driver.get(URL)
        try:
            username_element = self.driver.find_element_by_id('loginform-username')
            WebDriverWait(self.driver, 5).until(lambda d: username_element)
            username_element.send_keys(login)
            self.driver.find_element_by_id('loginform-password').send_keys(password)
            submit_button_element = self.driver.find_element_by_name('signup-button')
            submit_button_element.click()
            return True
        except Exception as error:
            LOGGER.exception(error)
            return False

    def spam(self, title: str, description: str):
        LOGGER.info('title: {}'.format(title))
        URL = 'https://ua.joblum.com/employer/rabota-v-kieve/job-add'
        self.driver.get(URL)
        try:
            title_eleement = self.driver.find_element_by_id('vacancy-title')
            WebDriverWait(self.driver, 5).until(lambda d: title_eleement)
            title_eleement.send_keys(title)
            self.driver.find_element_by_id('vacancy-location').send_keys('Киев')
            self.driver.find_element_by_id('vacancy-specialization_id').click()
            self.driver.find_element_by_xpath('//*[@id="vacancy-specialization_id"]/option[2]')
            self.driver.find_element_by_xpath('vacancy-salary_from').send_keys(f'1{choice([5, 6, 7, 8, 9])}000')
            self.driver.find_element_by_id('vacancy-salary_to').send_keys(f'2{choice([0, 1, 2, 3, 4, 5])}000')
            self.driver.find_element_by_xpath('//*[@id="w1"]/div[9]/div[1]/div').send_keys(description)
            self.driver.find_element_by_xpath('//*[@id="w1"]/div[10]/button').click()
            return True
        except NoSuchElementException as error:
            LOGGER.error(error)
            return False
        except Exception as error:
            LOGGER.exception(error)
            return False


def main():
    title = Data('title')
    description = Data('description')
    login = Data('login')
    password = Data('password')
    profile_id = Data('profile_id')
    gologin_key = Data('gologin_key')
    rudos = Rudos(next(profile_id), gologin_key=next(gologin_key))
    if rudos.auth(next(login), next(password)):
        while True:
            rudos.spam(next(title), next(description))
            time.sleep(30)


try:
    if __name__ == '__main__':
        main()
except Exception as error:
    LOGGER.exception(error)
