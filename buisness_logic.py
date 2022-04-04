import time
import os
from flask import session
from flask import url_for, redirect
from PIL import Image
from start import ALLOWED_EXTENSIONS, secure_filename, application, flash, ast


def save_requested_page(request, session_name: str = 'requested_page'):
    session['requested_page'] = request.base_url
    return session


def get_requested_page_or_home_page(request, session_name: str = 'requested_page', home_page_functions: str = 'index'):
    requested_page = session.get('requested_page')
    if requested_page:
        return redirect(requested_page)
    return url_for(home_page_functions)


def _find_match_account(all_hero_cards, all_artifact_cards, hero_on_account, artifact_on_account):
    """This function checks if the selected heroes/artifacts have on the game account.

    :param all_hero_cards: selected_heroes
    :param all_artifact_cards: selected artifacts
    :param hero_on_account: heroes on the game account
    :param artifact_on_account: artifacts on the game account
    :return:
    """
    counter = 0
    count_cards = len(all_hero_cards) + len(all_artifact_cards)

    remaining_heroes = hero_on_account
    for card_in_all_hero_cards in all_hero_cards:
        if card_in_all_hero_cards in remaining_heroes and counter != count_cards:
            counter = counter + 1
            remaining_heroes.remove(card_in_all_hero_cards)

    remaining_artifacts = artifact_on_account
    for card_in_all_artifact_cards in all_artifact_cards:
        if card_in_all_artifact_cards in remaining_artifacts and counter != count_cards:
            counter = counter + 1
            remaining_artifacts.remove(card_in_all_artifact_cards)
    if counter == count_cards:
        remaining_heroes.extend(all_hero_cards)
        remaining_artifacts.extend(all_artifact_cards)
        return True


def _sort_gameaccounts(content: list):
    """This function sorts the list of dictionaries by the value of the matches key.

    :param content: list of dictionaries to be sorted
    :return:
    """
    new_content = sorted(content, key=lambda k: k['rate'], reverse=True)
    return new_content


def search_gameaccounts(hero_names: list, artifact_names: list, gameaccounts: dict):
    """This function displays the game account if it finds the selected heroes of the facts in descending order of rating

    :param hero_names: user selected heroes
    :param artifact_names: user selected artifacts
    :param gameaccounts: list of available game accounts
    :return:
    """
    all_hero, all_artifact = hero_names, artifact_names
    content = []

    for gameaccount in gameaccounts:
        if _find_match_account(all_hero, all_artifact, gameaccount['heroes'], gameaccount['artifacts']):
            content.append(gameaccount)

    content = _sort_gameaccounts(content)
    return content


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


def _allowed_file(filename):
    """Checking for a valid extension

    :param filename: filename to check for valid extensions
    :return:
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def _check_size_img(filename):
    """Checks the dimensions of an image

    :param filename: the name of the file for which you want to check the extension
    :return:
    """

    img, original_img = Image.open(os.path.join(application.config['UPLOAD_FOLDER'], filename)), Image.open(
        'static/img/faces/achates.jpg')
    width, height = img.size
    original_width, original_height = original_img.size
    if width != original_width or height != original_height:
        img.close(), original_img.close()
        os.remove(os.path.join(application.config['UPLOAD_FOLDER'], filename))
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
    if file and _allowed_file(file.filename):
        file.filename = entered_name + '.jpg'
        filename = secure_filename(file.filename)
        file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
        if _check_size_img(filename):
            return True
        else:
            flash('Image dimensions do not fit')
            return False
    else:
        return False
