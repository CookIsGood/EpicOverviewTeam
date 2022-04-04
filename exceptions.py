class ExistingLogin(Exception):
    print('Такой логин уже существует!')

class DataNotMatch(Exception):
    print('Данные не совпадают')

class NotEnoughRights(Exception):
    print('У вас не хватает прав для этого действия')

class InvalidNumberCharacters(Exception):
    print("Неверное количество символов")