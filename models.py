from peewee import *
import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('social.db')

class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(Post.user == self) 

    def following(self):
        return (
            User.select().join(
                RelationShip, on=RelationShip.to_user
            ).where(
                RelationShip.from_user == self
            )
        )
    def followers(self):
        return (
            User.select().join(
                RelationShip, on=RelationShip.from_user
            ).where(
                RelationShip.to_user == self
            )
        )

     
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin)
        except IntegrityError:
            raise ValueError("User already exists")    


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        User,
        related_name='posts'
    )
    content = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


class RelationShip(Model):
    from_user = ForeignKeyField(User, related_name='relationships')
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        indexes = ((('from_user', 'to_user'), True),)





def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, RelationShip], safe=True)
    DATABASE.close() 