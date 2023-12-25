from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

assoc_purchases_item = db.Table(
    "association_purchases_items",
    db.Column("purchase_id", db.Integer, db.ForeignKey("purchase.id")),
    db.Column("item_id", db.Integer, db.ForeignKey("item.id"))
)

class User(db.Model):
    """
    User model
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    purchases = db.relationship("Purchase", cascade = "delete")

    def __init__(self, **kwargs):
        """
        Initialize a user object
        """

        self.username = kwargs.get("username", "")
        self.password = kwargs.get("password", "")

class Purchase(db.Model):
    """
    Purchase model
    """

    __tablename__ = "purchase"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    amount = db.Column(db.Integer, nullable = False)
    date = db.Column(db.DateTime, nullable = False)
    items = db.relationship("Item", secondary = assoc_purchases_item, back_populates = "purchases")

    def __init__(self, **kwargs):
        """
        Initialize a purchase object
        """

        #TODO


class Item(db.Model):
    """
    Item model
    """

    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    name = db.Column(db.String, nullable = False)
    purchases = db.relationship("Purchase", secondary = assoc_purchases_item, back_populates = "items")