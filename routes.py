from flask import render_template
from flask_login import login_user, login_required, logout_user, current_user
from start import *
from models import *
from errors import *

Role().add_standart_role()
User().create_superuser()
RoleAssignment().add_superuser_role()
Status().add_standart_statuses()
Hero().add_hero_from_json()
Artifact().add_artifact_from_json()


@application.route('/')
def index():
    return render_template("index.html")


@application.route('/search', methods=['GET', 'POST'])
def search():
    context = {
        'all_heroes': Hero().show_all_heroes(),
        'all_artifacts': Artifact().show_all_artifacts()
    }
    if request.method == 'POST':
        session['heroes'] = request.form.getlist('heroes')
        session['artifacts'] = request.form.getlist('artifacts')
        if len(session['heroes']) == 0 and len(session['artifacts']) == 0:
            flash("You haven't selected any hero or artifact!")
            return redirect(url_for('search'))
        return redirect(url_for('epicseven'))
    return render_template('search.html', **context)



@application.route('/board', methods=['GET'])
def epicseven():
    gameaccounts_info = GameAccount().show_gameaccount_all()
    sorted_gameaccounts_info = search_gameaccounts(session.get('heroes', []),
                                                   session.get('artifacts', []), gameaccounts_info)
    if sorted_gameaccounts_info is None:
        return render_template("epicseven.html", content=None, zip=zip)
    else:
        content = {
            "gameaccounts_info": sorted_gameaccounts_info
        }
        return render_template("epicseven.html", content=content, zip=zip)

@application.route('/about')
def about():
    return render_template("about.html")


@application.route('/faq')
def faq():
    return render_template("faq.html")


@application.route('/privacy-policy')
def privacy_policy():
    return render_template("privacy-policy.html")


@application.route('/copyright-policy')
def copyright_policy():
    return render_template("copyright-policy.html")


@application.route('/signin', methods=['GET', 'POST'])
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


@application.route('/contact-us', methods=['GET', 'POST'])
@login_required
def contact_us():
    form = ContactForm()
    if form.validate_on_submit():
        discord = form.discord.data
        user_email = form.email.data
        title = form.title.data
        message = form.message.data
        user = User.query.filter_by(email=user_email, id=current_user.get_id()).first()
        if user:
            msg_for_recipients = Message('Problems found!', sender=os.getenv('EMAIL'),
                                         recipients=[os.getenv('ADMIN_EMAIL')])
            msg_for_recipients.body = f'Request for improvement content fix!\n' \
                                      f'Discord: {discord}\n' \
                                      f'Email: {user_email}\n' \
                                      f'Title: {title}\n' \
                                      f'Message: {message}\n'
            mail.send(msg_for_recipients)
            flash("Your message has been successfully delivered!")
            return redirect(url_for('profile', user_login=user.login))
        else:
            flash("There is no user with this email!")
            return redirect(url_for('contact_us', form=form))

    return render_template('contact-form.html', form=form)

@application.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            if not check_password_hash(user.password, password):
                token = s.dumps({'email': email,
                                 'password': password},
                                salt='confirm-change-password')
                msg = Message('Confirm change password', sender=os.getenv('EMAIL'), recipients=[email])
                link = url_for('forgot_password_confirm', token=token, _external=True)
                msg.body = f'Your link is {link}'
                mail.send(msg)
                flash(f"A confirmation email has been sent to the address {email}")
                return redirect(url_for('forgot_password'))
            else:
                flash(f"You have entered the current password for {email}")
                return redirect(url_for('forgot_password'))
        else:
            flash(f"There is no such user {email}")
            return redirect(url_for('forgot_password'))

    return render_template('forgot-password.html', form=form)


@application.route('/forgot-password/confirm/<token>', methods=['GET', 'POST'])
def forgot_password_confirm(token):
    try:
        data = s.loads(token, salt='confirm-change-password', max_age=60 * 5)
        if User().change_password(data['email'], data['password']):
            flash(f"On the mailbox {data['email']} the password was changed.")
        else:
            flash("Something went wrong...")
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('signin'))
    return redirect(url_for('signin'))


