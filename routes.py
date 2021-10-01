from flask import render_template
from flask_login import login_user, login_required, logout_user, current_user
from __init__ import *
from models import *
from errors import *
from buisness_logic import *

Role().add_standart_role()
User().create_superuser()
RoleAssignment().add_superuser_role()
Status().add_standart_statuses()
Hero().add_hero()
Artifact().add_artifact()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/privacy-policy')
def privacy_policy():
    return render_template("privacy-policy.html")

@app.route('/copyright-policy')
def copyright_policy():
    return render_template("copyright-policy.html")

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        try:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Authorization failed!')
        except AttributeError:
            flash('The username or password is incorrect!')
    return render_template('login_user.html', form=form)


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            if not check_password_hash(user.password, password):
                token_for_email = s.dumps(email, salt='confirm-change-email')
                token_for_password = s.dumps(password, salt='confirm-change-password')
                msg = Message('Confirm change password', sender=email, recipients=[email])
                link = url_for('forgot_password_confirm', token=token_for_email, password=token_for_password,
                               _external=True)
                msg.body = f'Your link is {link}'
                mail.send(msg)
                flash(f"A confirmation email has been sent to the address {email}")
                return redirect(url_for('forgot_password'))
            else:
                login_user(user)
                flash(f"You have entered the current password for {email}")
                return redirect(url_for('forgot_password'))
        else:
            flash(f"There is no such user {email}")
            return redirect(url_for('forgot_password'))

    return render_template('forgot-password.html', form=form)


@app.route('/forgot-password/confirm/<token>/<password>', methods=['GET', 'POST'])
def forgot_password_confirm(token, password):
    try:
        email = s.loads(token, salt='confirm-change-email', max_age=60 * 5)
        password = s.loads(password, salt='confirm-change-password', max_age=60 * 5)
        if User().change_password(email, password):
            flash(f"On the mailbox {email} the password was changed.")
        else:
            flash("Something went wrong...")
    except SignatureExpired:
        flash("Link expired :(")
        return render_template("login_user.html")
    return render_template('login_user.html')


@app.route('/admin-panel', methods=['GET', 'POST'])
@login_required
def admin_login():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        available_roles = Role().show_roles()
        available_statuses = Status().show_statuses()
        all_users = User().show_all_users()
        heroes_without_img = Hero().show_hero_without_img()
        artifacts_without_img = Artifact().show_artifacts_without_img()
        content = {
            'users': all_users,
            'heroes_without_img': heroes_without_img,
            'artifacts_without_img': artifacts_without_img,
            'roles': available_roles,
            'statuses': available_statuses
        }

        return render_template("admin-panel.html", content=content)
    return render_template('errors/error404.html'), 404


@app.route('/admin-panel/hero-img-upload', methods=['GET', 'POST'])
@login_required
def hero_img_upload():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        if request.method == 'POST':
            hero_file = request.files['hero_file']
            hero_name = request.form.getlist('have_checkbox_heroes')
            if len(hero_name) != 0:
                if upload_img(hero_file, hero_name[0]):
                    flash("The file upload was successful!")
                    return redirect(url_for('profile'))
                else:
                    flash("The file could not be downloaded")
                    return redirect(url_for('profile'))
            else:
                flash("You have not chosen which hero to download!")
                return redirect(url_for('profile'))
    return render_template('errors/error404.html'), 404

@app.route('/admin-panel/artifact-img-upload', methods=['GET', 'POST'])
@login_required
def artifact_img_upload():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        if request.method == 'POST':
            artifact_file = request.files['artifact_file']
            artifact_name = request.form.getlist('have_checkbox_artifacts')
            if len(artifact_name) != 0:
                if upload_img(artifact_file, artifact_name[0]):
                    flash("The file upload was successful!")
                    return redirect(url_for('profile'))
                else:
                    flash("The file could not be downloaded")
                    return redirect(url_for('profile'))
            else:
                flash("You have not chosen which artifact to download!")
                return redirect(url_for('profile'))
    return render_template('errors/error404.html'), 404

