from models.user import User

class UserDAO:

    def get_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_by_id(self, user_id):
        return User.query.get(user_id)

    def get_all(self):
        return User.query.all()

    def save(self, user):
        from config.database import db
        db.session.add(user)
        db.session.commit()
        return user

    def delete(self, user):
        from config.database import db
        db.session.delete(user)
        db.session.commit()
