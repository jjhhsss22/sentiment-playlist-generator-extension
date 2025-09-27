
def is_valid_username(username):  # validates username by checking for spaces
    if " " in username:
        return False
    else:
        return True


def is_valid_password(password1, password2):  # validates password by checking against the rules

    if password1 != password2:  # verifies the two password inputs
        return False

    if len(password1) < 8:
        return False

    upper = any(char.isupper() for char in password1)  # checks for any capital letters and returns a Boolean value
    digit = any(char.isdigit() for char in password1)  # checks for any numbers and returns a Boolean value

    if upper and digit:
        return True
    else:
        return False