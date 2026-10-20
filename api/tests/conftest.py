import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session")
def client():
    return TestClient(app)

BIRTH = {"date": "1990-05-15", "time": "10:30:00", "timezone": "Asia/Kolkata", "latitude": 28.6139, "longitude": 77.209}
BIRTH2 = {"date": "1992-08-20", "time": "18:45:00", "timezone": "Asia/Kolkata", "latitude": 19.07, "longitude": 72.88}
DELHI = {"lat": 28.65195, "lon": 77.23149, "tz": "Asia/Kolkata"}
