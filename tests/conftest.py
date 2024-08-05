"""
Configuration test
"""
import pytest
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from common.conf import Cfg


@pytest.fixture(scope="function")
def browser():
    """
    Main fixture
    """
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("start-maximized") # open Browser in maximized mode
    chrome_options.add_argument("--disable-infobars") # disabling infobars
    chrome_options.add_argument("--disable-extensions") # disabling extensions
    chrome_options.add_argument("--disable-gpu") #  applicable to windows os only
    chrome_options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
    chrome_options.add_argument("--disable-search-engine-choice-screen")
    # chrome_options.add_argument("--headless")

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def knockout():
    """
    Knockout all pokemons
    """
    header = {'Content-Type':'application/json','trainer_token': Cfg.TRAINER_TOKEN}
    pokemons = requests.get(url=f'{Cfg.API_URL}/pokemons', params={"trainer_id": Cfg.TRAINER_ID},
                            headers=header, timeout=3)
    if 'data' in pokemons.json():
        for pokemon in pokemons.json()['data']:
            if pokemon['status'] != 0:
                requests.post(url=f'{Cfg.API_URL}/pokemons/knockout', headers=header,
                              json={"pokemon_id": pokemon['id']}, timeout=3)
