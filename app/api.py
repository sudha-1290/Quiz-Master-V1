from flask_restful import Api, Resource, reqparse
from app.models.subject import Subject
from app.extensions import db

api = Api()

class SubjectAPI(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True)
        self.parser.add_argument('description', type=str)

    def get(self, subject_id=None):
        if subject_id:
            subject = Subject.query.get_or_404(subject_id)
            return {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description
            }
        subjects = Subject.query.all()
        return [{
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        } for subject in subjects]

    def post(self):
        args = self.parser.parse_args()
        subject = Subject(name=args['name'], description=args['description'])
        db.session.add(subject)
        db.session.commit()
        return {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        }, 201

    def put(self, subject_id):
        args = self.parser.parse_args()
        subject = Subject.query.get_or_404(subject_id)
        subject.name = args['name']
        subject.description = args['description']
        db.session.commit()
        return {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description
        }

    def delete(self, subject_id):
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return '', 204 