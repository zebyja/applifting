from ms import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), index=True)
    description = db.Column(db.String(), index=True)

    def __repr__(self):
        return '<Product id: {}, name: {}, description: {}>'.format(self.id, self.name, self.description)


class Offer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prod_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    remote_id = db.Column(db.Integer)  # for keeping offers dedudiplicated
    price = db.Column(db.Integer)
    items_in_stock = db.Column(db.Integer)

    def __repr__(self):
        return '<Offer id: {}, prod_id: {}, remote_id: {}, price: {}, items_in_stock: {}'.format(
            self.id, self.prod_id, self.remote_id, self.price, self.items_in_stock)


class Settings(db.Model):
    name = db.Column(db.String, primary_key=True)
    value = db.Column(db.String)

    def __repr__(self):
        return '<Setting name: {}, value: {}'.format(self.name, self.value)
