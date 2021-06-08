from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#used to serialize outgoing data
resource_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'section': fields.String,
    'modifiers': fields.String,
}

sections_enum = {
    0: "Lunch",
    1: "Dinner"
}

#table for the menuitems
class MenuItemsModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(100), nullable=False)
    modifiers = db.Column(db.String(100), nullable=True)

#database reset
db.drop_all()
db.create_all()

#gets the arguments sent with the request
item_args = reqparse.RequestParser()
item_args.add_argument("title", type=str, help="Title of item is needed", required=True)
item_args.add_argument("section", type=str, help="Section not specified", required=True, action='append')
item_args.add_argument("modifiers", type=str, help="No modifiers", action='append')

#the routed requests for the items come into this class
class Item(Resource):
    #method gets the item by id
    @marshal_with(resource_fields) #take values and serialize
    def get(self, item_id):
        result = {}
        if item_id:
            result = MenuItemsModel.query.filter_by(id=item_id).first()
            
        if not result:
            abort(409, message="item not found")

        return result, 200
    
    #method overload for getting all items
    def get(self):
        result = MenuItemsModel.query.first()
        if not result:
            abort(409, message="no items in database")

        result = self.parseItemsResult()

        return result, 200

    #enters an entry into db
    @marshal_with(resource_fields)
    def put(self, item_id):
        args = item_args.parse_args()
        result = MenuItemsModel.query.filter_by(id=item_id).first()
        if result:
            abort(409, message="id taken")

        item = MenuItemsModel(id=item_id, title=args['title'], section=json.dumps(args['section']), modifiers=json.dumps(args['modifiers']))

        db.session.add(item)
        db.session.commit()

        return item, 201

    #updates existing entry with given fields
    @marshal_with(resource_fields)
    def patch(self, item_id):
        args = item_args.parse_args()
        result = MenuItemsModel.query.filter_by(id=item_id).first()
        if not result:
            abort(404, message=f"Could not update {item_id}")

        if args['title']:
            result.title = args['title']
        if args['section']:
            result.section = json.dumps(args['section'])
        if args['modifiers']:
            result.modifiers = json.dumps(args['modifiers'])

        db.session.commit()

        return result, 200

    #deletes item with given id or aborts if not existant
    def delete(self, item_id):
        result = MenuItemsModel.query.filter_by(id=item_id).first()

        if not result:
            abort(404, message="id not existing")

        db.session.delete(result)
        db.session.commit()

        result = MenuItemsModel.query.filter_by(id=item_id).first()

        if result:
            abort(404, message="Was not able to delete")

        return {"status": "success"}, 200

    # gets entries from db and constructs a json with the correct format
    def parseItemsResult(self):
        menu = []

        for s in sections_enum:
            section_type = sections_enum.get(s)
            result = MenuItemsModel.query.filter(MenuItemsModel.section.contains(section_type))
            menu.append({"id": len(menu) + 1, "title": f"{section_type} Specials", "items": []})
            item_id = 1

            for item in result:
                menu_item_dict = self.createItemObject(item, item_id)
                menu[len(menu) - 1].get("items").append(menu_item_dict)
                item_id += 1


        return json.dumps(menu)

    #helper method for parsing items
    def createItemObject(self, item, id):
        obj = {"id": id, "title": item.title, "modifiers": []}

        mod_id = 1
        for mod in json.loads(item.modifiers):
            obj["modifiers"].append({"id": mod_id, "title": mod})
            mod_id += 1

        return obj


#where the routing is matched from the requests
api.add_resource(Item, "/item", "/item/<int:item_id>")

#run on debug=False for prod.
if __name__ == "__main__":
    app.run(debug=True)