@application.route('/admin-panel', methods=['GET', 'POST'])
@login_required
def admin_login():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        available_roles = Role().show_roles()
        available_statuses = Status().show_statuses()
        all_users = User().show_all_users()
        heroes_without_img = Hero().show_hero_without_img()
        artifacts_without_img = Artifact().show_artifacts_without_img()
        heroes = Hero().show_all_heroes()
        artifacts = Artifact().show_all_artifacts()
        content = {
            'users': all_users,
            'heroes_without_img': heroes_without_img,
            'artifacts_without_img': artifacts_without_img,
            'roles': available_roles,
            'statuses': available_statuses,
            'heroes': heroes,
            'artifacts': artifacts,
        }

        return render_template("admin-panel.html", content=content)
    return render_template('errors/error404.html'), 404


@application.route('/admin-panel/change-hero-data', methods=['GET', 'POST'])
@login_required
def change_hero_data():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        if request.method == 'POST':
            name = request.form.getlist('checkbox_hero')
            if len(name) != 0:
                if request.form['actionCard'] == 'DeleteCard':
                    token = s.dumps({'name': name[0], },
                                    salt='confirm-delete-hero')
                    msg = Message('Confirm delete hero', sender=os.getenv('EMAIL'), recipients=[user.email])
                    link = url_for('delete_hero_confirm', token=token, _external=True)
                    msg.body = f'Name hero for delete: {name[0]}\n' \
                               f'Please double-check the correctness of the entered data! \nIf you notice that the data ' \
                               f'are incorrect, then ignore this letter and repeat the character creation procedure again.\n' \
                               f'Your link is:\n{link}'
                    mail.send(msg)
                    flash(f"A confirmation letter for delete a hero was sent to {user.email}")
                    return redirect(url_for('admin_login'))
                if request.form['actionCard'] == 'UpdateCard':
                    return redirect(url_for('update_hero', name_hero=name[0]))
            else:
                flash("You haven't picked a hero!")
                return redirect(url_for('admin_login'))
    return render_template('errors/error404.html'), 404

@application.route('/admin-panel/confirm-delete-hero/<token>', methods=['GET', 'POST'])
def delete_hero_confirm(token):
    try:
        data = s.loads(token, salt='confirm-delete-hero', max_age=60 * 5)
        if Hero().delete_hero(hero_name=data['name']):
            flash('You have successfully deleted your hero!')
            return redirect(url_for('admin_login'))
        else:
            flash('Failed to delete the hero!')
            return redirect(url_for('admin_login'))
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('admin_login'))


@application.route('/admin-panel/change-artifact-data', methods=['GET', 'POST'])
@login_required
def change_artifact_data():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        if request.method == 'POST':
            name = request.form.getlist('checkbox_artifact')
            if len(name) != 0:
                if request.form['actionCard'] == 'DeleteCard':
                    token = s.dumps({'name': name[0],},
                                    salt='confirm-delete-artifact')
                    msg = Message('Confirm delete artifact', sender=os.getenv('EMAIL'), recipients=[user.email])
                    link = url_for('delete_artifact_confirm', token=token, _external=True)
                    msg.body = f'Name artifact for delete: {name[0]}\n' \
                               f'Please double-check the correctness of the entered data! \nIf you notice that the data ' \
                               f'are incorrect, then ignore this letter and repeat the character creation procedure again.\n' \
                               f'Your link is:\n{link}'
                    mail.send(msg)
                    flash(f"A confirmation letter for delete a artifact was sent to {user.email}")
                    return redirect(url_for('admin_login'))
                if request.form['actionCard'] == 'UpdateCard':
                    return redirect(url_for('update_artifact', name_artifact=name[0]))
            else:
                flash("You haven't picked a artifact!")
                return redirect(url_for('admin_login'))
    return render_template('errors/error404.html'), 404