@app.route('/admin-panel/members/<member_login>', methods=['GET', 'POST'])
@login_required
def member_profile(member_login):
    user = User.query.filter_by(id=current_user.id).first()
    if user.role.filter_by(role='Admin').first():
        member = User.query.filter_by(login=member_login).first()
        member_info = User().show_user_info(member.login)
        gameaccounts_info = GameAccount().show_gameaccount_by_owner(user_owner=member.login)
        content = {
            "user_info": member_info,
            "gameaccounts_info": gameaccounts_info
        }
        return render_template("member-profile.html", content=content, member_login=member.login, zip=zip)
    return render_template('errors/error404.html'), 404


@app.route('/admin-panel/roles/create-role', methods=['GET', 'POST'])
@login_required
def create_role():
    user = User.query.filter_by(id=current_user.get_id()).first()
    form = CreateRoleForm()
    if user.role.filter_by(role='Admin').first():
        if form.validate_on_submit():
            get_role_for_add = form.role.data
            if Role().create_role(get_role_for_add):
                return redirect(url_for('admin_login'))
            else:
                return redirect(url_for('admin_login'))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('create-role-form.html', form=form)

@app.route('/admin-panel/statuses/create-status', methods=['GET', 'POST'])
@login_required
def create_status():
    user = User.query.filter_by(id=current_user.get_id()).first()
    form = CreateStatusForm()
    if user.role.filter_by(role='Admin').first():
        if form.validate_on_submit():
            get_status_for_add = form.status.data
            if Status().create_status(get_status_for_add):
                return redirect(url_for('admin_login'))
            else:
                return redirect(url_for('admin_login'))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('create-status-form.html', form=form)

@app.route('/admin-panel/statuses/delete-status', methods=['GET', 'POST'])
@login_required
def delete_status():
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        if user.role.filter_by(role='Admin').first():
            list_statuses_for_delete = request.form.getlist('have_checkbox_status')
            for item in list_statuses_for_delete:
                if Status().delete_status(item):
                    return redirect(url_for('admin_login'))
                else:
                    return redirect(url_for('admin_login'))
        return redirect(url_for('admin_login'))
    return render_template('errors/error404.html'), 404


@app.route('/admin-panel/roles/delete-role', methods=['GET', 'POST'])
@login_required
def delete_role():
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        if user.role.filter_by(role='Admin').first():
            list_roles_for_delete = request.form.getlist('have_checkbox_role')
            for item in list_roles_for_delete:
                if Role().delete_role(item):
                    flash(f"Role {item} deleted successfully!")
                    return redirect(url_for('admin_login'))
                else:
                    flash(f"Failed to delete role {item}!")
                    return redirect(url_for('admin_login'))
        return redirect(url_for('admin_login'))
    return render_template('errors/error404.html'), 404


@app.route('/admin-panel/members/<member_login>/add-role', methods=['GET', 'POST'])
@login_required
def add_role(member_login):
    user = User.query.filter_by(id=current_user.get_id()).first()
    available_roles = Role.query.all()
    group_roles = [(i.role, i.role) for i in available_roles]
    form = ActionWithRole()
    form.roles.choices = group_roles
    if user.role.filter_by(role='Admin').first():
        if form.validate_on_submit():
            if user.login != member_login:
                if RoleAssignment().add_role_user(login=member_login, role=form.roles.data):
                    return redirect(url_for('member_profile', member_login=member_login))
                else:
                    return redirect(url_for('add_role', member_login=member_login))
            else:
                flash("You can't add roles to yourself!")
                return redirect(url_for('add_role', member_login=member_login))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('change-role-form.html', form=form, member_login=member_login)

@app.route('/admin-panel/members/<member_login>/add-status', methods=['GET', 'POST'])
@login_required
def add_status(member_login):
    user = User.query.filter_by(id=current_user.get_id()).first()
    available_statuses = Status.query.all()
    group_statuses = [(i.status, i.status) for i in available_statuses]
    form = ActionWithStatus()
    form.statuses.choices = group_statuses
    if user.role.filter_by(role='Admin').first():
        if form.validate_on_submit():
            if user.login != member_login:
                if StatusAssignment().add_status_user(login_user=member_login, status=form.statuses.data):
                    return redirect(url_for('member_profile', member_login=member_login))
                else:
                    return redirect(url_for('add_status', member_login=member_login))
            else:
                flash("You can't add statuses to yourself!")
                return redirect(url_for('add_status', member_login=member_login))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('change-status-form.html', form=form, member_login=member_login)


