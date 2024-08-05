import pytest
import requests

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.conf import Cfg
from common.utils import wait_for


def test_positive_login(browser):
    """
    POC-1. Positive login
    """
    browser.get(url=f'{Cfg.URL}/login')

    logger.info('Step 1. Wait for clickable email input, type email and password')
    email = WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[class*="f_email"]')))
    email.click()
    email.send_keys(Cfg.VALID['email'])

    password = browser.find_element(by=By.CSS_SELECTOR, value='[class*="f_pass"]')
    password.click()
    password.send_keys(Cfg.VALID['password'])

    logger.info('Step 2. Press Enter to login')
    enter = browser.find_element(by=By.CSS_SELECTOR, value='[class*="send_auth"]')
    enter.click()
    
    WebDriverWait(browser, timeout=10, poll_frequency=2).until(EC.url_to_be(f'{Cfg.URL}/'))

    logger.info('Step 3. Find trainer ID')
    trainer_id = browser.find_element(by=By.CLASS_NAME, value='header__id-texts')
    assert trainer_id.text.replace('\n', ': ') == f'ID: {Cfg.TRAINER_ID}', 'Unexpected ID trainer'


CASES = [
    ('1', Cfg.INVALID['email'], Cfg.VALID['password'], ['Введите почту', '']),
    ('2', Cfg.VALID['email'], Cfg.INVALID['password'], ['', 'Неверные логин или пароль']),
    ('3', '', Cfg.VALID['password'], ['Введите почту', '']),
    ('4', Cfg.VALID['email'], '', ['', 'Введите пароль'])
]

@pytest.mark.parametrize('case, email, password, exp_alert', CASES)
def test_negative_login(case, email, password, exp_alert, browser):
    """
    POC-2. Negative cases for login
    """
    def check_alerts(browser):
        alerts = browser.find_elements(by=By.CSS_SELECTOR, value='[class*="auth__error"]')
        return [alert.text for alert in alerts]

    browser.get(url=Cfg.URL)

    email_input = WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[class*="f_email"]')))
    email_input.click()
    email_input.send_keys(email)

    password_input = browser.find_element(by=By.CSS_SELECTOR, value='[class*="f_pass"]')
    password_input.click()
    password_input.send_keys(password)

    enter_button = browser.find_element(by=By.CSS_SELECTOR, value='[class*="send_auth"]')
    enter_button.click()

    assert wait_for(lambda: check_alerts(browser) == exp_alert)(), 'Unexpected alert message'


def test_check_api(browser, knockout):
    """
    POC-3. Check create pokemon by api request
    """
    browser.get(url=Cfg.URL)

    email = WebDriverWait(browser, timeout=10, poll_frequency=2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[class*="f_email"]')))
    email.click()
    email.send_keys(Cfg.VALID['email'])

    password = browser.find_element(by=By.CSS_SELECTOR, value='[class*="f_pass"]')
    password.click()
    password.send_keys(Cfg.VALID['password'])

    enter = browser.find_element(by=By.CSS_SELECTOR, value='[class*="send_auth"]')
    enter.click()
    
    WebDriverWait(browser, timeout=5, poll_frequency=1).until(EC.url_to_be(f'{Cfg.URL}/'))
    
    browser.find_element(by=By.CLASS_NAME, value='header__id-texts').click()
    WebDriverWait(browser, timeout=5, poll_frequency=1).until(EC.url_to_be(f'{Cfg.URL}/trainer/{Cfg.TRAINER_ID}'))

    pokemon_count_before = browser.find_element(by=By.CSS_SELECTOR, value='[class="pokemons-info"] [class*="total-count"]')
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
        (By.CSS_SELECTOR, '[class="pokemons-info"] [class*="total-count"]'), f'{count_before+1}')), \
            'Unexpected pokemons count'
