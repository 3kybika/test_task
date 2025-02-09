import random

# ToDo - to conf
RANDOM_SEED = 42

random.seed(RANDOM_SEED)


def get_id():
    return random.randint(10000, 60000)
