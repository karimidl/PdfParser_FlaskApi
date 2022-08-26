from flask import Flask, flash, request, redirect, url_for, session, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from tika import parser
from werkzeug.utils import secure_filename
from utilities.ts_vector import TSVector
from sqlalchemy import Index
import os
import secrets
import urllib.request
secret = secrets.token_urlsafe(32)



UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:master@2022@localhost/myDb'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = secret
db = SQLAlchemy(app)

def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class DocumentModel(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    content = db.Column(db.UnicodeText, nullable=False)

    # __ts_vector__ = db.Column(TSVector(), db.Computed(
    #     "to_tsvector('english', title || ' ' || description)",
    #     persisted=True))
    # __table_args__ = (Index('ix_video___ts_vector__',
    #                         __ts_vector__, postgresql_using='gin'),)

    def __repr__(self):
        return f"Document(name = {self.name}, description = {self.content})"

document_put_args = reqparse.RequestParser()
document_put_args.add_argument("id", type=int, help="name of the document is required", required=True)

document_put_args.add_argument("name", type=str, help="name of the document is required", required=True)
document_put_args.add_argument("content", type=str, help="desc of the document is required", required=True)
# document_update_args = reqparse.RequestParser()
# document_update_args.add_argument("name", type=str, help="Name of the document is required")
# document_update_args.add_argument("description", type=str, help="Description of the document")

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'content': fields.String,
}

class Document(Resource):
    # @marshal_with(resource_fields)
    # def get(self, document_id):
    # 	result = DocumentModel.query.filter_by(id=document_id).first()
    # 	if not result:
    # 		abort(404, message="Could not find document with that id")
    # 	return result

    # @marshal_with(resource_fields)
    # def get(self, document_id):
    # 	result = DocumentModel.query.filter(DocumentModel.__ts_vector__.match(document_id)).all()
    # 	if not result:
    # 		abort(404, message="Could not find document with that id")
    # 	return result

    
    @app.route('/search/<string:key_word>', methods=['GET'])
    @marshal_with(resource_fields)
    def get(self, key_word):
        # documentModel = DocumentModel()
        result = DocumentModel.query.filter(DocumentModel.__ts_vector__.match(key_word)).all()
        if not result:
            abort(404, message="Could not find document with that text")
        return result
    
    @app.route('/document', methods = ['POST'])
    @marshal_with(resource_fields)
    def put():
        args = document_put_args.parse_args()
        
        parsed = parser.from_file(args['url'])
        document = DocumentModel(id, name=parsed["metadata"].get("resourceName"), content=parsed["content"])
        
        db.session.add(document)
        db.session.commit()
        return document, 201

    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        print(request.files)
        if 'files[]' not in request.files:
            print(request.files)

            resp = jsonify({'message' : 'No file part in the request'})
            resp.status_code = 400
            return resp
    
        files = request.files.getlist('files[]')
        
        
        errors = {}
        success = False
        
        for file in files:      
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                parsed = parser.from_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                document = DocumentModel(name=parsed["metadata"].get("resourceName"), content=parsed["content"])
                db.session.add(document)
                db.session.commit()
                success = True
            else:
                errors[file.filename] = 'File type is not allowed'
    
        if success and errors:
            
            
            errors['message'] = 'File(s) successfully uploaded'
            return jsonify(errors),500
            
        if success:
            
            return jsonify({'message' : 'Files successfully uploaded'}),201
            
        else:
            return jsonify(errors),500


















    # @app.route('/upload', methods=['GET', 'POST'])
    # def upload_file():
    #     if request.method == 'POST':
    #         # check if the post request has the file part
    #         if 'file' not in request.files:
    #             flash('No file part')
    #             return redirect(request.url)
    #         file = request.files['file']
    #         # if user does not select file, browser also
    #         # submit an empty part without filename
    #         if file.filename == '':
    #             flash('No selected file')
    #             return redirect(request.url)
    #         if file and allowed_file(file.filename):
    #             filename = secure_filename(file.filename)
    #             file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #             return redirect(url_for('uploaded_file',filename=filename))
    #     return "'''"
    # @app.route("/document/<int:document_id>", methods = ["PATCH"])
    # @marshal_with(resource_fields)
    # def patch(self, document_id):
    #     args = document_update_args.parse_args()
    #     result = DocumentModel.query.filter_by(id=document_id).first()
    #     if not result:
    #         abort(404, message="Document doesn't exist, cannot update")

    #     if args['name']:
    #         result.name = args['name']
    #     if args['description']:
    #         result.description = args['description']

    #     db.session.commit()

    #     return result


api.add_resource(Document, "/document/search/<string:key_word>")
# api.add_resource(Document, "/document/<string:document_id>")

if __name__ == "__main__":
    app.run(debug=True)