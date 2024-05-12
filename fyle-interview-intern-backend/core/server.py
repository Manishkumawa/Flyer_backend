from flask import jsonify ,request 
from marshmallow.exceptions import ValidationError
from core import app
from sqlalchemy import and_
from core.apis.assignments import student_assignments_resources, teacher_assignments_resources
from core.libs import helpers
from flask_sqlalchemy import SQLAlchemy

from core.libs.exceptions import FyleError
from werkzeug.exceptions import HTTPException
import datetime
from sqlalchemy.exc import IntegrityError
from core.models.assignments import Assignment
from core.models.teachers import Teacher
from core.models.students import Student
from core.models.teachers import Teacher
from core.models.users import User
db = SQLAlchemy(app)
app.register_blueprint(student_assignments_resources, url_prefix='/student')
app.register_blueprint(teacher_assignments_resources, url_prefix='/teacher')


@app.route('/')
def ready():
    response = jsonify({
        'status': 'ready',
        'time': helpers.get_utc_now()
    })

    return response

@app.errorhandler(Exception)
def handle_error(err):
    if isinstance(err, FyleError):
        return jsonify(
            error=err.__class__.__name__, message=err.message
        ), err.status_code
    elif isinstance(err, ValidationError):
        return jsonify(
            error=err.__class__.__name__, message=err.messages
        ), 400
    elif isinstance(err, IntegrityError):
        return jsonify(
            error=err.__class__.__name__, message=str(err.orig)
        ), 400
    elif isinstance(err, HTTPException):
        return jsonify(
            error=err.__class__.__name__, message=str(err)
        ), err.code

    raise err

@app.route('/student/assignments/',methods =['GET'])
def get_student_assignments():
    auth_header = request.headers.get('X-Principal')
    student_id = auth_header.get('student_id')
    user_id = auth_header.get('user_id')
    student_assignments = Assignment.get_assignments_by_student(student_id)
    result = []
    for  assignment in student_assignments:
        temp ={
            "content": assignment.content,
            "created_at": assignment.created_at,
            "grade": assignment.grade,
            "id": assignment.id,
            "state": assignment.state,
            "student_id": assignment.student_id,
            "teacher_id": assignment.teacher_id,
            "updated_at": assignment.updated_at
        }
        result.append(temp)
    return jsonify(result)

@app.route('/student/assignments/',methods =['POST'])
def create_assignments():
    auth_header = request.headers.get('X-Principal')
    student_id = auth_header.get('student_id')
    user_id = auth_header.get('user_id')

    data = request.get_json()
    content = data['content']

    assignment = Assignment(student_id =student_id ,content = content ,state = "DRAFT")
    db.session.commit()


    response = {
        "content": assignment.content,
        "created_at": assignment.created_at,
        "grade": assignment.grade,
        "id": assignment.id,
        "state": assignment.state,
        "student_id": assignment.student_id,
        "teacher_id": assignment.teacher_id,
        "updated_at": assignment.teacher_id

    }

    return jsonify(response)

@app.route('/student/assignments/',methods =['PATCH'])
def edit_assignments():

    auth_header = request.headers.get('X-Principal')
    student_id = auth_header.get('student_id')
    user_id = auth_header.get('user_id')

    data = request.get_json()
    id = data['id']
    content = data['content']

    assignment  =Assignment.get_by_id(id)
    assignment.content = content

    result = {
        "content":assignment.content,
        "created_at":assignment.created_at,
        "id":assignment.id,
        "grade":assignment.grade,
        "state":assignment.state,
        "student_id":assignment.student_id,
        "teacher_id":assignment.teacher_id,
        "updated_at":assignment.updated_at
    }
    return jsonify(result)

    

