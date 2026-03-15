import pytest
import requests
from pydantic import BaseModel



BASE_URL = "https://restful-booker.herokuapp.com"


class BookingDates(BaseModel):
    checkin: str
    checkout: str


class BookingData(BaseModel):
    firstname: str; lastname: str; totalprice: int; depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str


class AuthClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def get_token(self, username, password):
        payload = {"username": username, "password": password}
        response = requests.post(f"{self.base_url}/auth", json=payload)
        response.raise_for_status()
        return response.json()["token"]


class BookingClient:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def create_booking(self, booking_data: BookingData) -> requests.Response:
        response = requests.post(f"{self.base_url}/booking", json=booking_data.model_dump())
        response.raise_for_status()
        return response
        

    def delete_booking(self, booking_id: int, token: str) -> requests.Response: 
        headers = {
            'Content-Type' : 'application/json',
            'Accept': 'application/json',
            'Cookie': f'token={token}'
        }
        response = requests.delete(f"{self.base_url}/booking/{booking_id}", headers=headers)
        response.raise_for_status()
        return response


@pytest.fixture(scope="session")
def auth_client():
    return AuthClient(BASE_URL)


@pytest.fixture(scope="session")
def booking_client():
    return BookingClient(BASE_URL)


@pytest.fixture(scope="session")
def token(auth_client: AuthClient):
    return auth_client.get_token("admin", "password123")


@pytest.fixture
def booking_id(booking_client: BookingClient, token):
    dates = BookingDates(checkin="2026-05-01", checkout="2026-05-05")
    data = BookingData(firstname="API", lastname="Client", totalprice=999, depositpaid=False, bookingdates=dates, additionalneeds="None")
    
    response = booking_client.create_booking(data)
    new_id = response.json()["bookingid"]
    print(f"\nКлиент создал бронь {new_id}")
    
    yield new_id
    
    delete = booking_client.delete_booking(new_id, token)
    assert delete.status_code == 201
    print(f"\nКлиент удалил бронь {new_id}")


def test_booking_can_be_deleted(booking_id):
    response = requests.get(f"{BASE_URL}/booking/{booking_id}")
    assert response.status_code == 200

