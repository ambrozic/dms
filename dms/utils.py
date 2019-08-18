import random

chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def str20():
    return "".join([chars[random.randint(0, len(chars) - 1)] for _ in range(20)])