@app.route('/student/assignments/submit',methods =['POST'])
def submit_assignments():
    auth_header = request.headers.get('X-Principal')
    student_id = auth_header.get('student_id')
    user_id = auth_header.get('user_id')

    data  = request.get_json()
    id = data['id']
    teacher_id =data['teacher_id']

    All_data = Assignment.submit(id,teacher_id)

    data ={
       
        "content": All_data.content,
        "created_at": All_data.created_at,
        "grade": All_data.grade,
        "id": All_data.id,
        "state": All_data.state,
        "student_id": All_data.student_id,
        "teacher_id": All_data.teacher_id,
        "updated_at": All_data.updated_at
    }
    return jsonify(data)


    

@app.route('/teacher/assignments',methods =['GET'])
def get_teacher_assignements():
    auth_header = request.headers.get('X-Principal')
    teacher_id = auth_header.get('student_id')
    user_id = auth_header.get('user_id')

    all_data = Assignment.get_assignments_by_teacher(teacher_id)
    result = []
    for temp in all_data:
        data ={
            "content": temp.content,
            "created_at": temp.created_at,
            "grade": temp.grade,
            "id": temp.id,
            "state": temp.state,
            "student_id": temp.student_id,
            "teacher_id": temp.teacher_id,
            "updated_at": temp.updated_at
        }
        result.append(data)

    return result 


@app.route('/teacher/assignments/grade',methods =['POST'])
def teacher_grade():
  
    auth_header = request.headers.get('X-Principal')
    teacher_id = auth_header.get('teacher_id')
    user_id = auth_header.get('user_id')

    data = request.get_json()
    id = data['id']
    grade = data['grade']

    result = Assignment.mark_grade(id,grade)

    data = {
        "content": result.content,
        "created_at": result.created_at,
        "grade": result.grade,
        "id": result.id,
        "state": result.state,
        "student_id": result.student_id,
        "teacher_id": result.teacher_id,
        "updated_at": result.updated_at
    }

    return jsonify(data)



@app.route('/principal/assignments',methods =['GET'])
def principal_assignments():

    auth_header = request.headers.get('X-Principal')

    user_id = auth_header('user_id')
    principal_id = auth_header('principal_id')

    all_data = Assignment.query.filter(and_(Assignment.teacher_id == principal_id,
                                                             Assignment.state.in_(['SUBMITTED', 'GRADED']))).all()



    
    result =[]
    for data in all_data:
        temp ={
            "content": data.content,
            "created_at": data.created_at,
            "grade": data.grade,
            "id":data.id,
            "state": data.state,
            "student_id": data.student_id,
            "teacher_id": data.teacher_id,
            "updated_at": data.updated_at

        }
        result.append(temp)

    return result


@app.route('/principal/teachers',methods =['GET'])
def get_teachers():
    auth_header = request.headers.get('X-Principal')

    user_id = auth_header('user_id')
    principal_id = auth_header('principal_id')

    all_data = Teacher.query.all()
    result =[]
    for data in all_data:
        temp ={

            "created_at": data.created_by,
            "id": data.id,
            "updated_at": data.updated_by,
            "user_id": data.user_id

        }
        result.append(temp)

    return result 


@app.route('/principal/assignments/grade',methods =['POST','GET'])
def principal_grade():

    auth_header = request.headers.get('X-Principal')

    user_id = auth_header('user_id')
    principal_id = auth_header('principal_id')

    data = request.get_json()
    id = data['id']
    grade = data['grade']

    assignment = Assignment.query.filter(and_(Assignment.id == id,
                                                  Assignment.teacher_id == principal_id)).first()
    
    if not assignment:
            return jsonify({"error": "Assignment not found or you are not authorized to grade it"}), 404

        # Update the assignment with the new grade
    assignment.grade = grade
    assignment.state = "GRADED"
    db.session.commit()

    result ={
        "content":assignment.content,
        "created_at":assignment.created_at,
        "updated_at":assignment.updated_at,
        "grade":assignment.grade,
        "state":assignment.state,
        "student_id":assignment.student_id,
        "teacher_id":assignment.teacher_id,
        "id":assignment.id
    }

    return jsonify(result)



if __name__ =='__main__':
    app.run(debug =True)
