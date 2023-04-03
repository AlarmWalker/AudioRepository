#!/usr/bin/env python3
import os
import sys
from flask import Flask, jsonify, abort, request, make_response, session, flash, redirect, url_for
from flask_restful import reqparse, Resource, Api
from flask_session import Session
import json
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import *
import pymysql
import pymysql.cursors
import ssl
from werkzeug import secure_filename

import settings  # Our server and db settings, stored in settings.py

UPLOAD_FOLDER = 'audios/'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
app.config['SESSION_COOKIE_DOMAIN'] = settings.APP_HOST
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
####################################################################################
#
# Error handlers
#
@app.errorhandler(400) # decorators to add to 400 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Bad request' } ), 400)

@app.errorhandler(404) # decorators to add to 404 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Resource not found' } ), 404)

@app.errorhandler(500) # decorators to add to 500 response
def not_found(error):
	return make_response(jsonify( { 'status': 'Internal server error' } ), 500)


####################################################################################
#
# Static Endpoints for humans
#
class Root(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('index.html')


class Developer(Resource):
   # get method. What might others be aptly named? (hint: post)
	def get(self):
		return app.send_static_file('developer.html')

####################################################################################
#
# Routing: GET and POST using Flask-Session
#
class SignIn(Resource):
	#
	# Set Session and return Cookie
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X POST -d '{"username": "Jen", "password": "password123"}'
	#  	-c cookie-jar -k https://cs3103.cs.unb.ca:8024/signin
        # OR use signinClient script
	#
	def post(self):

		if not request.json:
			abort(400) # bad request

		# Parse the json
		parser = reqparse.RequestParser()
		try:
 			# Check for required attributes in json document, create a dictionary
			parser.add_argument('username', type=str, required=True)
			parser.add_argument('password', type=str, required=True)
			request_params = parser.parse_args()
		except:
			abort(400) # bad request
		if request_params['username'] in session:
			response = {'status': 'success'}
			responseCode = 200
		else:
			try:
				ldapServer = Server(host=settings.LDAP_HOST)
				ldapConnection = Connection(ldapServer,
					raise_exceptions=True,
					user='uid='+request_params['username']+', ou=People,ou=fcs,o=unb',
					password = request_params['password'])
				ldapConnection.open()
				ldapConnection.start_tls()
				ldapConnection.bind()
				session['username'] = request_params['username']
				try:
					dbConnection = pymysql.connect(
						settings.DB_HOST,
						settings.DB_USER,
						settings.DB_PASSWD,
						settings.DB_DATABASE,
						charset='utf8mb4',
						cursorclass= pymysql.cursors.DictCursor)
					username = session['username']
					cursor = dbConnection.cursor()

					sql1 = 'findUser'
					sqlArgs = [username]
					cursor.callproc(sql1, sqlArgs)
					result = cursor.fetchone()
					#if we cant find user in database, create user.
					if result is None:
						sql2 = 'addUser'
						cursor.callproc(sql2, sqlArgs)
						dbConnection.commit()

					cursor.callproc(sql1, sqlArgs)
					result = cursor.fetchone()
					
				except:
					abort(500)
				finally:
					cursor.close()
					dbConnection.close()
				response = {'status': 'success', 'user_id':result }
				responseCode = 201
			except LDAPException:
				response = {'status': 'Access denied'}
				print(response)
				responseCode = 403
			finally:
				ldapConnection.unbind()

		return make_response(jsonify(response), responseCode)

	# GET: Check Cookie data with Session data
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X GET
	#	-c cookie-jar -k https://cs3103.cs.unb.ca:8024/signin
	def get(self):
		if 'username' in session:
			username = session['username']
			response = {'status': 'success'}
			responseCode = 200
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

    # DELETE: Sign out a user
	#
	# Example curl command:
	# curl -i -H "Content-Type: application/json" -X DELETE
	#	-c cookie-jar -k https://cs3103.cs.unb.ca:8024/signin
	def delete(self):
		if 'username' in session:
			session.pop('username', None)
			response = {'status': 'success'}
			responseCode = 204
		else:
			response = {'status': 'fail'}
			responseCode = 403

		return make_response(jsonify(response), responseCode)

class Users(Resource):
    # GET: return all registered users
    #
    # Example curl command:
    # curl -i -H "Content-Type: application/json" -X GET
    #	-c cookie-jar -k https://cs3103.cs.unb.ca:8024/users
    def get(self):
        if 'username' in session:
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)
        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql = 'getAllUsers'
            cursor = dbConnection.cursor()
            cursor.callproc(sql)
            result = cursor.fetchall()
            if result is None:
                abort(404)
            else:
                response = {"Users": result}
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        
        return make_response(jsonify(response), 200)

