import allure
from pytest import mark


@allure.title('Check that columns are hidden in mobile view')
@mark.test_id(203)
def test_columns_hidden(mobile_app_auth):
    mobile_app_auth.click_main_menu()
    mobile_app_auth.navigate_to('Test Cases')
    assert mobile_app_auth.test_cases.check_columns_hidden()
    assert False
