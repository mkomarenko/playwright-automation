import allure
from pytest import mark

data = {'argnames': 'name, description',
        'argvalues': [
                          ('hello', 'world'),
                          ('hello', ''),
                          ('123', 'world')
                      ],
        'ids': ['with name and description', 'with no description', 'with digits in name']
        }


@allure.title('Create new test case')
@mark.parametrize(**data)
def test_new_test_case(desktop_app_auth, name, description, get_db):
    tests_num = len(get_db.list_test_cases())
    desktop_app_auth.navigate_to('Create new test')
    desktop_app_auth.create_test(name, description)
    desktop_app_auth.navigate_to('Test Cases')
    assert tests_num + 1 == len(get_db.list_test_cases())
    assert desktop_app_auth.test_cases.check_test_exists(name)
    # desktop_app_auth.test_cases.delete_test_by_name(name)
    get_db.delete_test_case(name)
    assert tests_num == len(get_db.list_test_cases())


@allure.title('Delete test case')
def test_delete_test_case(desktop_app_auth, get_web_service):
    test_name = 'test for delete'
    get_web_service.create_test(test_name, 'delete me pls')
    desktop_app_auth.navigate_to('Test Cases')
    assert desktop_app_auth.test_cases.check_test_exists(test_name)
    desktop_app_auth.test_cases.delete_test_by_name(test_name)
    assert not desktop_app_auth.test_cases.check_test_exists(test_name)
