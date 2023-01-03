from pytest import mark

data = {'argnames': 'name, description',
        'argvalues': [
                          ('hello', 'world'),
                          ('hello', ''),
                          ('123', 'world')
                      ],
        'ids': ['with name and description', 'with no description', 'with digits in name']
        }


@mark.parametrize(**data)
def test_new_test_case(desktop_app_auth, name, description):
    desktop_app_auth.navigate_to('Create new test')
    desktop_app_auth.create_test(name, description)
    desktop_app_auth.navigate_to('Test Cases')
    test_exists = desktop_app_auth.test_cases.check_test_exists(name)
    desktop_app_auth.test_cases.delete_test_by_name(name)
    assert test_exists


def test_delete_test_case(desktop_app_auth, get_web_service):
    test_name = 'test for delete'
    get_web_service.create_test(test_name, 'delete me pls')
    desktop_app_auth.navigate_to('Test Cases')
    assert desktop_app_auth.test_cases.check_test_exists(test_name)
    desktop_app_auth.test_cases.delete_test_by_name(test_name)
    assert not desktop_app_auth.test_cases.check_test_exists(test_name)