class User(Resource):
    # GET: return certain user by Id
    #
    # Example curl command:
    # curl -i -H "Content-Type: application/json" -X GET
    #	-c cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<userId>
    def get(self, userId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql = 'getUserById'
            sqlArgs = (userId,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"message": "user does not exist"}), 404)
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"user": row}), 200)

    # DELETE: delete a user
    #
    # Example curl command:
    # curl -i -H "Content-Type: application/json" -X DELETE
    #	-c cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<userId>
    def delete(self, userId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql = 'deleteUser'
            sql2 = 'getUserById'
            sqlArgs = (userId,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"user does not exist"}), 404)
            cursor.callproc(sql, sqlArgs)
            dbConnection.commit()
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"status": "success", "message":"successfully deleted user"}), 204)

class UserByName(Resource):
    # GET: return certain user by username
    #
    # Example curl command:
    # curl -i -H "Content-Type: application/json" -X GET
    #	-c cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<username>
    def get(self, username):
        if 'username' in session:
            #username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql = 'getUserByName'
            sqlArgs = (username,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"message": "user does not exist"}), 404)
            else:
                response = {"Users": row}
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        
        return make_response(jsonify(response), 200)
class Audios(Resource):

    # GET: Return all audios in database
    #
    # Example request: curl -i -H "Content-Type: application/json" -X GET
    # -b cookie-jar -k https://cs3103.cs.unb.ca:8024/audios
    #
    def get(self):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql = 'getAllAudio'
            cursor = dbConnection.cursor()
            cursor.callproc(sql)
            row = cursor.fetchall()
            if row is None:
                abort(404)
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"audios": row}), 200)

    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
class Audio(Resource):
    # GET: Returns certain audio
    #
    # Example request: curl -i -H "Content-Type: application/json" -X GET
    # -b cookie-jar -k https://cs3103.cs.unb.ca:8024/audios/<audioId>
    #
    def get(self, audioId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql = 'getAudioById'
            sqlArgs = (audioId, )
            cursor = dbConnection.cursor()
            cursor.callproc(sql, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message": "audio does not exist"}), )
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"audio": row}), 200)

class UserAudioLibrary(Resource):

    # GET: Returns a user's audio library
    #
    # Example request: curl -i -H "Content-Type: application/json" -X GET
    # -b cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<userId>/audios
    def get(self, userId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql2 = 'getUserById'
            sqlArgs = (userId,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"user does not exist"}), 404)

            sql = 'getUserAudioLibrary'
            sqlArgs = (userId, )
            cursor.callproc(sql, sqlArgs)
            row = cursor.fetchall()
            if row is None:
                abort(404)
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"Audio Library": row}), 200)

    # POST: Add an audio to user library
    #
    # Example request: curl -i -H "Content-Type: application/json" -X POST
    # -d '{"audioName": "speech of myself", "audioFile": "audios/example.mp3"}'
    # -b cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<userId>/audios
    def post(self, userId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            return make_response(jsonify(response), responseCode)

        if not request.json or not 'audioName' or not 'audioFile' in request.json:
            response = {'status': 'fail', 'message': 'Bad Request'}
            responseCode = 400
            return make_response(jsonify(response), responseCode)

        audioName = request.json["audioName"]
        audioFile = request.json["audioFile"]

        # add audio
        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql2 = 'getUserById'
            sqlArgs = (userId,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"user does not exist"}), 404)

            else:
                sql = 'addAudio'
                sqlArgs = (audioName, audioFile, userId,)
                cursor.callproc(sql, sqlArgs)
                row = cursor.fetchone()
                dbConnection.commit()
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()

        uri = 'http://'+settings.APP_HOST+':'+str(settings.APP_PORT)
        uri = uri+'/users/'+str(userId)+'/audios/'+str(row['LAST_INSERT_ID()'])
        return make_response(jsonify({"status": "success", "uri": uri}), 201)


