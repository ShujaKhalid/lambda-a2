from flask import render_template, url_for, request, session, redirect
from app import webapp

import datetime
import boto3
import json
import os
# import logging

webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'
# logging.basicConfig()


@webapp.route('/dev/login', methods=['GET', 'POST'])
def login():
    return render_template("user/login.html")


@webapp.route('/', methods=['GET', 'POST'])
@webapp.route('/dev/', methods=['GET', 'POST'])
@webapp.route('/dev/debate', methods=['GET', 'POST'])
def main():
    return render_template("chat/chat.html")


@webapp.route('/dev/login_submit', methods=['GET', 'POST'])
def login_submit():
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')
    import urllib

    email = request.form['email']

    error_msg = "Error: User with provided credentials does not exist!"

    tabledata = client.get_item(TableName='userdata', Key={
                                'hfboards': {'S': email}})
    # print('tabledata = ')
    # print(tabledata)
    # print(tabledata['Item']['user']['S'])

    if 'email' in request.form != None \
        and request.form['email'] == tabledata['Item']['hfboards']['S'] and \
        'password' in request.form != None and \
            request.form['password'] == tabledata['Item']['password']['S']:

        session['authenticated'] = True
        session['email'] = request.form['email']
        session['username'] = tabledata['Item']['user']['S']
        session['password'] = request.form['password']
        username = session['username']

        url = "https://s3.amazonaws.com/ece1779bucket2/user-data.json"
        response = urllib.urlopen(url)
        response_read = response.read()
        simplejson = json.loads(response_read)
        print simplejson

        usersArray = simplejson["usersArray"]
        # Count the no. of users that already exist
        count = 0
        for i in usersArray:
            count = count + 1

        lst = {'id': count,
               'email': email,
               'username': session['username'],
               'profile_picture_url': "https://app.viima.com/static/media/user_profiles/user-icon.png"
               }

        usersArray.append(lst)
        with open("app/static/user-data.json", "w") as outfile:
            json.dump({'usersArray': usersArray}, outfile, indent=4)

        s3 = boto3.client('s3')
        with open('app/static/user-data.json', 'rb') as data:
            s3.upload_fileobj(data, 'ece1779bucket2', 'user-data.json')

        return render_template("chat/chat.html", username=username)

    else:
        return render_template("user/login.html", error_msg=error_msg)


@webapp.route('/dev/create_account', methods=['GET', 'POST'])
def create_account():
    return redirect(url_for('user_create'))


@webapp.route('/dev/user/create', methods=['GET'])
# Display an empty HTML form that allows users to define new user.
def user_create():
    return render_template("user/new.html", title="New User")


@webapp.route('/dev/user/create', methods=['POST'])
# Create a new user and save them in the database.
def user_create_save():
    username = request.form.get('login', "")
    email = request.form.get('email', "")
    password = request.form.get('password', "")
    password_reenter = request.form.get('password_reenter', "")

    error = False

    if username == "" or password == "" or email == "":
        error = True
        error_msg = "Error: All fields are required!"

    if password != password_reenter:
        error = True
        error_msg = "Entered passwords do not match"

    if error:
        return render_template("user/new.html", title="New user", error_msg=error_msg,
                               login=username, password=password)

    add_item_to_table(username, password, email)

    return redirect(url_for('login'))


@webapp.route('/dev/add_item_to_table', methods=['POST'])
# Create a new user and save them in the database.
def add_item_to_table(username, password, email):
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    client.put_item(TableName='userdata', Item={'user': {'S': username}, 'password': {
                    'S': password}, 'hfboards': {'S': email}})

    return 'Table write complete!'


