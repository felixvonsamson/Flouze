from .globals import current_user

def change_user(user):
    global current_user
    current_user = user