@application.route('/admin-panel/confirm-delete-artifact/<token>', methods=['GET', 'POST'])
def delete_artifact_confirm(token):
    try:
        data = s.loads(token, salt='confirm-delete-artifact', max_age=60 * 5)
        if Artifact().delete_artifact(artifact_name=data['name']):
            flash('You have successfully deleted your artifact!')
            return redirect(url_for('admin_login'))
        else:
            flash('Failed to delete the artifact!')
            return redirect(url_for('admin_login'))
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('admin_login'))


@application.route('/admin-panel/update-hero/<name_hero>', methods=['GET', 'POST'])
@login_required
def update_hero(name_hero):
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        hero = Hero.query.filter_by(name=name_hero).first()
        data = {
            'name_hero': hero.name,
            'star_hero': hero.star,
            'rate_hero': hero.rate,
            'element_hero': hero.element,
            'classes_hero': hero.classes,
        }
        form = ChangeHero(data=data)
        if form.validate_on_submit():
            name = form.name_hero.data
            star = form.star_hero.data
            rate = form.rate_hero.data
            element = form.element_hero.data
            classes = form.classes_hero.data

            token = s.dumps({'name': name,
                             'star': star,
                             'user': user.login,
                             'rate': rate,
                             'element': element,
                             'classes': classes},
                            salt='confirm-update-hero')
            msg = Message('Confirm update hero', sender=os.getenv('EMAIL'), recipients=[user.email])
            link = url_for('update_hero_confirm', token=token, _external=True)
            msg.body = f'New hero name: {name}\n' \
                       f'Number of stars: {star}\n'\
                       f'Rate: {rate}\n' \
                       f'Element: {element}\n'\
                       f'Class: {classes}\n' \
                       f'Please double-check the correctness of the entered data! \nIf you notice that the data ' \
                       f'are incorrect, then ignore this letter and repeat the character creation procedure again.\n' \
                       f'Your link is:\n{link}'
            mail.send(msg)
            flash(f"A confirmation letter for update a artifact was sent to {user.email}")
            return redirect(url_for('admin_login'))

        return render_template('update-hero.html', form=form)
    return render_template('errors/error404.html'), 404


@application.route('/admin-panel/confirm-update-hero/<token>', methods=['GET', 'POST'])
def update_hero_confirm(token):
    try:
        data = s.loads(token, salt='confirm-update-hero', max_age=60 * 5)
        if Hero().update_hero(user_login=data['user'], hero_name=data['name'], star=data['star'], rate=data['rate'],
                              element=data['element'], classes=data['classes']):
            return redirect(url_for('admin_login'))
        else:
            return redirect(url_for('update_hero', name_hero=data['name']))
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('admin_login'))


@application.route('/admin-panel/update-artifact/<name_artifact>', methods=['GET', 'POST'])
@login_required
def update_artifact(name_artifact):
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        artifact = Artifact.query.filter_by(name=name_artifact).first()
        data = {
            'name_artifact': artifact.name,
            'star_artifact': artifact.star,
            'classes_artifact': artifact.classes,
        }
        form = ChangeArtifact(data=data)
        if form.validate_on_submit():
            name = form.name_artifact.data
            star = form.star_artifact.data
            classes = form.classes_artifact.data
            token = s.dumps({'name': name,
                             'star': star,
                             'user': user.login,
                             'classes': classes},
                            salt='confirm-update-artifact')
            msg = Message('Confirm update artifact', sender=os.getenv('EMAIL'), recipients=[user.email])
            link = url_for('update_artifact_confirm', token=token, _external=True)
            msg.body = f'New artifact name: {name}\n' \
                       f'Number of stars: {star}\n' \
                       f'Class: {classes}\n' \
                       f'Please double-check the correctness of the entered data! \nIf you notice that the data ' \
                       f'are incorrect, then ignore this letter and repeat the character creation procedure again.\n' \
                       f'Your link is:\n{link}'
            mail.send(msg)
            flash(f"A confirmation letter for update a artifact was sent to {user.email}")
            return redirect(url_for('admin_login'))
        return render_template('update-artifact.html', form=form)
    return render_template('errors/error404.html'), 404


