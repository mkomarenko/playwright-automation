import json

import allure
from pytest import mark


@allure.title('Check Dashboard data')
@mark.test_id(200)
def test_dashboard_data(desktop_app_auth):
    payload = json.dumps({"total": 0, "passed": 0, "failed": 0, "norun": 0})
    desktop_app_auth.intercept_requests('**/getstat*', payload)
    desktop_app_auth.refresh_dashboard()
    total_tests = desktop_app_auth.get_total_tests_stats()
    desktop_app_auth.stop_intercept('**/getstat*')
    assert '0' == total_tests


@allure.title('Verify multiple roles')
@mark.test_id(201)
def test_multiple_roles(desktop_app_auth, desktop_app_bob, get_db):
    test_name = 'hello123'
    alice = desktop_app_auth
    alice.refresh_dashboard()
    bob = desktop_app_bob
    before = alice.get_total_tests_stats()
    bob.navigate_to('Create new test')
    bob.create_test(test_name, 'world')
    alice.refresh_dashboard()
    after = alice.get_total_tests_stats()
    get_db.delete_test_case(test_name)
    assert int(before) + 1 == int(after)
