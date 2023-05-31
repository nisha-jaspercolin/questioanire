from flask import Flask, jsonify, Response, request
import pymongo
import json
from bson.objectid import ObjectId

app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"

@app.route('/home', methods=['POST', 'GET'], defaults={'name': 'Default'})
@app.route('/home/<string:name>', methods=['POST', 'GET'])
def home(name):
    return '<h1>Hello {}, you are on a Home Page.</h1>'.format(name)

################################## Mongo CRUD Operations ######################
try:
    #connecting to mongo server
    mongo = pymongo.MongoClient('mongodb://nishaAdmin:admin@192.168.2.204:27017/qbuilder_db?authSource=admin&authMechanism=SCRAM-SHA-256')
    db = mongo.qbuilder_db #creating a new database namely Questionaire

    # mongo = pymongo.MongoClient("mongodb+srv://nishadatascientist12:L0DRVxKQeexcOF56@appcluster.n8hsla5.mongodb.net/?retryWrites=true&w=majority") #connecting to mongo server
    # db = mongo.Questionaire #creating a new database namely Questionaire
    mongo.server_info()
except:
    print("Error while connecting database!")

################################## Get All Questions ##################################
@app.route("/questions",methods=["GET"])
def get_all_questions(): #function to display all the  questions from database
    try:
        # data = list(db.Questions.find())  
        data = list(db.ict_db.find())        
        for question in data:
            question["_id"] = str(question["_id"])
        return Response(response=json.dumps(data),status=200,mimetype="application/json")
    except Exception as ex: #except block used in case any error occures while connecting with database or any other unexpected error occurs
        print(ex)
        return Response(response=json.dumps({"message":"Cannot read questions",}),status=500,mimetype="application/json")

################################# Search Question by Keyword #################################
@app.route("/questionsbykeywords",methods=["GET"])
def get_question(): #function to get question with specific keyword from database
    try:
        # print(request.form["keywords"])
        #data = list(db.ict_db)
        # data = list(db.question.find({"cuisine" : { "$regex" : "^C" }})
        keydetails = request.form["keywords"]

        keywords = keydetails.split(',')
        # print(keywords)
        # query = {'$or': [{'field1' : {'$regex' : keywords, '$options' : 'i'}}for keyword in keywords]}
        # print(query)
        # data = db.ict_db.find(query)
        print(keywords)

        myquery = { "keywords": { "$regex": "^" + str(keywords) } }
        
        data = db.ict_db.find(myquery)
        
        return Response(response=json.dumps(data),status=200,mimetype="application/json")
        # for user in data:
        #     user["_id"]=str(user["_id"])    
        
        # keywords = request.args.get('keywords', '').split(',')
        # query = {'$or': [{'field1' : {'$regex' : keyword, '$options' : 'i'}}for keyword in keywords]}
        # data = list(collection.find(query))
        # return jsonify(data)

    except Exception as ex: #except block used in case wrong user id is given or any other unexpected error occurs
        print(ex)
        return Response(response=json.dumps({"message": "Error Cannot Find question"}),status=500,mimetype="application/json")
    
################################## Create Question ##################################
@app.route("/createquestions",methods=['GET', 'POST'])
def create_question(): #function to create new question in database
    try:
        question = {"qlabel": request.form["qlabel"], "qtext": request.form["qtext"],"qtype": request.form["qtype"], "qrows": request.form["qrows"], "qcolumn": request.form["qcolumn"], "domain": request.form["domain"],"subdomain1": request.form["subdomain1"],"subdomain2": request.form["subdomain2"],"keywords": request.form["keywords"]}
        print(question)
        dbResponse = db.ict_db.insert_one(question)
        print(dbResponse)
        data = list(db.ict_db.find({"_id": ObjectId(dbResponse.inserted_id)}))
        
        for question_id in data:
            question_id["_id"]=str(question_id["_id"])

        return Response(response=json.dumps({"message":"Question created sucessfully","id": f"{dbResponse.inserted_id}","Question": data[0]["Question"],"qtext": data[0]["qtext"],"qtype": data[0]["qtype"]}),status=200,mimetype="application/json")
    except Exception as ex: #except block used in case any error occur while adding data or any wrong entry is filled or any entry filled with wrong or improper data or any other unexpected error occurs
        print(ex)
        
################################## Update Question ##################################
@app.route("/udatequestions/<id>",methods=["PATCH"])
def update_question(id): #function to update the data of question with specific id in database
    try:
        dbResponse = db.ict_db.update_one({"_id": ObjectId(id)},{"$set": {"qtext": request.form["qtext"],"qtype": request.form["qtype"],"domain": request.form["domain"]}})
        
        if dbResponse.modified_count==1:
            return Response(response=json.dumps({"message": "Questions updated scuessfully."}),status=200,mimetype="application/json")
        else:
            return Response(response=json.dumps({"message": "Nothing to modify"}),status=200,mimetype="application/json")
    except Exception as ex: #excep block is used in case wrong id is used or question with the id is not present or any other unexpected error occurs
        print(ex)
        return Response(response=json.dumps({"message": "Error Cannot update question"}),status=500,mimetype="application/json")

##################################  Delete Question ################################## 
@app.route("/deletequestion/<id>",methods=["DELETE"])
def delete_question(id): #function to delete question from database 
    try:
        data = list(db.ict_db.find({"_id": ObjectId(id)}))
        for question_id in data:
            question_id["_id"]=str(question_id["_id"])
        print(str(data))      
        dbResponse = db.ict_db.delete_one({"_id": ObjectId(id)})
        if dbResponse.deleted_count==1:
            return Response(response=json.dumps({"message": "Question Deleted Successfully ","id": id,"Question": data[0]["Question"],"qtext": data[0]["qtext"],"qtype": data[0]["qtype"]}),status=200,mimetype="application/json")
        else:
            return Response(response=json.dumps({"message": "Question not found"}),status=500,mimetype="application/json")
    except Exception as ex: #except block if question not found or any other unexpected error occurs
        print("*********************")
        print(ex)
        print("*********************")
        return Response(response=json.dumps({"message": "Cannot delete question"}),status=500,mimetype="application/json")

##################################
if __name__ == '__main__':
    app.run(host="127.0.0.9", port=8080, debug=True)
