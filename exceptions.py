class ExistingLogin(Exception):
    print('This login already exists!')

class DataNotMatch(Exception):
    print('The data does not match!')

class NotEnoughRights(Exception):
    print('You do not have enough rights for this action!')

class InvalidNumberCharacters(Exception):
    print("Invalid number of characters!")