@application.route('/admin-panel/confirm-update-artifact/<token>', methods=['GET', 'POST'])
def update_artifact_confirm(token):
    try:
        data = s.loads(token, salt='confirm-update-artifact', max_age=60 * 5)
        if Artifact().update_artifact(user_login=data['user'], artifact_name=data['name'], star=data['star'],
                                      classes=data['classes']):
            return redirect(url_for('admin_login'))
        else:
            return redirect(url_for('update_artifact', name_artifact=data['name']))
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('admin_login'))


@application.route('/admin-panel/add-new-hero-form', methods=['GET', 'POST'])
@login_required
def create_hero():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        form = CreateHero()
        if form.validate_on_submit():
            name = form.name_hero.data
            star = form.star_hero.data
            rate = form.rate_hero.data
            element = form.element_hero.data
            classes = form.classes_hero.data
            token = s.dumps({'name': name,
                             'star': star,
                             'rate': rate,
                             'user': user.login,
                             'element': element,
                             'classes': classes},
                            salt='confirm-create-hero')
            msg = Message('Confirm create hero', sender=os.getenv('EMAIL'), recipients=[user.email])
            link = url_for('create_hero_confirm', token=token, _external=True)
            msg.body = f'New character name: {name}\n' \
                       f'Number of stars: {star}\n' \
                       f'Rating: {rate} \n' \
                       f'Element: {element}\n' \
                       f'Class: {classes}\n' \
                       f'Please double-check the correctness of the entered data! \nIf you notice that the data ' \
                       f'are incorrect, then ignore this letter and repeat the character creation procedure again.\n' \
                       f'Your link is:\n{link}'
            mail.send(msg)
            flash(f"A confirmation letter for adding a hero was sent to {user.email}")
            return redirect(url_for('admin_login'))
        return render_template('create-hero.html', form=form)
    return render_template('errors/error404.html'), 404


@application.route('/admin-panel/confirm-create-hero/<token>', methods=['GET', 'POST'])
def create_hero_confirm(token):
    try:
        data = s.loads(token, salt='confirm-create-hero', max_age=60 * 5)
        if Hero().create_hero(user_login=data['user'], name_hero=data['name'], stars_hero=data['star'],
                              rate_hero=data['rate'], classes=data['classes'], element=data['element']):
            flash("The hero was created successfully!")
            return redirect(url_for('admin_login'))
        else:
            return redirect(url_for('create_hero'))
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('admin_login'))


@application.route('/admin-panel/add-new-artifact-form', methods=['GET', 'POST'])
@login_required
def create_artifact():
    user = User.query.filter_by(id=current_user.get_id()).first()
    if user.role.filter_by(role='Admin').first():
        form = CreateArtifact()
        if form.validate_on_submit():
            name = form.name_artifact.data
            star = form.star_artifact.data
            classes = form.classes_artifact.data
            token = s.dumps({'name': name,
                             'star': star,
                             'user': user.login,
                             'classes': classes},
                            salt='confirm-create-artifact')
            msg = Message('Confirm create artifact', sender=os.getenv('EMAIL'), recipients=[user.email])
            link = url_for('create_artifact_confirm', token=token, _external=True)
            msg.body = f'New artifact name: {name}\n' \
                       f'Number of stars: {star}\n' \
                       f'Class: {classes}\n' \
                       f'Please double-check the correctness of the entered data! \nIf you notice that the data ' \
                       f'are incorrect, then ignore this letter and repeat the artifact creation procedure again.\n' \
                       f'Your link is:\n{link}'
            mail.send(msg)
            flash(f"A confirmation letter for adding a artifact was sent to {user.email}")
            return redirect(url_for('admin_login'))
        return render_template('create-artifact.html', form=form)
    return render_template('errors/error404.html'), 404


