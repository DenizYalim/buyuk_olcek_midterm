
# Limit call to 3 per student per day using a simple in-memory counter per student
from __future__ import annotations
from datetime import datetime, date
import os
from typing import Dict
import requests

_CALLS: Dict[int, Dict[str, int]] = {}
_MAX_CALLS_PER_DAY = 3


def _today_str() -> str:
    return date.today().isoformat()


def get_tuition(student_id: int): 
    # rate limit
    key = student_id
    today = _today_str()
    if key not in _CALLS or _CALLS[key].get("date") != today:
        # initialize for today
        _CALLS[key] = {"date": today, "count": 0}

    if _CALLS[key]["count"] >= _MAX_CALLS_PER_DAY:
        raise ValueError("daily limit reached for student")


    bank_base = os.environ.get("BANK_URL", "http://127.0.0.1:5001/bank")
    url = f"{bank_base.rstrip('/')}/get_tuition"

    try:
        resp = requests.get(url, params={"id": student_id}, timeout=3)
        resp.raise_for_status()
    except requests.RequestException as ex:
        raise

    data = resp.json()

    _CALLS[key]["count"] += 1

    return data


def pay_tuition(student_id: int):
    pass