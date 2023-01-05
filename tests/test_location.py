import allure
from pytest import mark


@allure.title('Check geolocation')
@mark.test_id(202)
def test_location_ok(mobile_app_auth):
    location = mobile_app_auth.get_location()
    assert '48.8:2.3' == location
