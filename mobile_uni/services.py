
from datetime import datetime, date
import os
import requests

CALLS = {}
MAX_CALLS_PER_DAY = 3


def _today_str() -> str:
    return date.today().isoformat()


def get_tuition(student_id: int): 
    # rate limit
    key = student_id
    today = _today_str()
    if key not in CALLS or CALLS[key].get("date") != today:
        # initialize for today
        CALLS[key] = {"date": today, "count": 0}

    if CALLS[key]["count"] >= MAX_CALLS_PER_DAY:
        raise ValueError("daily limit reached for student")


    bank_base = os.environ.get("BANK_URL", "http://127.0.0.1:5001/bank")
    url = f"{bank_base.rstrip('/')}/get_tuition"

    try:
        resp = requests.get(url, params={"id": student_id}, timeout=3)
        resp.raise_for_status()
    except requests.RequestException as ex:
        raise

    data = resp.json()

    CALLS[key]["count"] += 1

    return data


def pay_tuition(student_id: int):
    pass