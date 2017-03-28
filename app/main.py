from flask import render_template, url_for, request, session, redirect
from app import webapp

import datetime
import boto3
import json
import os
# import logging

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'
# logging.basicConfig()


@webapp.route('/', methods=['GET', 'POST'])
@webapp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("user/login.html")


@webapp.route('/debate', methods=['GET', 'POST'])
def main():
    return render_template("chat/chat.html")


@webapp.route('/login_submit', methods=['GET', 'POST'])
def login_submit():
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    user = request.form['username']

    error_msg = "Error: User with provided credentials does not exist!"

    tabledata = client.get_item(TableName='userdata', Key={
                                'hfboards': {'S': 'hfboards'}})
    # print('tabledata = ')
    # print(tabledata)
    # print(tabledata['Item']['user']['S'])

    if 'username' in request.form != None \
        and request.form['username'] == tabledata['Item']['user']['S'] and \
        'password' in request.form != None and \
            request.form['password'] == tabledata['Item']['password']['S']:

        session['authenticated'] = True
        session['username'] = request.form['username']
        session['password'] = request.form['password']

        return redirect(url_for('main'))

    return render_template("user/login.html", error_msg=error_msg)


@webapp.route('/create_account', methods=['GET', 'POST'])
def create_account():
    return redirect(url_for('user_create'))


@webapp.route('/user/create', methods=['GET'])
# Display an empty HTML form that allows users to define new user.
def user_create():
    return render_template("user/new.html", title="New User")


@webapp.route('/user/create', methods=['POST'])
# Create a new user and save them in the database.
def user_create_save():
    username = request.form.get('login', "")
    password = request.form.get('password', "")
    password_reenter = request.form.get('password_reenter', "")

    error = False

    if username == "" or password == "":
        error = True
        error_msg = "Error: All fields are required!"

    if password != password_reenter:
        error = True
        error_msg = "Entered passwords do not match"

    if error:
        return render_template("user/new.html", title="New user", error_msg=error_msg,
                               login=username, password=password)

    add_item_to_table(username, password)

    return redirect(url_for('login'))


@webapp.route('/add_item_to_table', methods=['POST'])
# Create a new user and save them in the database.
def add_item_to_table(username, password):
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    client.put_item(TableName='userdata', Item={'user': {'S': username}, 'password': {
                    'S': password}, 'hfboards': {'S': 'hfboards'}})

    return 'Table write complete!'


@webapp.route('/comments_right', methods=['GET', 'POST'])
# Create a new user and save them in the database.
def send_to_server_right():
    import json
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    print request.form['id']
    print request.form['parent']
    print request.form['created']
    print request.form['modified']
    print request.form['content']
    # print request.form['pings']
    print request.form['fullname']
    print request.form['profile_picture_url']
    print request.form['created_by_admin']
    print request.form['created_by_current_user']
    print request.form['upvote_count']
    print request.form['user_has_upvoted']

    print 'dooodi'
    if len(request.form['id']) != 1:
        id = int(request.form['id'][1])
    else:
        id = int(request.form['id'][0])
        
    parent = request.form['parent']
    if parent == "":
        parent = 'null'
    created = request.form['created'][0:10]
    creator = 1
    modified = request.form['modified'][0:10]
    content = request.form['content']
    # creator = request.form['creator']
    # pings = request.form['pings']
    fullname = request.form['fullname']
    profile_picture_url = request.form['profile_picture_url']
    created_by_admin = json.loads(request.form['created_by_admin'])
    created_by_current_user = json.loads(request.form['created_by_current_user'])
    upvote_count = int(request.form['upvote_count'])
    user_has_upvoted = json.loads(request.form['user_has_upvoted'])

    # print 'Field2 = ', str(request.form['parent'])
    # print request.POST['field2']

    client.put_item(TableName='chatdata',
                    Item={'id': {'N': str(id)},
                          'parent': {'S': parent},
                          'created': {'S': created},
                          'modified': {'S': modified},
                          'content': {'S': content},
                          'fullname': {'S': fullname},
                          'profile_picture_url': {'S': profile_picture_url},
                          'created_by_admin': {'BOOL': created_by_admin},
                          'created_by_current_user': {'BOOL': created_by_current_user},
                          'upvote_count': {'N': str(upvote_count)},
                          'user_has_upvoted': {'BOOL': user_has_upvoted},
                          'chatdata': {'S': 'chatdata'}})

    with open("app\static\comments-data-chat-right.json", "r") as data:
        simplejson = json.load(data)

    commentsArray = simplejson["commentsArray"]
    lst = {'id': id, 'parent': parent, 'created': created,
           'modified': modified, 'content': content,
           'fullname': fullname, 'pings': [],
           'profile_picture_url': profile_picture_url,
           'created_by_admin': created_by_admin,
           'created_by_current_user': created_by_current_user,
           'upvote_count': upvote_count,
           'user_has_upvoted': user_has_upvoted,
           'creator': creator}
    # usersArray = simplejson["usersArray"]
    commentsArray.append(lst)

    # commentsArray = set(commentsArray)

    with open("app\static\comments-data-chat-right.json", "w") as outfile:
        json.dump({'commentsArray': commentsArray}, outfile, indent=4)

    return 'Data successfully sent to server!'