@application.route('/admin-panel/confirm-create-artifact/<token>', methods=['GET', 'POST'])
def create_artifact_confirm(token):
    try:
        data = s.loads(token, salt='confirm-create-artifact', max_age=60 * 5)
        if Artifact().create_artifact(user_login=data['user'],
                                      name_artifact=data['name'],
                                      stars_artifact=data['star'],
                                      classes=data['classes']):
            flash("The artifact was created successfully!")
            return redirect(url_for('admin_login'))
        else:
            return redirect(url_for('create_artifact'))
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('admin_login'))


@application.route('/admin-panel/hero-img-upload', methods=['GET', 'POST'])
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


@application.route('/admin-panel/artifact-img-upload', methods=['GET', 'POST'])
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


@application.route('/admin-panel/members/<member_login>', methods=['GET', 'POST'])
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


@application.route('/admin-panel/roles/create-role', methods=['GET', 'POST'])
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


@application.route('/admin-panel/statuses/create-status', methods=['GET', 'POST'])
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


@application.route('/admin-panel/statuses/delete-status', methods=['GET', 'POST'])
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


@application.route('/admin-panel/roles/delete-role', methods=['GET', 'POST'])
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


@application.route('/admin-panel/members/<member_login>/add-role', methods=['GET', 'POST'])
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


@application.route('/admin-panel/members/<member_login>/add-status', methods=['GET', 'POST'])
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


@application.route('/admin-panel/members/<member_login>/take-off-role', methods=['GET', 'POST'])
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
                    flash(f"Role {form.roles.data} successfully deleted from the user {member_login}")
                    return redirect(url_for('member_profile', member_login=member_login))
                else:
                    return redirect(url_for('take_off_role', member_login=member_login))
            else:
                flash("You can't take the role off yourself!")
                return redirect(url_for('take_off_role', member_login=member_login))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('change-role-form.html', form=form, member_login=member_login)


@application.route('/admin-panel/members/<member_login>/take-off-status', methods=['GET', 'POST'])
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
                    flash(f"Status {form.statuses.data} successfully deleted from the user {member_login}")
                    return redirect(url_for('member_profile', member_login=member_login))
                else:
                    return redirect(url_for('take_off_status', member_login=member_login))
            else:
                flash("You cannot remove the status from yourself!")
                return redirect(url_for('take_off_status', member_login=member_login))
    else:
        return render_template('errors/error404.html'), 404
    return render_template('change-status-form.html', form=form, member_login=member_login)


@application.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        login = form.login.data
        discord_nickname = form.discord_nickname.data
        password = form.password.data

        if not User.query.filter_by(email=email).first() and not User.query.filter_by(login=login).first():
            token = s.dumps({'email': email,
                             'discord_nickname': discord_nickname,
                             'login': login,
                             'password': password},
                            salt='confirm-signup')
            msg = Message('Confirm your email address', sender=os.getenv('EMAIL'), recipients=[email])
            link = url_for('confirm_signup', token=token, _external=True)
            msg.body = f'Your link is {link}'
            mail.send(msg)
            flash(f"A confirmation email has been sent to the address {email}")
            return redirect(url_for('signup'))
        else:
            flash("The user is already registered!")
            return redirect(url_for('signup'))

    return render_template('register_user.html', form=form)


@application.route('/signup/confirm/<token>', methods=['GET', 'POST'])
def confirm_signup(token):
    try:
        data = s.loads(token, salt='confirm-signup', max_age=60 * 5)
        if not User.query.filter_by(email=data['email']).first():
            user = User().register(email=data['email'],
                                   login=data['login'],
                                   password=data['password'],
                                   discord_nickname=data['discord_nickname'])
            if user:
                flash(f"You have successfully registered!")
            else:
                flash("Something went wrong...")
        else:
            flash("A user with this email already exists!")
    except SignatureExpired:
        flash("Link expired :(")
        return redirect(url_for('signin'))
    return redirect(url_for('signin'))


