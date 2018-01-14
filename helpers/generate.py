import string
import random


def code(n):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))
