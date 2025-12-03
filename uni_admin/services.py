import requests
from bank.db import get_all_unpaid, add_tuition_and_balance

TUITON_COST = 1000


def add_tuition(stu_id, term=1):
    add_tuition_and_balance(stu_id, term * TUITON_COST)


def add_tuition_batch():  # this should read from a csv
    for a in b:
        add_tuition(a["id"], a["term"])


def get_unpaid_tuitions():
    return get_all_unpaid()