class UserAudio(Resource):
    # PUT: Update audio name
    #
    # Example request: curl -i -H "Content-Type: application/json" -X PUT
    # -d '{"audioName": "changed audio name"}'
    # -c cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<userId>/audios/<audioId>
    def put(self, userId, audioId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail'}
            responseCode = 403
        if not request.json:
            abort(400)

        if not request.json or not 'audioName' in request.json:
            response = {'status': 'fail', 'message': 'Bad Request'}
            responseCode = 400
            return make_response(jsonify(response), responseCode)

        audioName = request.json["audioName"]

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)

            sql2 = 'getUserById'
            sqlArgs = (userId,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"user does not exist"}), 404)

            sql2 = 'getAudioById'
            sqlArgs = (audioId,)
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"audio does not exist"}), 404)
            else:
                sql = 'updateUserAudio'
                sqlArgs = (audioId, audioName, userId,)
                cursor.callproc(sql, sqlArgs)
                dbConnection.commit()

        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"status": "success", "message":"successfully updated audio name"}), 200)  # successful

    # GET: Return identified audio resource (audio by ID)
    #
    # Example request: curl -i -H "Content-Type: application/json" -X GET
    # -b cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<userId>/audios/<audioId>
    #
    def get(self, userId, audioId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail'}
            responseCode = 403

        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)
            sql2 = 'getUserById'
            sqlArgs = (userId,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"user does not exist"}), 404)

            sql2 = 'getAudioById'
            sqlArgs = (audioId,)
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"audio does not exist"}), 404)
            else:
                sql = 'getUserAudio'
                sqlArgs = (userId, audioId,)
                cursor.callproc(sql, sqlArgs)
                row = cursor.fetchone()
                if row is None:
                    return make_response(jsonify({"status": "fail", "message":"audio does not exist"}), 404)
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"audio": row}), 200)

    # DELETE: Delete audio from user's library
    #
    # Example request: curl -i -H "Content-Type: application/json" -X DELETE
    # -b cookie-jar -k https://cs3103.cs.unb.ca:8024/users/<userId>/audios/<audioId>
    def delete(self, userId, audioId):
        if 'username' in session:
            username = session['username']
            response = {'status': 'success'}
            responseCode = 200
        else:
            response = {'status': 'fail', 'message': 'Access Denied'}
            responseCode = 403
            #return make_response(jsonify(response), responseCode)

        # Delete audio
        try:
            dbConnection = pymysql.connect(
                settings.DB_HOST,
                settings.DB_USER,
                settings.DB_PASSWD,
                settings.DB_DATABASE,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor)

            sql2 = 'getUserById'
            sqlArgs = (userId,)
            cursor = dbConnection.cursor()
            cursor.callproc(sql2, sqlArgs)
            row = cursor.fetchone()
            if row is None:
                return make_response(jsonify({"status": "fail", "message":"user does not exist"}), 404)

            sql = 'deleteUserAudio'
            sql2 = 'getUserAudio'
            sqlArgs = (audioId, userId, )
            cursor.callproc(sql2, (userId, audioId, ))
            result = cursor.fetchone()
            if result is None:
                return make_response(jsonify({"message": "Audio does not exist"}), 404)

            cursor.callproc(sql, sqlArgs)
            dbConnection.commit()
        except:
            abort(500)
        finally:
            cursor.close()
            dbConnection.close()
        return make_response(jsonify({"status": "success"}), 204)

class FileUpload(Resource):
    def post(self):
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return make_response(jsonify({"status": "success"}), 201)


####################################################################################
#
# Identify/create endpoints and endpoint objects
#
api = Api(app)
api.add_resource(Root,'/')
api.add_resource(Developer,'/dev')
api.add_resource(SignIn, '/signin')

#all audios
api.add_resource(Audios, '/audios')

#certain audio
api.add_resource(Audio, '/audios/<int:audioId>')

#user audio library
api.add_resource(UserAudioLibrary, '/users/<int:userId>/audios')
api.add_resource(UserAudio, '/users/<int:userId>/audios/<int:audioId>')

#all Users
api.add_resource(Users, '/users')

#certain user
api.add_resource(User, '/users/<int:userId>')

api.add_resource(UserByName, '/users/<string:username>')

#file upload
api.add_resource(FileUpload, '/FileUpload')

if __name__ == "__main__":
	context = ('cert.pem', 'key.pem')
	app.run(
		host=settings.APP_HOST,
		port=settings.APP_PORT,
		ssl_context=context,
		debug=settings.APP_DEBUG)
