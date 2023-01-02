import json
import logging
import os.path

from _pytest.fixtures import fixture
from playwright.sync_api import Playwright, sync_playwright

from page_objects.application import App
from settings import *


@fixture(autouse=True, scope='session')
def preconditions():
    logging.info('Pre-condition started')
    yield
    logging.info('Post-condition started')


@fixture(scope='session')
def get_playwright():
    with sync_playwright() as playwright:
        yield playwright


@fixture(scope='session', params=['chromium'], ids=['chromium'])
def get_browser(get_playwright, request):
    # browser = request.config.getoption('--browser')
    browser = request.param
    headless = request.config.getini('headless')

    if headless == 'True':
        headless = True
    else:
        headless = False

    if browser == 'chromium':
        yield get_playwright.chromium.launch(headless=headless)
    elif browser == 'firefox':
        yield get_playwright.firefox.launch(headless=headless)
    elif browser == 'webkit':
        yield get_playwright.webkit.launch(headless=headless)
    else:
        assert False, 'browser type is not supported'


@fixture(scope='session')
def desktop_app(get_browser, request):
    base_url = request.config.getini('base_url')
    app = App(get_browser, base_url=base_url, **BROWSER_OPTIONS)
    app.goto('/')
    yield app
    app.close()


@fixture(scope='session')
def desktop_app_auth(desktop_app):
    # secure = request.config.getoption('--secure')
    # config = load_config(secure)
    app = desktop_app
    app.goto('/login')
    # app.login(**config)
    login = os.environ.get('TESTME_USER')
    password = os.environ.get('TESTME_PWD')
    app.login(login=login, password=password)
    yield app


@fixture(scope='session', params=['iPhone 12 Mini landscape', 'Pixel 2'])
def mobile_app(get_playwright, get_browser, request):
    # device = request.config.getoption('--device')
    device = request.param
    device_config = get_playwright.devices.get(device)
    if device_config is not None:
        device_config.update(BROWSER_OPTIONS)
    else:
        device_config = BROWSER_OPTIONS
    base_url = request.config.getini('base_url')
    app = App(get_browser, base_url=base_url, **device_config)
    app.goto('/')
    yield app
    app.close()


@fixture(scope='session')
def mobile_app_auth(mobile_app):
    # secure = request.config.getoption('--secure')
    # config = load_config(secure)
    app = mobile_app
    app.goto('/login')
    # app.login(**config)
    login = os.environ.get('TESTME_USER')
    password = os.environ.get('TESTME_PWD')
    app.login(login=login, password=password)
    yield app


def pytest_addoption(parser):
    parser.addoption('--secure', action='store', default='secure.json')
    parser.addoption('--device', action='store', default='')
    parser.addoption('--browser', action='store', default='chromium')
    parser.addini('headless', help='run tests in headless mode', default=False)
    parser.addini('base_url', help='Base url of the site under test', default='http://127.0.0.1:8000')


def load_config(file):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    with open(config_file) as cfg:
        return json.loads(cfg.read())
