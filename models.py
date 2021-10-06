from flask_login import login_user
from sqlalchemy.orm import backref
from werkzeug.security import check_password_hash
from buisness_logic import *
from __init__ import *
from exceptions import *
from abc import ABCMeta, abstractmethod


class AbstUser():
    __metaclass__ = ABCMeta

    @abstractmethod
    def register(self):
        pass

    @staticmethod
    def _check_password_equality(password, password2):
        """Password Equality Check

        Behavior:
            If the strings are equal, then True, otherwise False.

        :param password (str): first line input
        :param password2 (str): second line input
        :return boolean:
        """
        if password == password2:
            return True
        return False


class User(AbstUser, db.Model, UserMixin):
    __tablename__ = 'user'
    """Class for storing users
    
    id - record numbering
    login - user name
    email - user mail
    password - user password
    created_at - when the account was registered
    
    possessions - game accounts that are linked to user.
    role - the roles the user has
    status - the status that the user has (banned and etc)
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True, nullable=False)
    login = db.Column(db.String(10), unique=True, nullable=False)
    discord_nickname = db.Column(db.String(25), unique=False, nullable=False)
    password = db.Column(db.Text, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    role = db.relationship("RoleAssignment", backref="user", lazy="dynamic")
    possessions = db.relationship("GameAccount", backref="user", lazy="dynamic")
    status = db.relationship("StatusAssignment", backref="user", lazy="dynamic")

    def change_discord(self, discord_nickname, email):
        user = self.query.filter_by(email=email).first()
        user.discord_nickname = discord_nickname
        db.session.commit()
        return True


    def create_superuser(self):
        """This function creates a superuser.

        Behavior:
            If the admin user does not exist, then it creates it.

        :return:
        """
        if not self.query.filter_by(email=admin_email).first():
            user = User(email=admin_email, login='admin', password=generate_password_hash(admin_password), discord_nickname='key#8211')
            db.session.add(user)
            db.session.commit()
            return True
        else:
            return False

    def show_user_info(self, login: str):
        """This function shows information about the user.

        Behavior:
            The user's record is taken from the database, all roles and statuses belonging to the user are written to
            the list.
            A dictionary is returned.

        :param login (str): user login
        :return :
        """
        user = self.query.filter_by(login=login).first()
        roles = []
        all_roles = user.role.all()
        for i in range(len(all_roles)):
            roles.append(all_roles[i].role)
        statuses = []
        all_statuses = user.status.all()
        for i in range(len(all_statuses)):
            statuses.append(all_statuses[i].status)
        content = {
            'email': user.email,
            'login': user.login,
            'discord_nickname': user.discord_nickname,
            'created_at': user.created_at,
            'roles': roles,
            'statuses': statuses
        }
        return content

    def show_all_users(self):  # show_all_users can be combined with show_user_info
        """This function is designed to display information about all users.

        Behavior:
            It works similarly to the show_user_info function, except that the query is made to all records in the User
            table.

        :return:
        """
        users = self.query.all()
        content = []
        for item in users:
            roles = []
            all_roles = item.role.all()
            for i in range(len(all_roles)):
                roles.append(all_roles[i].role)

            statuses = []
            all_statuses = item.status.all()
            for i in range(len(all_statuses)):
                statuses.append(all_statuses[i].status)
            user_info = {
                'email': item.email,
                'login': item.login,
                'discord_nickname': item.discord_nickname,
                'created_at': item.created_at,
                'roles': roles,
                'statuses': statuses
            }
            content.append(user_info)
        return content

    def register(self, email: str, login: str, discord_nickname: str, password: str, role: str = 'User'):
        """This function creates a new user

        Behavior:
            The user record is created and the user is assigned the User (default) role.

        :param email (str): user email
        :param login (str): user login
        :param discord_nickname (str): user discord
        :param password (str): user password
        :param role (str): user role (default - User)
        :return user:
        """

        try:
            user = User(email=email, login=login, discord_nickname=discord_nickname, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            db.session.add(RoleAssignment(user_login=login, role=role))
            db.session.commit()
            return user

        except ExistingLogin:
            raise ValueError('This login already exists!')

    def change_password(self, email, password):
        """Changes user password by email

        :param email: user email
        :param password: user password
        :return:
        """
        user = self.query.filter_by(email=email).first()
        user.password = generate_password_hash(password)
        db.session.commit()
        return True

    def __repr__(self):
        return f"{self.email}:{self.login}:{self.password}"


class StatusAssignment(db.Model):
    __tablename__ = 'statusassignment'

    """Class for assigning users roles

    status - roles from the status table
    user_login - username from the user table
    """
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), db.ForeignKey('status.status'))
    user_login = db.Column(db.String(10), db.ForeignKey('user.login'))

    def add_status_user(self, login_user: str, status: str):
        """This function adds status to the user

        Behavior:
            Checks the compliance of the superuser login, and also checks the presence of the status and user in the
            database. If all conditions are met, then the status is added to the user.

        :param login_user (str): Username of the user to whom the status is added
        :param status (str): The status to add to the user
        :return:
        """
        if login_user == 'admin':
            flash('Can`t add status to superuser!')
            return False

        if not Status.query.filter_by(status=status).first() or not User.query.filter_by(login=login_user).first():
            flash("There is no user with such a login or such status!")
            return False
        else:
            if not self.query.filter_by(status=status, user_login=login_user).first():
                status_add = StatusAssignment(status=status, user_login=login_user)
                db.session.add(status_add)
                db.session.commit()
                flash(f"User {login_user} successfully added status {status}")
                return True
            else:
                flash(f"User {login_user} already issued {status} status!")
                return False

    def delete_status_user(self, login_user: str, status: str):
        """This function removes the status from the user.

        Behavior:
            The existence of the status and user in the database is checked. If all conditions are met and the user
            has such a status, then the status is removed from him.


        Unusual behavior:
            User with role Admin (not superuser) can remove their status


        :param login_user: Username of the user to whom the status is being removed
        :param status: Status to be removed
        :return:
        """

        if not Status.query.filter_by(status=status).first() or not User.query.filter_by(login=login_user).first():
            flash("There is no user with such a login or such status!")
            return False
        else:
            available_status = self.query.filter_by(status=status, user_login=login_user).first()
            if available_status:
                db.session.delete(available_status)
                db.session.commit()
                flash(f"Status {status} successfully deleted from the user {login_user}")
                return True
            else:
                flash(f"User has {login_user} no status {status}!")
                return False


class RoleAssignment(db.Model):
    __tablename__ = 'roleassignment'

    """Class for assigning users roles
    
    role - roles from the role table
    user_login - username from the User table
    """
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), db.ForeignKey('role.role'))
    user_login = db.Column(db.String(10), db.ForeignKey('user.login'))

    def add_superuser_role(self):
        """Adds the Admin role to the superuser

        Behavior:
            If the user with the login admin does not have the Admin role, then it is added to him

        :return:
        """
        if not self.query.filter_by(user_login='admin').first():
            role_add = RoleAssignment(role="Admin", user_login='admin')
            db.session.add(role_add)
            db.session.commit()
            return True
        else:
            return False

    def add_role_user(self, login, role):
        """This function is designed to add existing roles to the user

        Behavior:
            If the role or user does not exist, then False, otherwise the role is added to the user if he does not
            already have such a role.

        :param login: username of the user to be assigned the role
        :param role: the name of the role to be assigned
        :return:
        """
        user = User.query.filter_by(login='admin').first().login
        if login == user:
            flash("You can't add a role to a superuser!")
            return False
        if not Role.query.filter_by(role=role).first() or not User.query.filter_by(login=login).first():
            flash("There is no user with such a login or such a role!")
            return False
        else:
            if not RoleAssignment.query.filter_by(role=role, user_login=login).first():
                role_add = RoleAssignment(role=role, user_login=login)
                db.session.add(role_add)
                db.session.commit()
                flash(f"User {login} added role successfully {role}")
                return True
            else:
                flash(f"User {login} already issued {role} role!")
                return False

    def delete_role_user(self, login: str, role: str):
        """This function removes the role from the user

        Behavior:
            If the role or user does not exist, then False, otherwise the role is removed from the user if he has such
            a role.
            UPD: Added checking for superuser and removing basic roles.


        :param login: the name of the user from whom the role should be removed
        :param role: the role to be removed from the user
        :return:
        """

        if login == 'admin':
            flash("The superuser cannot be deleted!")
            return False
        if role == 'User':
            flash('You cannot remove a base role from a user!')
            return False

        if not Role.query.filter_by(role=role).first() or not User.query.filter_by(login=login).first():
            flash("There is no user with such a login or such a role!")
            return False
        else:
            available_role = self.query.filter_by(role=role, user_login=login).first()
            if available_role:
                db.session.delete(available_role)
                db.session.commit()
                flash(f"Role {role} successfully deleted from the user {login}")
                return True
            else:
                flash(f"User has {login} no role {role}!")
                return False



class Status(db.Model):
    __tablename__ = 'status'

    """Class for storing statuses
    
    status - status that can be assigned to the user
    
    Basic statuses: 
        Banned - the banned user no longer displays game accounts in the general Board
    """
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), unique=True, nullable=False)

    def show_statuses(self):
        """This function shows all possible statuses

        Behavior:
            Displays all statuses by request and adds them to the list.

        :return:
        """
        statuses = self.query.all()
        content = []
        for item in statuses:
            content.append(item.status)
        return content

    def add_standart_statuses(self):
        """This function adds standard statuses

        Behavior:
            If the Banned status is not in the list, then it adds it.

        :return:
        """
        statuses = ['Banned']
        for item in statuses:
            if not self.query.filter_by(status=item).first():
                status = Status(status=item)
                db.session.add(status)
                db.session.commit()
            else:
                return False
        return True

    def create_status(self, status_name: str):
        """This function creates a new status

        Behavior:
            If there is no added status in the table, then it adds it.

        :param status_name (str): the name of the status to be created
        :return:
        """
        if not self.query.filter_by(status=status_name).first():
            status = Status(status=status_name)
            db.session.add(status)
            db.session.commit()
            flash(f'Status {status_name} successfully created!')
            return True
        else:
            flash(f'Status {status_name} already exists!')
            return False

    def delete_status(self, status: str):
        """This function removes the existing status

        Behavior:
            If it is not a basic status and the status exists in the table, then it deletes it.

        :param status (str): The name of the status to be removed
        :return:
        """
        statuses = ['Banned']
        for item in statuses:
            if status == item:
                flash("Basic statuses cannot be deleted!")
                return False
        status_for_delete = self.query.filter_by(status=status).first()
        if status_for_delete:
            db.session.delete(status_for_delete)
            db.session.commit()
            flash(f'Status {status} successfully deleted!')
            return True
        else:
            flash(f'Status {status} does not exist!')
            return False




class Role(db.Model):
    __tablename__ = 'role'

    """Class for storing User roles
    
    id - role numbering
    role - a role that can be assigned to a user
    """
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), unique=True, nullable=False)

    def show_roles(self):
        """Method for viewing all roles

        Behavior:
            Displays all the roles in the database as a query and returns a list of roles.

        :return:
        """
        roles = self.query.all()
        content = []
        for item in roles:
            content.append(item.role)
        return content

    def add_standart_role(self):
        """Method for adding standard roles (User, Admin)

        Behavior:
            Если ролей User и Admin не существует, то True, а иначе False.

        :return:
        """
        roles = ['User', 'Admin']
        for item in roles:
            if not self.query.filter_by(role=item).first():
                role = Role(role=item)
                db.session.add(role)
                db.session.commit()
            else:
                return False
        return True

    def create_role(self, role: str):
        """Method for adding custom roles

        Behavior:
            Accepts the role that the user (admin) wants to create and if it does not exist, then True, otherwise
            False.

        :param role (str): the name of the role to be created
        :return:
        """
        if not self.query.filter_by(role=role).first():
            new_role = Role(role=role)
            db.session.add(new_role)
            db.session.commit()
            flash("The role was created successfully!")
            return True
        else:
            flash("The role already exists!")
            return False

    def delete_role(self, role: str):
        """Method for removing custom roles

        Behavior
            If the role is == User or Admin, then this role cannot be removed. Also, you cannot delete a non-existent
            role.

        :param role (str): the name of the role to be removed
        :return:
        """
        roles = ['User', 'Admin']
        for item in roles:
            if role == item:
                flash("Basic roles cannot be removed!")
                return False
        if self.query.filter_by(role=role).first():
            role_for_delete = self.query.filter_by(role=role).first()
            db.session.delete(role_for_delete)
            db.session.commit()
            return True
        else:
            flash("There is no such role!")
            return False


class GameAccount(db.Model):
    __tablename__ = 'gameaccount'

    """Class for storing game accounts owned by User.
    
    id - numbering of records.
    name - account name (str).
    garaunteed_roll - availability of guaranteed rolls (str).
    Accepted values:
           (Yes (default) - available, No - not available).
    
    status_code - account state (str).
    Accepted values:
           (SOLD - sold, SELLING (default) - sold, PROCESSED - pending).
    
    price - account price (float).
    rate -account rating (float).
    user_owner - account owner (str), link to User table (user.login).
    created_at - time when the account was created.
    
    hero_game_content - heroes stored on the account (link to the ContentHeroGameAccount table).
    artifact_game_content - artifacts stored on the account (link to the ContentArtifactGameAccount table).
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False)
    garaunteed_roll = db.Column(db.String(3), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, default=0.0, nullable=False)
    status_code = db.Column(db.String(9), nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    user_owner = db.Column(db.String(10), db.ForeignKey('user.login'))

    hero_game_content = db.relationship("ContentHeroGameAccount", backref="herogamecontent", lazy="dynamic")
    artifact_game_content = db.relationship("ContentArtifactGameAccount", backref="artifactgamecontent", lazy="dynamic")

    def create(self, name: str, garaunteed_roll: str, price: int, user_owner: str, status_code: str = "SELLING"):
        """Creates a game account.

        Behavior:
            This function checks the length of the account name (name), as well as the existence of an equivalent
            name in the database. If all conditions are met, the entry is added.

        :param name (str): name of the game account
        :param garaunteed_roll (str): availability of guaranteed rolls
        :param price (int): game account price
        :param user_owner (str): game account owner
        :param status_code (str): game account state (default - SELLING)
        :return boolean -> True:
        """

        if self._check_len_name(name):
            user = User.query.filter_by(email=user_owner).first()
            gameaccount = self.query.filter_by(user_owner=user.login, name=name).first()
            if gameaccount:
                flash(f"Name {name} already exists!")
            else:
                create_gameaccount = GameAccount(name=name, garaunteed_roll=garaunteed_roll, price=price,
                                                 status_code=status_code, user_owner=user.login)
                db.session.add(create_gameaccount)
                db.session.commit()
                return True
        else:
            raise InvalidNumberCharacters("Invalid number of characters!")

    def show_gameaccount_by_owner(self, user_owner):
        """Returns a list (dict) of all game accounts belonging to user.

        Behavior:
            The request displays all game accounts owned by user. An empty content list and two empty heroes_content
            lists, artifacts_content, are created inside the for loop. Name, user_owner, garaunteed_roll, price,
            status_code, created_at, rate are entered into the empty content list by the gameaccount [i] element. The
            heroes_content, artifacts_content lists are created inside the loop so that they are rewritten on every i
            element. Otherwise, there may be a bug with the display of heroes and artifacts on the game account.

            UPD: Added additional loops that generate paths to hero pictures. If no such path exists, then the standard
            path is used.

        :param user_owner (str): own the game account that needs to be shown
        :return list(dict):
        """

        gameaccount = self.query.filter_by(user_owner=user_owner).all()
        content = []
        for i in range(len(gameaccount)):
            heroes_content, artifacts_content, path_img_hero, path_img_artifact = [], [], [], []
            heroes = gameaccount[i].hero_game_content.all()
            artifacts = gameaccount[i].artifact_game_content.all()
            for j in range(len(heroes)):
                heroes_content.append(heroes[j].hero.replace("_", " "))
                if os.path.exists(f'static/img/faces/{heroes[j].hero}.jpg'):
                    path_img_hero.append(f'/static/img/faces/{heroes[j].hero}.jpg')
                else:
                    path_img_hero.append(f'/static/img/faces/missing.jpg')
            for k in range(len(artifacts)):
                artifacts_content.append(artifacts[k].artifact.replace("_", " "))
                if os.path.exists(f'static/img/faces/{artifacts[k].artifact}.jpg'):
                    path_img_artifact.append(f'/static/img/faces/{artifacts[k].artifact}.jpg')
                else:
                    path_img_artifact.append(f'/static/img/faces/missing.jpg')
            gameaccount_info = {
                "name": gameaccount[i].name,
                "user_owner": gameaccount[i].user_owner,
                "heroes": heroes_content,
                "path_img_hero": path_img_hero,
                "artifacts": artifacts_content,
                "path_img_artifact": path_img_artifact,
                "garaunteed_roll": gameaccount[i].garaunteed_roll,
                "created_at": gameaccount[i].created_at,
                "rate": gameaccount[i].rate,
                "price": gameaccount[i].price,
                "status_code": gameaccount[i].status_code
            }
            content.append(gameaccount_info)
        return content

    def show_gameaccount_by_name(self, user_owner, name):
        """Returns information about the game account of the proper user, and information about the heroes and
        artifacts available on the account.

        Behavior:
            The request displays the account (user_owner - unique, name - unique) owned by user. Creates three empty
            lists (content, heroes, artifacts). The gameaccount_info contains field values (except for
            hero_game_content, artifact_game_content) of the GameAccount table.

            The values of the Hero and Artifact tables are written to the heroes_content, artifacts_content
            lists with separate for loops (different len () may be), after comparing whether this character is
            on this account in the ContentHeroGameAccount and ContentArtifactGameAccount table. Further, the resulting
            filled lists are assigned to the gameaccount_info dictionary. The content sheet, in turn, is filled with the
            gameaccount_info dictionaries.

        :param user_owner (str): the owner of the game account, which must be shown
        :param name (str): the name of the game account you want to show
        :return list(dict):
        """

        gameaccount = self.query.filter_by(user_owner=user_owner, name=name).first()
        content, heroes_content, artifacts_content = [], [], []
        heroes = gameaccount.hero_game_content.all()
        artifacts = gameaccount.artifact_game_content.all()
        parse_heroes = Hero.query.filter_by().all()
        parse_artifacts = Artifact.query.filter_by().all()
        for j in range(len(heroes)):
            for hero in parse_heroes:
                if hero.name == heroes[j].hero:
                    full_hero_info = {
                        "name": hero.name,
                        "star": hero.star,
                        "rate": hero.rate,
                        "added": heroes[j].created_at
                    }
                    heroes_content.append(full_hero_info)
        for k in range(len(artifacts)):
            for artifact in parse_artifacts:
                if artifact.name == artifacts[k].artifact:
                    full_artifact_info = {
                        "name": artifact.name,
                        "star": artifact.star,
                        "added": artifacts[k].created_at
                    }
                    artifacts_content.append(full_artifact_info)
        gameaccount_info = {
            "name": gameaccount.name,
            "user_owner": gameaccount.user_owner,
            "heroes": heroes_content,
            "artifacts": artifacts_content,
            "garaunteed_roll": gameaccount.garaunteed_roll,
            "created_at": gameaccount.created_at,
            "rate": gameaccount.rate,
            "price": gameaccount.price,
            "status_code": gameaccount.status_code
        }
        content.append(gameaccount_info)
        return content

    def show_gameaccount_all(self):
        """Returns information about all game accounts.

        Behavior
            Displays all game accounts as a request. An empty content list and two empty heroes_content lists,
            artifacts_content, are created inside the for loop. Name, user_owner, garaunteed_roll, price, status_code
            are entered into the empty content list by the gameaccount [i] element.

            The heroes_content, artifacts_content lists are created inside the loop so that they are rewritten on
            every i element. Otherwise, there may be a bug with displaying heroes and artifacts on the game account

            UPD: Added additional loops that generate paths to hero pictures. If no such path exists, then the standard
            path is used.

        :return list(dict):
        """

        gameaccount = self.query.all()
        content = []
        for i in range(len(gameaccount)):
            status = StatusAssignment.query.filter_by(user_login=gameaccount[i].user_owner).first()
            if not status:
                status = None
            else:
                status = status.status
            if gameaccount[i].rate >= 1 and gameaccount[i].status_code != 'SOLD' and status != 'Banned' and \
                    gameaccount[i].status_code != 'PROCESSED':
                # 1 - the rating from which all accounts should be shown
                heroes_content, artifacts_content, path_img_hero, path_img_artifact = [], [], [], []
                user = User.query.filter_by(login=gameaccount[i].user_owner).first()
                heroes = gameaccount[i].hero_game_content.all()
                artifacts = gameaccount[i].artifact_game_content.all()
                for j in range(len(heroes)):
                    heroes_content.append(heroes[j].hero.replace("_", " "))
                    if os.path.exists(f'static/img/faces/{heroes[j].hero}.jpg'):
                        path_img_hero.append(f'/static/img/faces/{heroes[j].hero}.jpg')
                    else:
                        path_img_hero.append(f'/static/img/faces/missing.jpg')
                for k in range(len(artifacts)):
                    artifacts_content.append(artifacts[k].artifact.replace("_", " "))
                    if os.path.exists(f'static/img/faces/{artifacts[k].artifact}.jpg'):
                        path_img_artifact.append(f'/static/img/faces/{artifacts[k].artifact}.jpg')
                    else:
                        path_img_artifact.append(f'/static/img/faces/missing.jpg')
                gameaccount_info = {
                    "name": gameaccount[i].name,
                    "user_owner": gameaccount[i].user_owner,
                    "discord_nickname": user.discord_nickname,
                    "heroes": heroes_content,
                    "path_img_hero": path_img_hero,
                    "artifacts": artifacts_content,
                    "path_img_artifact": path_img_artifact,
                    "garaunteed_roll": gameaccount[i].garaunteed_roll,
                    "created_at": gameaccount[i].created_at,
                    "rate": gameaccount[i].rate,
                    "price": gameaccount[i].price,
                    "status_code": gameaccount[i].status_code
                }
                content.append(gameaccount_info)
        return content

    def delete(self, user_owner, name):
        """Deletes the game account (GameAccount).

        Behavior:
            The request displays the account (name - unique) belonging to user_owner (user_owner - unique). If a record
            exists in the table, then True, otherwise False.

        :param user_owner (str): the owner of the game account to be deleted
        :param name (str): the name of the game account to be deleted
        :return boolean -> True:
        """

        gameaccount = self.query.filter_by(user_owner=user_owner, name=name).first()
        if gameaccount:
            db.session.delete(gameaccount)
            db.session.commit()
            return True
        else:
            False

    def change_settings(self, user_owner: str, name: str, garaunteed_roll: str,
                        price: int, status_code: str):
        """Changes the parameters of the game account.

        Behavior
            Checks len() and the existence of a new game account name in the table, and the existence of a new name in
            the GameAccount table.

            If all conditions are met, then the data from the ContentHeroGameAccount and ContentArtifactGameAccount
            tables is assigned a GameAccount named name.

        :param user_owner (str): account owner
        :param name (str): account name
        :param garaunteed_roll (str): availability of a guaranteed roll
        :param price (int): game account price
        :param status_code (str): game account state
        :return boolean -> True:
        """

        gameaccount = self.query.filter_by(user_owner=user_owner, name=name).first()
        if gameaccount:
            gameaccount.price = price
            gameaccount.status_code = status_code
            gameaccount.garaunteed_roll = garaunteed_roll
            db.session.commit()
            return True
        else:
            return False

    @staticmethod
    def _check_len_name(name: str):
        """Checking the length of the string.

        Behavior:
            If the string length is greater than 10 or less than 2, then False, otherwise True.

        :param name (str):
        :return boolean:
        """

        if len(name) > 10 or len(name) < 2:
            return False
        return True

    def __repr__(self):
        return f"{self.id}:{self.name}:{self.user_owner}:{self.garaunteed_roll}:" \
               f"{self.price}:{self.status_code}"


class ContentHeroGameAccount(db.Model):
    __tablename__ = 'contentherogameaccount'

    """A class for storing characters bound to GameAccount.
    
    id - numbering of records.
    hero - hero name (str).
    name - the name of the account that the hero belongs to (link to the Game Account table) (str).
    """

    id = db.Column(db.Integer, primary_key=True)
    hero = db.Column(db.String(30), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    name = db.Column(db.String(5), db.ForeignKey('gameaccount.name'))

    def add_card(self, name_game_account: str, heroes: list):
        """Adding a hero to GameAccount.

        Behavior:
            Iterates through all the items in the heroes list and adds each item to the ContentHeroGameAccount table.

            If there are records: calls all hero records from the ContentHeroGameAccount table by name and all heroes
            from the Hero table. Next, using the calculate_game_account_rate function, it calculates the account's
            rating.
            If there are no entries: assigns a rating of 0 to the game account.

        :param name_game_account (str): the name of the game account to add heroes to
        :param heroes (list): list of heroes to add
        :return boolean:
        """

        for item in heroes:
            contentgameaccount = ContentHeroGameAccount(name=name_game_account, hero=item)
            db.session.add(contentgameaccount)
            db.session.commit()

        heroes = self.query.filter_by(name=name_game_account).all()
        if heroes:
            parse_heroes = Hero.query.filter_by().all()

            rate = calculate_game_account_rate(heroes=heroes, parse_heroes=parse_heroes)
            gameaccount = GameAccount.query.filter_by(name=name_game_account).first()
            gameaccount.rate = rate
            db.session.commit()
        else:
            gameaccount = GameAccount.query.filter_by(name=name_game_account).first()
            gameaccount.rate = 0
            db.session.commit()

        return True

    def delete_card(self, name_game_account: str, heroes: list):
        """Removes a hero from GameAccount.

        Behavior:
            It iterates over all items in heroes and makes a request for name_game_account and item.

            If there are records: calls all hero records from the ContentHeroGameAccount table by name and all heroes
            from the Hero table. Next, using the calculate_game_account_rate function, it calculates the account's
            rating.
            If there are no entries: assigns a rating of 0 to the game account.

        :param name_game_account (str): the name of the game account from which heroes need to be deleted
        :param heroes (list): list of heroes to be removed
        :return boolean:
        """
        for item in heroes:
            contentgameaccount = self.query.filter_by(name=name_game_account, hero=item).first()
            db.session.delete(contentgameaccount)
            db.session.commit()

        heroes = self.query.filter_by(name=name_game_account).all()
        if heroes:
            parse_heroes = Hero.query.filter_by().all()

            rate = calculate_game_account_rate(heroes=heroes, parse_heroes=parse_heroes)
            gameaccount = GameAccount.query.filter_by(name=name_game_account).first()
            gameaccount.rate = rate
            db.session.commit()
        else:
            gameaccount = GameAccount.query.filter_by(name=name_game_account).first()
            gameaccount.rate = 0
            db.session.commit()

        return True

    def __repr__(self):
        return f"{self.id}:{self.hero}:{self.name}"


class ContentArtifactGameAccount(db.Model):
    __tablename__ = 'contentartifactgameaccount'

    """This class stores artifacts belonging to the Game account.
    
    id - numbering of records.
    artifact - the name of the artifact.
    
    name - the name of the account that owns the artifact (link to the Game Account table) (str).
    
    """

    id = db.Column(db.Integer, primary_key=True)
    artifact = db.Column(db.String(50), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)

    name = db.Column(db.String(5), db.ForeignKey('gameaccount.name'))

    def add_card(self, name_game_account: str, artifacts: list):
        """Adding an artifact to GameAccount.

        Behavior:
            Iterates through all the items in the artifacts list and adds each item to the ContentArtifactGameAccount
            table.

        :param name_game_account (str): the name of the account to which you want to add artifacts
        :param artifacts (list): list of user marked artifacts
        :return boolean:
        """
        for item in artifacts:
            contentgameaccount = ContentArtifactGameAccount(name=name_game_account, artifact=item)
            db.session.add(contentgameaccount)
            db.session.commit()
        return True

    def delete_card(self, name_game_account: str, artifacts: list):
        """Removes the artifact from the GameAccount.

        Behavior:
                It iterates over all items in artifacts and makes a request for name_game_account and item. After that,
                it deletes the entry and returns True.

        :param name_game_account (str): the name of the game account from which you want to remove artifacts
        :param artifacts (list): list of user marked artifacts
        :return boolean:
        """
        for item in artifacts:
            contentgameaccount = self.query.filter_by(name=name_game_account, artifact=item).first()
            db.session.delete(contentgameaccount)
            db.session.commit()
        return True

    def __repr__(self):
        return f"{self.id}:{self.artifact}Ж{self.name}"


class Hero(db.Model):
    __tablename__ = 'hero'

    """This class stores all possible heroes
    
    id - column numbering
    name - character name (str)
    star - the number of stars the character has (int)
    rate - average character rating (float)
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    star = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)

    def show_hero_without_img(self):
        """Shows heroes who have no image

        :return:
        """
        all_heroes = self.query.all()
        content = []
        for item in all_heroes:
            if not os.path.exists(f'static/img/faces/{item.name}.jpg'):
                hero_without_img = {
                    'name': item.name,
                    'star': item.star,
                    'rate': item.rate
                }
                content.append(hero_without_img)
        return content

    def add_hero_from_json(self):
        """Adds heroes from json

        Behavior:
            Loads information from json. If such a hero does not exist in the table, then add it.

        :return boolean:
        """
        with open('static/data/heroes_data/heroes.json', 'r', encoding='utf-8') as fh:
            result = json.load(fh)
        for i in range(len(result['name'])):
            hero = self.query.filter_by(name=result['name'][i]).first()
            if not hero:
                hero_add = Hero(name=result['name'][i], star=result['star'][i], rate=result['rate'][i])
                db.session.add(hero_add)
                db.session.commit()
        return True

    def create_hero(self, user_login, name_hero: str, stars_hero: int, rate_hero: float):
        """Adds a hero

        Behavior:
                If the user does not have the Admin role, then False. If the hero name already exists, then False.
                If all the conditions are met, a new hero is added.

        :param user: an object of such a user who wants to add a hero
        :param name_hero: the name of the hero to add
        :param stars_hero: the number of stars the hero has
        :param rate_hero: hero rating
        :return:
        """
        user = User.query.filter_by(login=user_login).first()
        if user.role.filter_by(role='Admin').first():
            if not self.query.filter_by(name=name_hero).first():
                hero = Hero(name=name_hero, star=stars_hero, rate=rate_hero)
                db.session.add(hero)
                db.session.commit()
                return True
            else:
                flash("Such an hero already exists!")
                return False
        else:
            flash("You are not an administrator!")
            return False


    def show_all_heroes(self):
        """Returns a list with information about all heroes

        Behavior:
            Adds all information about all heroes to the list.

        :return list:
        """
        heroes = self.query.all()
        content = []
        for i in range(len(heroes)):
            result = {
                "name": heroes[i].name,
                "star": heroes[i].star,
                "rate": heroes[i].rate
            }
            content.append(result)
        return content

    def __repr__(self):
        return f"{self.name}:{self.star}:{self.rate}"


class Artifact(db.Model):
    __tablename__ = 'artifact'
    """This class stores all possible artifacts.
    
        id - column numbering
        name - artifact name (all artifact names are loaded using a parser)
        star - the number of stars the artifact has (4 or 5 stars)
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    star = db.Column(db.Integer, nullable=False)

    def show_artifacts_without_img(self):
        all_artifacts = self.query.all()
        content = []
        for item in all_artifacts:
            if not os.path.exists(f'static/img/faces/{item.name}.jpg'):
                artifact_without_img = {
                    'name': item.name,
                    'star': item.star
                }
                content.append(artifact_without_img)
        return content

    def add_artifact_from_json(self):
        """Adds artifact from json

         Behavior:
            Loads information from json. If such a artifact does not exist in the table, then add it.

        :return boolean:
        """
        with open('static/data/artifacts_data/artifacts.json', 'r', encoding='utf-8') as fh:
            result = json.load(fh)
        for i in range(len(result['name'])):
            artifact = self.query.filter_by(name=result['name'][i]).first()
            if not artifact:
                artifact_add = Artifact(name=result['name'][i], star=result['star'][i])
                db.session.add(artifact_add)
                db.session.commit()
        return True

    def create_artifact(self, user_login, name_artifact: str, stars_artifact: int):
        """Adds an artifact

        Behavior
                If the user does not have the Admin role, then False. If the artifact name already exists, then False.
                If all conditions are met, a new artifact is added.

        :param user_login: an object of such a user who wants to add a new artifact
        :param name_artifact: artifact name
        :param stars_artifact: the number of stars the artifact has
        :return:
        """
        user = User.query.filter_by(login=user_login).first()
        if user.role.filter_by(role='Admin'):
            if not self.query.filter_by(name=name_artifact).first():
                artifact = Artifact(name=name_artifact, star=stars_artifact)
                db.session.add(artifact)
                db.session.commit()
                return True
            else:
                flash("Such an artifact already exists!")
                return False
        else:
            flash("You are not an administrator!")
            return False

    def show_all_artifacts(self):
        """Returns information about all artifacts

        Behavior:
            Adds all information about all artifacts to list.

        :return list:
        """
        artifacts = self.query.all()
        content = []
        for i in range(len(artifacts)):
            result = {
                "name": artifacts[i].name,
                "star": artifacts[i].star
            }
            content.append(result)
        return content

    def __repr__(self):
        return f"{self.name}:{self.star}"


db.create_all()


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
