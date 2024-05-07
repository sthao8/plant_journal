import json
import requests

from flask import session, redirect
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/register")
        return f(*args, **kwargs)

    return decorated_function


def lookup(plant_name):
    """Queries API for info based on plant name, returns list of dict for each plant found"""

    # Third-party house plants API
    url = "https://house-plants2.p.rapidapi.com/search"

    querystring = {"query": plant_name}

    headers = {
        "X-RapidAPI-Key": "05507268a1msh8e61f7fade5a0bap152d15jsn8fa5ef60d1a7",
        "X-RapidAPI-Host": "house-plants2.p.rapidapi.com",
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()

        keys = [
            "id",
            "Img",
            "Latin name",
            "Common name",
            "Climat",
            "Avaibility",
            "Categories",
        ]
        plants_info = []
        for plant in response.json():
            plant_info = {}
            for key in keys:
                plant_info[key] = plant["item"][key]
            plants_info.append(plant_info)

        if plants_info:
            return plants_info
        else:
            return None

    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def lookup_by_id(plant_id: str):
    """Queries API using one plant_id, returns one dict"""
    url = f"https://house-plants2.p.rapidapi.com/id/{plant_id}"

    headers = {
        "X-RapidAPI-Key": "05507268a1msh8e61f7fade5a0bap152d15jsn8fa5ef60d1a7",
        "X-RapidAPI-Host": "house-plants2.p.rapidapi.com",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response:
            return response.json()
        else:
            return None

    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def update_table(db, insert_data, table_name):
    # Filters out none data
    valid_insert_data = {
        data_type: data for data_type, data in insert_data.items() if data
    }
    data_type = valid_insert_data.keys()
    data = valid_insert_data.values()

    # Dynamically build a sql query if table_name is in allowed table_names based on filtered data
    if table_name in ["event_history", "intake_details"]:
        query = (
            f"INSERT INTO {table_name} ("
            + ", ".join(data_type)
            + ") VALUES ("
            + ", ".join(["%s"] * len(data))
            + ");"
        )
    else:
        raise ValueError("Unathorized table access.")

    # Executes the dynamic sql query with only valid data(no None allowed)
    db.execute(query, *data)
