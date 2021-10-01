import time
import os
from flask import session
from flask import url_for, redirect
from __init__ import ALLOWED_EXTENSIONS, secure_filename, app, flash
from PIL import Image


def save_requested_page(request, session_name: str = 'requested_page'):
    session['requested_page'] = request.base_url
    return session


def get_requested_page_or_home_page(request, session_name: str = 'requested_page', home_page_functions: str = 'index'):
    requested_page = session.get('requested_page')
    if requested_page:
        return redirect(requested_page)
    return url_for(home_page_functions)


def calculate_game_account_rate(heroes, parse_heroes):
    """This function calculates the rating of the game account

    Behavior:
        Lists all heroes on the game account and removes duplicates from the list. Further, if the hero is from
        ContentHeroGameAccount matches the hero from the Hero table, then the content_for_calculate list contains the
        character's rating.

        The rating is calculated by dividing the sum of the items in the content_for_calculate list by the number of
        items in the parse_heroes list.


    :param heroes (list): heroes available on the game account
    :param parse_heroes (list): heroes who managed to spar
    :return float: game account rating
    """

    content_for_calculate = []
    no_hero_duplicates = []
    for i in range(len(heroes)):
        no_hero_duplicates.append(heroes[i].hero)
    no_hero_duplicates = list(set(no_hero_duplicates))
    for j in range(len(no_hero_duplicates)):
        for hero in parse_heroes:
            if hero.name == no_hero_duplicates[j]:
                content_for_calculate.append(hero.rate)

    rate = (sum(content_for_calculate) / len(parse_heroes))
    return round(rate, 3)


def allowed_file(filename):
    """Checking for a valid extension

    :param filename: filename to check for valid extensions
    :return:
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def check_size_img(filename):
    """Checks the dimensions of an image

    :param filename: the name of the file for which you want to check the extension
    :return:
    """

    img, original_img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename)), Image.open(
        'static/img/faces/achates.jpg')
    width, height = img.size
    original_width, original_height = original_img.size
    if width != original_width or height != original_height:
        img.close(), original_img.close()
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return False
    else:
        img.close(), original_img.close()
        return True


def upload_img(file, entered_name):
    """Loading an image

    :param file: file to download
    :param entered_name: the name to assign to the file
    :return:
    """
    if file and allowed_file(file.filename):
        file.filename = entered_name + '.jpg'
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        if check_size_img(filename):
            return True
        else:
            flash('Image dimensions do not fit')
            return False
    else:
        return False
