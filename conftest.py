import json
import logging
import os.path
import allure

from pytest import fixture, hookimpl
from playwright.sync_api import sync_playwright

from helpers.db import DataBase
from helpers.web_service import WebService
from page_objects.application import App
from settings import *


@fixture(autouse=True, scope='session')
def preconditions(request):
    logging.info('Pre-condition started')
    base_url = request.config.getini('base_url')
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    yield
    logging.info('Post-condition started')
    web = WebService(base_url)
    web.login(**config["users"]["userRole3"])
    for test in request.node.items:
        if len(test.own_markers) > 0:
            if test.own_markers[0].name == 'test_id':
                if test.result_call.passed:
                    web.report_test(test.own_markers[0].args[0], 'PASS')
                elif test.result_call.failed:
                    web.report_test(test.own_markers[0].args[0], 'FAIL')


@fixture(scope='session')
def get_web_service(request):
    base_url = request.config.getini('base_url')
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    web = WebService(base_url)
    web.login(**config["users"]["userRole1"])
    yield web
    web.close()


@fixture(scope='session')
def get_db(request):
    path = request.config.getini('db_path')
    db = DataBase(path)
    yield db
    db.close()


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
def desktop_app_auth(request, desktop_app):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    app = desktop_app
    app.goto('/login')
    app.login(**config["users"]["userRole1"])
    # login = os.environ.get('TESTME_USER')
    # password = os.environ.get('TESTME_PWD')
    # app.login(login=login, password=password)
    yield app


@fixture(scope='session')
def desktop_app_bob(get_browser, request):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    base_url = request.config.getini('base_url')
    app = App(get_browser, base_url=base_url, **BROWSER_OPTIONS)
    app.goto('/login')
    app.login(**config["users"]["userRole2"])
    yield app
    app.close()


@fixture(scope='session', params=['Pixel 2', 'iPhone 12 Mini'], ids=['Pixel 2', 'iPhone 12 Mini'])
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
def mobile_app_auth(mobile_app, request):
    secure = request.config.getoption('--secure')
    config = load_config(secure)
    app = mobile_app
    app.goto('/login')
    app.login(**config["users"]["userRole1"])
    # login = os.environ.get('TESTME_USER')
    # password = os.environ.get('TESTME_PWD')
    # app.login(login=login, password=password)
    yield app


@hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    # result.when == "setup" >> "call" >> "teardown"
    setattr(item, f'result_{result.when}', result)


@fixture(scope='function', autouse=True)
def make_screenshot(request):
    yield
    if request.node.result_call.failed:
        for arg in request.node.funcargs.values():
            if isinstance(arg, App):
                allure.attach(body=arg.page.screenshot(),
                              name='screenshot',
                              attachment_type=allure.attachment_type.PNG)


def pytest_addoption(parser):
    parser.addoption('--secure', action='store', default='secure.json')
    parser.addoption('--device', action='store', default='')
    parser.addoption('--browser', action='store', default='chromium')
    parser.addini('headless', help='run tests in headless mode', default=False)
    parser.addini('base_url', help='Base url of the site under test', default='http://127.0.0.1:8000')
    parser.addini('db_path', help='path to sqlite db file', default='C:\\Users\\maxko\\repo\\TestMe-TCM\\db.sqlite3')


def load_config(file):
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    with open(config_file) as cfg:
        return json.loads(cfg.read())