@app.route('/admin-panel/members/<member_login>/take-off-role', methods=['GET', 'POST'])
@login_required
def take_off_role(member_login):
    user = User.query.filter_by(id=current_user.get_id()).first()
    available_roles = Role.query.all()
    group_roles = [(i.role, i.role) for i in available_roles]
    form = ActionWithRole()
    form.roles.choices = group_roles
    if user.role.filter_by(role='Admin').first():
        if form.validate_on_submit():
            if user.login != member_login:
                if RoleAssignment().delete_role_user(login=member_login, role=form.roles.data):
                    return redirect(url_for('member_profile', member_login=member_login))
                else:
                    return redirect(url_for('take_off_role', member_login=member_login))
            else:
                flash("You can't take the role off yourself!")
                return redirect(url_for('take_off_role', member_login=member_login))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('change-role-form.html', form=form, member_login=member_login)

@app.route('/admin-panel/members/<member_login>/take-off-status', methods=['GET', 'POST'])
@login_required
def take_off_status(member_login):
    user = User.query.filter_by(id=current_user.get_id()).first()
    available_statuses = Status.query.all()
    group_statuses = [(i.status, i.status) for i in available_statuses]
    form = ActionWithStatus()
    form.statuses.choices = group_statuses
    if user.role.filter_by(role='Admin').first():
        if form.validate_on_submit():
            if user.login != member_login:
                if StatusAssignment().delete_status_user(login_user=member_login, status=form.statuses.data):
                    return redirect(url_for('member_profile', member_login=member_login))
                else:
                    return redirect(url_for('take_off_status', member_login=member_login))
            else:
                flash("You cannot remove the status from yourself!")
                return redirect(url_for('take_off_status', member_login=member_login))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('change-status-form.html', form=form, member_login=member_login)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        login = form.login.data
        discord_nickname = form.discord_nickname.data
        password = form.password.data

        if not User.query.filter_by(email=email).first() and not User.query.filter_by(login=login).first() and \
                not User.query.filter_by(discord_nickname=discord_nickname).first():
            token_for_email = s.dumps(email, salt='confirm-signup-email')
            token_for_discord_nickname = s.dumps(discord_nickname, salt='confirm-signup-discord_nickname')
            token_for_login = s.dumps(login, salt='confirm-signup-login')
            token_for_password = s.dumps(password, salt='confirm-signup-password')
            msg = Message('Confirm your email address', sender=email, recipients=[email])
            link = url_for('confirm_signup', token=token_for_email, password=token_for_password,
                           login=token_for_login, discord_nickname=token_for_discord_nickname, _external=True)
            msg.body = f'Your link is {link}'
            mail.send(msg)
            flash(f"A confirmation email has been sent to the address {email}")
            return redirect(url_for('signup'))
        else:
            flash("The user is already registered!")
            return redirect(url_for('signup'))

    return render_template('register_user.html', form=form)


@app.route('/signup/confirm/<token>/<password>/<login>/<discord_nickname>', methods=['GET', 'POST'])
def confirm_signup(token, password, login, discord_nickname):
    form = LoginForm()
    try:
        email = s.loads(token, salt='confirm-signup-email', max_age=60 * 5)
        login = s.loads(login, salt='confirm-signup-login', max_age=60 * 5)
        discord_nickname = s.loads(discord_nickname, salt='confirm-signup-discord_nickname', max_age=60 * 5)
        password = s.loads(password, salt='confirm-signup-password', max_age=60 * 5)

        if not User.query.filter_by(email=email).first():
            user = User().register(email=email, login=login, password=password, discord_nickname=discord_nickname)
            if user:
                flash(f"You have successfully registered!")
            else:
                flash("Something went wrong...")
        else:
            flash("A user with this email already exists!")
    except SignatureExpired:
        flash("Link expired :(")
        return render_template("login_user.html", form=form)
    return render_template('login_user.html', form=form)


@app.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    if request.method == 'POST':
        logout_user()
        return redirect(url_for('index'))
    return render_template('errors/error404.html'), 404


@app.route('/board', methods=['GET', 'POST'])
@cache.cached(timeout=60*5)
def epicseven():
    gameaccounts_info = GameAccount().show_gameaccount_all()
    if gameaccounts_info is None:
        return render_template("epicseven.html", content=None, zip=zip)
    else:
        content = {
            "gameaccounts_info": gameaccounts_info
        }
        return render_template("epicseven.html", content=content, zip=zip)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(id=current_user.get_id()).first()
    return redirect(url_for('profile_login', user_login=user.login))


