import pytest
from agents.weather_agent import get_weather
from agents.sql_agent import query_database
from agents.recommender_agent import recommend

def test_weather():
    result = get_weather("Singapore")
    assert isinstance(result, str) and "weather" in result.lower()

def test_sql():
    result = query_database("SELECT 1;")
    assert "1" in result

def test_recommend():
    result = recommend("books")
    assert "Recommended books" in result
