from datetime import datetime, date
import os
import requests
from bank.db import get_tuition, add_tuition_and_balance


# TODO: burada günde 3 kere callanmaya karşı bir kod olmalı; dict olabilir {(date, id): call_count} olan
def get_tuition(student_id: int):
    return get_tuition(student_id)


def pay_tuition(student_id, term) -> bool:
    res = get_tuition(student_id=student_id)
    if res[1] > res[0]:
        add_tuition_and_balance(student_id, tuition=0, balance=res[1] - res[0])
        return True