@webapp.route('/dev/comments_right', methods=['GET', 'POST'])
# Create a new user and save them in the database.
def send_to_server_right():
    import json
    from datetime import datetime
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

    # print 'dooodi'
    print request.form['id']
    if len(request.form['id']) != 1:
        id = int(request.form['id'][1])
    else:
        id = int(request.form['id'][0])

    if len(request.form['parent']) == 2:
        parent = int(request.form['parent'][1])
    elif (len(request.form['parent']) == 1):
        parent = int(request.form['parent'][0])
    else:
        parent = None

    # parent = request.form['parent']
    if parent == "":
        parent_temp = 'null'
        parent = None
    else:
        parent_temp = str(parent)
        parent = parent
    created = request.form['created'][0:10]
    creator = 1
    modified = request.form['modified'][0:10]
    content = request.form['content']
    # creator = request.form['creator']
    # pings = request.form['pings']
    fullname = request.form['fullname']
    profile_picture_url = request.form['profile_picture_url']
    created_by_admin = json.loads(request.form['created_by_admin'])
    created_by_current_user = json.loads(
        request.form['created_by_current_user'])
    upvote_count = int(request.form['upvote_count'])
    user_has_upvoted = json.loads(request.form['user_has_upvoted'])

    # print 'Field2 = ', str(request.form['parent'])
    # print request.POST['field2']

    client.put_item(TableName='chatdata',
                    Item={'id': {'N': str(id)},
                          'parent': {'S': parent_temp},
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
    import urllib
    url = "https://s3.amazonaws.com/ece1779bucket2/comments-data-chat-right.json"
    response = urllib.urlopen(url)
    response_read = response.read()
    simplejson = json.loads(response_read)

    commentsArray = simplejson["commentsArray"]
    time = datetime.now().strftime('%Y%m%d%H%M%S')
    lst = {'modacc': time, 'id': id, 'parent': parent, 'created': created,
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
    null_array = []
    reply_array = []

    for i in commentsArray:
        if i['parent'] == None:
            null_array.append(i)

    for i in commentsArray:
        if i['parent'] != None:
            reply_array.append(i)

    # commentsArray = set(commentsArray)
    null_array.sort(key=lambda modacc: modacc, reverse=True)
    reply_array.sort(key=lambda x: ('id', 'modacc'), reverse=False)
    # print 'after: ' , lst

    for i in reply_array:
        null_array.append(i)

    commentsArray = null_array
    print commentsArray

    with open("app/static/comments-data-chat-right.json", "w") as outfile:
        json.dump({'commentsArray': commentsArray}, outfile, indent=4)
    # Upload a new file
    s3 = boto3.client('s3')
    with open('app/static/comments-data-chat-right.json', 'rb') as data:
        s3.upload_fileobj(data, 'ece1779bucket2',
                          'comments-data-chat-right.json')
        # s3_client.Bucket('ece1779bucket2').put_object(Key='comments-data-chat-right.json', Body=data)

    return 'Data successfully sent to server!'

@webapp.route('/dev/comments_left', methods=['GET', 'POST'])
# Create a new user and save them in the database.
def send_to_server_left():
    import json
    from datetime import datetime
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

    # print 'dooodi'
    print request.form['id']
    if len(request.form['id']) != 1:
        id = int(request.form['id'][1])
    else:
        id = int(request.form['id'][0])

    if len(request.form['parent']) == 2:
        parent = int(request.form['parent'][1])
    elif (len(request.form['parent']) == 1):
        parent = int(request.form['parent'][0])
    else:
        parent = None

    # parent = request.form['parent']
    if parent == "":
        parent_temp = 'null'
        parent = None
    else:
        parent_temp = str(parent)
        parent = parent
    created = request.form['created'][0:10]
    creator = 1
    modified = request.form['modified'][0:10]
    content = request.form['content']
    # creator = request.form['creator']
    # pings = request.form['pings']
    fullname = request.form['fullname']
    profile_picture_url = request.form['profile_picture_url']
    created_by_admin = json.loads(request.form['created_by_admin'])
    created_by_current_user = json.loads(
        request.form['created_by_current_user'])
    upvote_count = int(request.form['upvote_count'])
    user_has_upvoted = json.loads(request.form['user_has_upvoted'])

    # print 'Field2 = ', str(request.form['parent'])
    # print request.POST['field2']

    client.put_item(TableName='chatdata',
                    Item={'id': {'N': str(id)},
                          'parent': {'S': parent_temp},
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
    import urllib
    url = "https://s3.amazonaws.com/ece1779bucket2/comments-data-chat-left.json"
    response = urllib.urlopen(url)
    response_read = response.read()
    simplejson = json.loads(response_read)

    commentsArray = simplejson["commentsArray"]
    time = datetime.now().strftime('%Y%m%d%H%M%S')
    lst = {'modacc': time, 'id': id, 'parent': parent, 'created': created,
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
    null_array = []
    reply_array = []

    for i in commentsArray:
        if i['parent'] == None:
            null_array.append(i)

    for i in commentsArray:
        if i['parent'] != None:
            reply_array.append(i)

    # commentsArray = set(commentsArray)
    null_array.sort(key=lambda modacc: modacc, reverse=True)
    reply_array.sort(key=lambda x: ('id', 'modacc'), reverse=False)
    # print 'after: ' , lst

    for i in reply_array:
        null_array.append(i)

    commentsArray = null_array
    print commentsArray

    with open("app/static/comments-data-chat-left.json", "w") as outfile:
        json.dump({'commentsArray': commentsArray}, outfile, indent=4)
    # Upload a new file
    s3 = boto3.client('s3')
    with open('app/static/comments-data-chat-left.json', 'rb') as data:
        s3.upload_fileobj(data, 'ece1779bucket2',
                          'comments-data-chat-left.json')
        # s3_client.Bucket('ece1779bucket2').put_object(Key='comments-data-chat-right.json', Body=data)

    return 'Data successfully sent to server!'


@webapp.route('/dev/del_comments_right', methods=['GET', 'POST'])
# Delete a comment
def del_comments_right():
    from datetime import datetime
    new_array = []

    if len(request.form['id']) != 1:
        id = int(request.form['id'][1])
    else:
        id = int(request.form['id'][0])

    import urllib
    url = "https://s3.amazonaws.com/ece1779bucket2/comments-data-chat-right.json"
    response = urllib.urlopen(url)
    response_read = response.read()
    simplejson = json.loads(response_read)

    commentsArray = simplejson["commentsArray"]

    for i in commentsArray:
        if i['id'] != id:
            new_array.append(i)

    with open("app/static/comments-data-chat-right.json", "w") as outfile:
        json.dump({'commentsArray': new_array}, outfile, indent=4)
    # Upload a new file
    s3 = boto3.client('s3')
    with open('app/static/comments-data-chat-right.json', 'rb') as data:
        s3.upload_fileobj(data, 'ece1779bucket2',
                          'comments-data-chat-right.json')

    return 'Comment Deleted'

@webapp.route('/dev/del_comments_left', methods=['GET', 'POST'])
# Delete a comment
def del_comments_left():
    from datetime import datetime
    new_array = []

    if len(request.form['id']) != 1:
        id = int(request.form['id'][1])
    else:
        id = int(request.form['id'][0])

    import urllib
    url = "https://s3.amazonaws.com/ece1779bucket2/comments-data-chat-left.json"
    response = urllib.urlopen(url)
    response_read = response.read()
    simplejson = json.loads(response_read)

    commentsArray = simplejson["commentsArray"]

    for i in commentsArray:
        if i['id'] != id:
            new_array.append(i)

    with open("app/static/comments-data-chat-left.json", "w") as outfile:
        json.dump({'commentsArray': new_array}, outfile, indent=4)
    # Upload a new file
    s3 = boto3.client('s3')
    with open('app/static/comments-data-chat-left.json', 'rb') as data:
        s3.upload_fileobj(data, 'ece1779bucket2',
                          'comments-data-chat-left.json')

    return 'Comment Deleted'


@webapp.route('/dev/vote_agree', methods=['GET', 'POST'])
# Check the user and add a vote if
def vote_agree():
    new_array = []
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    client.put_item(TableName='votedata',
                    Item={'vote': {'S': 'yes'},
                          'votes': {'S': session['username']}})

    # Add animation later
    return render_template("chat/chat.html", username=session['username'])


@webapp.route('/dev/vote_disagree', methods=['GET', 'POST'])
# Check the user and add a vote if
def vote_disagree():
    new_array = []
    client = boto3.client('dynamodb')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('userdata')

    client.put_item(TableName='votedata',
                    Item={'vote': {'S': 'no'},
                          'votes': {'S': session['username']}})

    # Add animation later
    return render_template("chat/chat.html", username=session['username'])


@webapp.route('/dev/results', methods=['GET', 'POST'])
# Create a new user and save them in the database.
def view_results():
    import boto3
    agree_votes = 0.0
    disagree_votes = 0.0
    client = boto3.client('dynamodb')

    response = client.scan(
        TableName='votedata'
        )


    # Get the vote data
    total_votes = response['Count']
    for i in response['Items']:
        if i['vote']['S'] == "yes":
            agree_votes = agree_votes + 1.0
        else:
            disagree_votes = disagree_votes + 1.0

    percent = int((agree_votes/total_votes)*100.0)

    # print the data
    print 'total_votes = ' + str(response['Count'])
    print 'agree_votes = ' + str(agree_votes)
    print 'disagree_votes = ' + str(disagree_votes)
    print 'percent = ' + str(percent)

    # Get the chat data
    import urllib
    url = "https://s3.amazonaws.com/ece1779bucket2/comments-data-chat-right.json"
    response = urllib.urlopen(url)
    response_read = response.read()
    simplejson = json.loads(response_read)

    commentsArray = simplejson["commentsArray"]
    unique_id_right = []
    likes_right = 0

    for i in commentsArray:
        unique_id_right.append(i['id'])
        if i['upvote_count'] == 1:
            likes_right = likes_right + 1

    unique_id_right = set(unique_id_right)
    print (unique_id_right)  
    print (likes_right)  
    print max(unique_id_right)  

    # Get the chat data
    import urllib
    url = "https://s3.amazonaws.com/ece1779bucket2/comments-data-chat-left.json"
    response = urllib.urlopen(url)
    response_read = response.read()
    simplejson = json.loads(response_read)

    commentsArray = simplejson["commentsArray"]
    unique_id_left = []
    likes_left = 0

    for i in commentsArray:
        unique_id_left.append(i['id'])
        if i['upvote_count'] == 1:
            likes_left = likes_left + 1

    unique_id_left = set(unique_id_left)
    total_comments = max(unique_id_left) + max(unique_id_right)
    print (likes_left)  
    print max(unique_id_left)  

    return render_template("counter/counter.html", 
        total_votes=int(total_votes), 
        agree_votes=int(agree_votes), 
        disagree_votes=int(disagree_votes),
        percent=percent,
        total_comments=total_comments,
        likes_left=likes_left,
        likes_right=likes_right)