@application.route('/logout/', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(id=current_user.get_id()).first()
    return redirect(url_for('profile_login', user_login=user.login))


@application.route('/profile/<user_login>', methods=['GET', 'POST'])
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


@application.route('/profile/<user_login>/create-game-account-form', methods=['GET', 'POST'])
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


@application.route('/profile/<user_login>/change-discord', methods=['GET', 'POST'])
@login_required
def change_discord(user_login):
    user = User.query.filter_by(id=current_user.get_id()).first()
    person = {'discord': user.discord_nickname}
    form = ChangeDiscord(data=person)
    if form.validate_on_submit():
        discord = form.discord.data
        if not User.query.filter_by(discord_nickname=discord).first() \
                and User().change_discord(email=user.email, discord_nickname=discord):
            flash("You have successfully changed your discord nickname!")
            return redirect(url_for('profile', user_login=user.login))
        else:
            flash("An account with such a discord nickname already exists!")
            return redirect(url_for('change_discord', user_login=user.login))
    return render_template("change-discord.html", user_login=user.login, form=form)


@application.route('/profile/<user_login>/<name_account>', methods=['GET', 'POST'])
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


@application.route('/profile/<user_login>/<name_account>/add-card-hero/', methods=['GET', 'POST'])
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


@application.route('/profile/<user_login>/<name_account>/add-card-artifact/', methods=['GET', 'POST'])
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


@application.route('/profile/<user_login>/<name_account>/delete-card-hero/', methods=['GET', 'POST'])
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


@application.route('/profile/<user_login>/<name_account>/delete-card-artifact/', methods=['GET', 'POST'])
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


@application.route('/profile/<user_login>/<name_account>/delete-game-account', methods=['GET', 'POST'])
@login_required
def deleteGameAccount(user_login, name_account):
    if request.method == 'POST':
        user = User.query.filter_by(id=current_user.get_id()).first()
        name = user.possessions.filter_by(name=name_account).first().name
        if user.possessions.filter_by(name=name_account).first():
            token = s.dumps({'login': user.login,
                             'name': name},
                            salt='confirm-delete')
            msg = Message(f'Confirm delete account {name}', sender=os.getenv('EMAIL'), recipients=[user.email])
            link = url_for('deleteGameAccount_confirm', token=token, _external=True)
            msg.body = f'Your link is {link}'
            mail.send(msg)
            flash(f"A confirmation email has been sent to the address {user.email}")
            return redirect(url_for('profile', user_login=user.login))
        else:
            flash("You don't have such an account!")
            return redirect(url_for('profile', user_login=user.login))

    return render_template('errors/error404.html'), 404


@application.route('/delete-account/confirm/<token>', methods=['GET', 'POST'])
def deleteGameAccount_confirm(token):
    try:
        data = s.loads(token, salt='confirm-delete', max_age=60 * 5)
        if GameAccount().delete(user_owner=data['login'],
                                name=data['name']):
            flash("The account has been successfully deleted!")
            return redirect(url_for('profile', user_login=data['login']))
        else:
            flash("The game account could not be deleted...")
            return redirect(url_for('profile', user_login=data['login']))
    except SignatureExpired:
        flash("Link expired :(")
        return render_template("game-account_profile.html")


@application.route('/profile/<user_login>/<name_account>/change-game-account-form', methods=['GET', 'POST'])
@login_required
def change_game_account_form(user_login, name_account):
    user = User.query.filter_by(id=current_user.get_id()).first()
    content = {
        "name": user.possessions.filter_by(name=name_account).first().name,
        "garaunteed_roll": user.possessions.filter_by(name=name_account).first().garaunteed_roll,
        "price": user.possessions.filter_by(name=name_account).first().price,
        "status_code": user.possessions.filter_by(name=name_account).first().status_code
    }
    gameaccount = {'price': content['price'],
                   'status_code': content['status_code'],
                   'garaunteed_roll': content['garaunteed_roll']}
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


@application.after_request
def redirect_to_sign(response):
    if response.status_code == 401:
        save_requested_page(request)
        return redirect(url_for('signin'))
    return response