@webapp.route('/comments_left', methods=['GET', 'POST'])
# Create a new user and save them in the database.
def send_to_server_left():
    import json
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    print request.form['id']
    print request.form['parent']
    print request.form['created']
    print request.form['modified']
    print request.form['content']
    # print request.form['pings']
    print request.form['fullname']
    print request.form['profile_picture_url']
    print request.form['created_by_admin']
    print request.form['created_by_current_user']
    print request.form['upvote_count']
    print request.form['user_has_upvoted']

    id = int(request.form['id'][1])
    parent = request.form['parent']
    if parent == "":
        parent = 'null'
    created = request.form['created'][0:10]
    creator = 1
    modified = request.form['modified'][0:10]
    content = request.form['content']
    # creator = request.form['creator']
    # pings = request.form['pings']
    fullname = request.form['fullname']
    profile_picture_url = request.form['profile_picture_url']
    created_by_admin = json.loads(request.form['created_by_admin'])
    created_by_current_user = json.loads(request.form['created_by_current_user'])
    upvote_count = int(request.form['upvote_count'])
    user_has_upvoted = json.loads(request.form['user_has_upvoted'])

    # print 'Field2 = ', str(request.form['parent'])
    # print request.POST['field2']

    client.put_item(TableName='chatdata',
                    Item={'id': {'N': str(id)},
                          'parent': {'S': parent},
                          'created': {'S': created},
                          'modified': {'S': modified},
                          'content': {'S': content},
                          'fullname': {'S': fullname},
                          'profile_picture_url': {'S': profile_picture_url},
                          'created_by_admin': {'BOOL': created_by_admin},
                          'created_by_current_user': {'BOOL': created_by_current_user},
                          'upvote_count': {'N': str(upvote_count)},
                          'user_has_upvoted': {'BOOL': user_has_upvoted},
                          'chatdata': {'S': 'chatdata'}})

    with open("app\static\comments-data-chat-right.json", "r") as data:
        simplejson = json.load(data)

    commentsArray = simplejson["commentsArray"]
    lst = {'id': id, 'parent': parent, 'created': created,
           'modified': modified, 'content': content,
           'fullname': fullname, 'pings': [],
           'profile_picture_url': profile_picture_url,
           'created_by_admin': created_by_admin,
           'created_by_current_user': created_by_current_user,
           'upvote_count': upvote_count,
           'user_has_upvoted': user_has_upvoted,
           'creator': creator}
    # usersArray = simplejson["usersArray"]
    commentsArray.append(lst)

    # commentsArray = set(commentsArray)

    with open("app\static\comments-data-chat-right.json", "w") as outfile:
        json.dump({'commentsArray': commentsArray}, outfile, indent=4)

    return 'Data successfully sent to server!'