@app.route('/profile/<user_login>', methods=['GET', 'POST'])
@login_required
def profile_login(user_login):
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.login == user_login:
        user_info = User().show_user_info(login=user.login)
        gameaccounts_info = GameAccount().show_gameaccount_by_owner(user_owner=user.login)
        content = {
            "user_info": user_info,
            "gameaccounts_info": gameaccounts_info
        }
        return render_template("profile.html", user_login=user.login, content=content, zip=zip)
    else:
        return redirect(url_for('index'))


@app.route('/profile/<user_login>/create-game-account-form', methods=['GET', 'POST'])
@login_required
def create_game_account_form(user_login):
    form = CreateGameAccountForm()
    user = User.query.filter_by(id=current_user.get_id()).first()
    if form.validate_on_submit():
        name = form.name.data
        garaunteed_roll = form.garaunteed_roll.data
        price = form.price.data
        user = User.query.filter_by(id=current_user.get_id()).first()
        if not GameAccount.query.filter_by(name=name).first():
            if GameAccount().create(name=name, garaunteed_roll=garaunteed_roll, price=price, user_owner=user.email):
                flash("The game account has been successfully created!")
                return redirect(url_for('profile', user_login=user.login))
            else:
                flash("Something went wrong")
                return redirect(url_for('create_game_account_form', user_login=user.login))
        else:
            flash("An account with that name already exists!")
            return redirect(url_for('create_game_account_form', user_login=user.login))
    return render_template("create-game-account.html", user_login=user.login, form=form)


@app.route('/profile/<user_login>/change-discord', methods=['GET', 'POST'])
@login_required
def change_discord(user_login):
    user = User.query.filter_by(id=current_user.get_id()).first()
    person = {'discord': user.discord_nickname}
    form = ChangeDiscord(data=person)
    if form.validate_on_submit():
        discord = form.discord.data
        if not User.query.filter_by(discord_nickname=discord).first()\
                and User().change_discord(email=user.email, discord_nickname=discord):
            flash("You have successfully changed your discord nickname!")
            return redirect(url_for('profile', user_login=user.login))
        else:
            flash("An account with such a discord nickname already exists!")
            return redirect(url_for('change_discord', user_login=user.login))
    return render_template("change-discord.html", user_login=user.login, form=form)


@app.route('/profile/<user_login>/<name_account>', methods=['GET', 'POST'])
@login_required
def profile_account(user_login, name_account):
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.possessions.filter_by(name=name_account).first():
        account_info = user.possessions.filter_by(name=name_account).first()
        artifacts = Artifact().show_all_artifacts()
        heroes = Hero().show_all_heroes()
        gameaccounts_info = GameAccount().show_gameaccount_by_name(user_owner=user.login, name=name_account)
        content = {
            "gameaccounts_info": gameaccounts_info,
            "heroes": heroes,
            "artifacts": artifacts
        }
        return render_template('game-account_profile.html', user_login=user.login,
                               name_account=account_info.name, content=content)
    return redirect(url_for('profile', user_login=user.login))


@app.route('/profile/<user_login>/<name_account>/add-card-hero/', methods=['GET', 'POST'])
@login_required
def add_card_hero(user_login, name_account):
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        hero_cards = request.form.getlist('checkbox_hero')
        if len(hero_cards) != 0:
            if ContentHeroGameAccount().add_card(name_game_account=name_account, heroes=hero_cards):
                flash("Heroes have been successfully added!")
                return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
            else:
                flash("Failed to add heroes!")
                return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
        else:
            flash("You didn't choose the heroes!")
            return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
    return render_template('errors/error404.html'), 404


@app.route('/profile/<user_login>/<name_account>/add-card-artifact/', methods=['GET', 'POST'])
@login_required
def add_card_artifact(user_login, name_account):
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        artifact_cards = request.form.getlist('checkbox_artifact')
        if len(artifact_cards) != 0:
            if ContentArtifactGameAccount().add_card(name_game_account=name_account, artifacts=artifact_cards):
                flash("Artifacts have been added successfully!")
                return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
            else:
                flash("Failed to add artifacts!")
                return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
        else:
            flash("You didn't choose artifacts!")
            return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
    return render_template('errors/error404.html'), 404


