from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

assoc_purchases_item = db.Table(
    "association_purchases_items",
    db.Column("purchase_id", db.Integer, db.ForeignKey("purchase.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("item.id"))
)


class User(UserMixin, db.Model):
    """
    User model
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    purchases = db.relationship("Purchase", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize a user object
        """

        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")

    def serialize(self):
        """
        Serialize a user object
        """

        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "purchases": [purchase.serialize() for purchase in self.purchases]
        }


class Purchase(db.Model):
    """
    Purchase model
    """

    __tablename__ = "purchase"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    items = db.relationship(
        "Item", secondary=assoc_purchases_item, back_populates="purchases")

    def __init__(self, **kwargs):
        """
        Initialize a purchase object
        """

        self.amount = kwargs.get("amount", 0)
        self.date = kwargs.get("date")
        self.type = kwargs.get("type", "uncategorized")
        self.user_id = kwargs.get("user_id", 1)

    def serialize(self):
        """
        Serialize a purchase object
        """

        return {
            "id": self.id,
            "amount": self.amount,
            "date": self.date,
            "type": self.type,
            "user_id": self.user_id,
            "items": [item.serialize() for item in self.items]
        }

    def simple_serialize(self):
        """
        Serialize a purchase object without items
        """

        return {
            "id": self.id,
            "amount": self.amount,
            "date": self.date,
            "type": self.type,
        }


class Item(db.Model):
    """
    Item model
    """

    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    purchases = db.relationship(
        "Purchase", secondary=assoc_purchases_item, back_populates="items")

    def __init__(self, **kwargs):
        """
        Initialize an item object
        """

        self.name = kwargs.get("name", "")

    def serialize(self):
        """
        Serialize an item object
        """

        return {
            "id": self.id,
            "name": self.name,
            "purchases": [purchase.simple_serialize() for purchase in self.purchases]
        }
