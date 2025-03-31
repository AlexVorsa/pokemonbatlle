"""
Smoke tests for pokemons
"""
import pytest
import requests

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.conf import Cfg

class Locators:
    """
    Class for locators
    """
    EMAIL = '[class*="k_form_control"] [id="k_email"]'
    PASSWORD = '[class*="k_form_control"] [id="k_password"]'
    LOGIN = '[class*="k_form_send_auth"]'
    TRAINER_ID = '[class="header_card_trainer_id_num"]'
    ALERT = '[class*="auth__error"]'
    POK_TOTAL_COUNT = '[class*="pokemons"] [class*="total-count"]'

def test_positive_login(browser):
    """
    POC-1. Positive login
    """
    browser.get(url=f'{Cfg.URL}/login')

    logger.info('Step 1. Wait for clickable email input, type email and password')
    email = WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, Locators.EMAIL)))
    email.click()
    email.send_keys(Cfg.VALID['email'])

    password = browser.find_element(by=By.CSS_SELECTOR, value=Locators.PASSWORD)
    password.click()
    password.send_keys(Cfg.VALID['password'])

    logger.info('Step 2. Press Enter to login')
    enter = browser.find_element(by=By.CSS_SELECTOR, value=Locators.LOGIN)
    enter.click()

    WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.url_to_be(f'{Cfg.URL}/'))

    logger.info('Step 3. Find trainer ID')
    trainer_id = browser.find_element(by=By.CSS_SELECTOR, value=Locators.TRAINER_ID)
    assert trainer_id.text == Cfg.TRAINER_ID, 'Unexpected ID trainer'


CASES = [
    ('1', Cfg.INVALID['email'], Cfg.VALID['password'], 'Введите корректную почту'),
    ('2', Cfg.VALID['email'], Cfg.INVALID['password'], 'Неверные логин или пароль'),
    ('3', '', Cfg.VALID['password'], 'Введите почту'),
    ('4', Cfg.VALID['email'], '', 'Введите пароль')
]

@pytest.mark.parametrize('case, email, password, exp_alert', CASES)
def test_negative_login(case, email, password, exp_alert, browser):
    """
    POC-2. Negative cases for login
    """
    logger.info(f'Negative case № {case}')
    browser.get(url=Cfg.URL)

    email_input = WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, Locators.EMAIL)))
    email_input.click()
    email_input.send_keys(email)

    password_input = browser.find_element(by=By.CSS_SELECTOR, value=Locators.PASSWORD)
    password_input.click()
    password_input.send_keys(password)

    enter_button = browser.find_element(by=By.CSS_SELECTOR, value=Locators.LOGIN)
    enter_button.click()

    alert = WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, Locators.ALERT)))

    assert alert.text == exp_alert, 'Unexpected alert message'


def test_check_api(browser, knockout):
    """
    POC-3. Check create pokemon by api request
    """
    browser.get(url=Cfg.URL)

    email = WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, Locators.EMAIL)))
    email.click()
    email.send_keys(Cfg.VALID['email'])

    password = browser.find_element(by=By.CSS_SELECTOR, value=Locators.PASSWORD)
    password.click()
    password.send_keys(Cfg.VALID['password'])

    enter = browser.find_element(by=By.CSS_SELECTOR, value=Locators.LOGIN)
    enter.click()
    
    WebDriverWait(browser, timeout=5, poll_frequency=1).until(EC.url_to_be(f'{Cfg.URL}/'))
    
    trainer = WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, Locators.TRAINER_ID)))
    trainer.click()
    
    pok = WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, '[class*="pokemon_one_body_content_inner_pokemons"]')))
    WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        lambda x: 'feature-empty' not in pok.get_attribute('class'))
    
    pokemon_count_before = browser.find_element(by=By.CSS_SELECTOR, value=Locators.POK_TOTAL_COUNT)
    count_before = int(pokemon_count_before.text)

    body_create = {
        "name": "generate",
        "photo_id": 1
    }
    header = {'Content-Type':'application/json','trainer_token': Cfg.TRAINER_TOKEN}
    response_create = requests.post(url=f'{Cfg.API_URL}/pokemons', headers=header, json=body_create, timeout=3)
    assert response_create.status_code == 201, 'Unexpected response status_code'

    browser.refresh()

    assert WebDriverWait(browser, timeout=5, poll_frequency=1).until(EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, Locators.POK_TOTAL_COUNT), f'{count_before+1}')), 'Unexpected pokemons count'