@app.route('/profile/<user_login>/<name_account>/delete-card-hero/', methods=['GET', 'POST'])
@login_required
def delete_card_hero(user_login, name_account):
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        hero_cards = request.form.getlist('have_checkbox_hero')
        if ContentHeroGameAccount().delete_card(name_game_account=name_account, heroes=hero_cards):
            flash("Heroes have been successfully removed!")
            return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
        else:
            flash("Failed to delete heroes!")
            return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
    return render_template('errors/error404.html'), 404


@app.route('/profile/<user_login>/<name_account>/delete-card-artifact/', methods=['GET', 'POST'])
@login_required
def delete_card_artifact(user_login, name_account):
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        artifact_cards = request.form.getlist('have_checkbox_artifact')
        if ContentArtifactGameAccount().delete_card(name_game_account=name_account, artifacts=artifact_cards):
            flash("Artifacts have been successfully removed!")
            return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
        else:
            flash("Failed to delete artifacts!")
            return redirect(url_for('profile_account', user_login=user.login, name_account=name_account))
    return render_template('errors/error404.html'), 404


@app.route('/profile/<user_login>/<name_account>/delete-game-account', methods=['GET', 'POST'])
@login_required
def deleteGameAccount(user_login, name_account):
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        name = user.possessions.filter_by(name=name_account).first().name
        if user.possessions.filter_by(name=name_account).first():
            token_for_login = s.dumps(user.login, salt='confirm-delete-login')
            token_for_name = s.dumps(name, salt='confirm-delete-name')
            msg = Message(f'Confirm delete account {name}', sender=email, recipients=[user.email])
            link = url_for('deleteGameAccount_confirm', token=token_for_login, name=token_for_name,
                           _external=True)
            msg.body = f'Your link is {link}'
            mail.send(msg)
            flash(f"A confirmation email has been sent to the address {user.email}")
            return redirect(url_for('profile', user_login=user.login))
        else:
            flash("You don't have such an account!")
            return redirect(url_for('profile', user_login=user.login))

    return render_template('errors/error404.html'), 404


@app.route('/delete-account/confirm/<token>/<name>', methods=['GET', 'POST'])
def deleteGameAccount_confirm(token, name):
    try:
        login = s.loads(token, salt='confirm-delete-login', max_age=60 * 5)
        name = s.loads(name, salt='confirm-delete-name', max_age=60 * 5)
        user = User.query.filter_by(id=current_user.get_id()).first()
        if GameAccount().delete(user_owner=login,
                                name=name):
            flash("The account has been successfully deleted!")
            return redirect(url_for('profile', user_login=user.login))
        else:
            flash("The game account could not be deleted...")
            return redirect(url_for('profile', user_login=user.login))
    except SignatureExpired:
        flash("Link expired :(")
        return render_template("game-account_profile.html")


@app.route('/profile/<user_login>/<name_account>/change-game-account-form', methods=['GET', 'POST'])
@login_required
def change_game_account_form(user_login, name_account):
    user = User.query.filter_by(id=current_user.get_id()).first()
    content = {
        "name": user.possessions.filter_by(name=name_account).first().name,
        "garaunteed_roll": user.possessions.filter_by(name=name_account).first().garaunteed_roll,
        "price": user.possessions.filter_by(name=name_account).first().price,
        "status_code": user.possessions.filter_by(name=name_account).first().status_code
    }
    gameaccount = {'price': user.possessions.filter_by(name=name_account).first().price}
    form = ChangeSettingsGameAccountForm(data=gameaccount)
    if form.validate_on_submit():
        user_owner = user.login
        name = user.possessions.filter_by(name=name_account).first().name
        garaunteed_roll = form.garaunteed_roll.data
        price = form.price.data
        status_code = form.status_code.data
        if GameAccount().change_settings(user_owner=user_owner, name=name,
                                         garaunteed_roll=garaunteed_roll,
                                         price=price, status_code=status_code):
            flash("Account settings have been successfully changed!")
            return redirect(url_for('profile_account', user_login=user.login, name_account=name))
        else:
            flash("Failed to change account settings!")
            return redirect(url_for('change_game_account_form', user_login=user.login, name_account=name))

    return render_template('change-game-account.html', content=content, form=form)


@app.after_request
def redirect_to_sign(response):
    if response.status_code == 401:
        save_requested_page(request)
        return redirect(url_for('signin'))
    return response
