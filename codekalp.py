

from flask import *
# from flask_ngrok import run_with_ngrok
from db import insert
import uuid
import json
import pyodbc



from datetime import datetime as dt

#initialising date and time object
now_date = dt.now()
DATE = now_date.strftime("%Y-%m-%d")
TIME = now_date



#connection string for database named CODEKALP
conn = (
    "Driver={SQL Server};"
    "SERVER=(local);"
    "Database=CODEKALP;"
    "Trusted_Connection=yes;"
)

#connecting 
connecting = pyodbc.connect(conn)

#cursor 

cursor = connecting.cursor()


""" calling the class insert which contains database inserting commands """
insertion = insert()

#initialising the unique id uuid
unique = uuid.uuid1()

#initialising Flask app

codekalp = Flask(__name__)
# run_with_ngrok(app)

#setting up of secret key
codekalp.secret_key = "ALE"


#default route with '/' it is used for sign up
@codekalp.route("/",methods=["GET","POST"])
def signup():

    if "LOGGED_USER" in session:
        return redirect(url_for('main'))
    #user_id
    USER_ID = unique.hex
    

    if request.method == "POST":
        EMAIL = request.form['email']
        NAME = request.form['name']
        USERNAME = request.form['username']

        #assigning USERNAME in session for global access and to know the current user
        session['USERNAME'] = USERNAME
        PASSWORD = request.form['password']

        """checking whether the signing in user details are already in the table 
           called SIGN_UP """
        selection_query =("select * from SIGN_UP where USER_NAME='{}'".format(USERNAME))
        var = cursor.execute(selection_query).fetchone()

        #if signning in user details are not in the SIGN_UP table it will allow to insert into SIGN_UP table
        if var == None:
            values_signup = (USER_ID,EMAIL,NAME,USERNAME,PASSWORD,DATE,TIME)
            insertion.signup(values_signup)

            """inserting the USER_ID and USERNAME  also in the PROFILE table"""
            values_profile = (USER_ID,USERNAME,"","")
            insertion.profile(values_profile)
            return redirect(url_for('createprofile'))
        else:

            """if the user credentials is existed with the same username"""
            flash("This username is already existed")
            return redirect(url_for('signup'))


    return render_template("signup.html")

#create profile page route
@codekalp.route("/createprofile",methods=["GET","POST"])
def createprofile():
    if request.method == "POST":
        
        image = request.form["img"]
        user_bio = request.form["userbio"]

        #updating the userbio and image in the relevant field
        updating = ("update PROFILE set PROFILE_PIC='{}',USER_BIO='{}' where USER_NAME='{}'".format(image,user_bio,session['USERNAME']))
        updated_profile = cursor.execute(updating)
        cursor.commit()
        return redirect(url_for('login'))
    return render_template("createprofile.html")


#login route for login page
@codekalp.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        logged_user = request.form['username']
        #creating session variable for LOGGED_USER
        session["LOGGED_USER"] = logged_user

        logged_password = request.form['password']

        #checking the entered user credentials
        checking =("select USER_ID from SIGN_UP where USER_NAME='{}' and PASSWORD='{}'".format(logged_user,logged_password))

        var_user_id = cursor.execute(checking).fetchone()
        if var_user_id == None:
            flash("Username or password is wrong")
            return redirect('login')
        else:
            stripping = str(var_user_id)
            storing_user_id = stripping[2:-4] 
            #print(storing_user_id)
            session['USER_ID'] = storing_user_id
            return redirect('main')
    


    #verifying user
   
    return render_template("login.html")


   


@codekalp.route("/main")
def main():
    if "LOGGED_USER" in session:
        Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
        exe = cursor.execute(Profile_display).fetchone()
   
        return render_template("main.html",exe=exe)
    return redirect(url_for('login'))



@codekalp.route("/posting",methods=["GET","POST"])
def post():
    POST_ID = unique.int
    print(POST_ID)
    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()
    
    if request.method == "POST":
        
        LANGUAGE = request.form["lang"]
        
        POST_CODE = request.form["ale"]
        DESCRIPT = request.form["description"]
        values_post = (str(POST_ID),LANGUAGE,POST_CODE,DESCRIPT,session['LOGGED_USER'],DATE,TIME,0)
        insertion.post(values_post)

        FILE_OPEN = open("USER_FILES/{}{}".format(POST_ID,LANGUAGE),"w")
        writing = FILE_OPEN.write(POST_CODE)

        

        return redirect(url_for('posted'))

    
    
    return render_template("post.html",exe=exe)

@codekalp.route("/question",methods=["POST","GET"])
def question():

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()
    if request.method == "POST":
        question_id = unique.hex
        quest_lang = request.form["language"]
        question_code = request.form["post-code"]
        question_descript = request.form["description"]
        questioned_by = session["LOGGED_USER"]
        
        values_question = (question_id,quest_lang,question_code,question_descript,questioned_by,DATE,TIME)
        print(values_question)
        insertion.question(values_question)
        return redirect(url_for('questioned'))

   
        
    return render_template("question.html",exe=exe)

@codekalp.route("/questioned")
def questioned():

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    show_post = cursor.execute("select QUESTION.QUESTION_ID, QUESTION.QUEST_LANG,QUESTION.QUEST_CODE,QUESTION.QUEST_DESCRIPT,QUESTION.DATE,QUESTION.QUESTIONED_BY,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from QUESTION inner join PROFILE on QUESTION.QUESTIONED_BY = PROFILE.USER_NAME order by QUESTION.DATE DESC").fetchall()
    print(show_post)
    var = cursor.execute("select * from QUESTION").fetchall()
    print(var)
    return render_template("questioned.html",show_post=show_post,exe=exe)


@codekalp.route("/posted")
def posted():
    if "LOGGED_USER" in session:

        Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
        exe = cursor.execute(Profile_display).fetchone()
        #print(exe)
        show_post = cursor.execute("select POST.LANG,POST.POST_CODE,POST.POST_DESCRIPT,POST.POSTED_BY ,POST.LIKES,POST.DATE,PROFILE.USER_BIO,PROFILE.PROFILE_PIC,POST.POST_ID from POST inner join PROFILE on POST.POSTED_BY=PROFILE.USER_NAME order by DATE DESC").fetchall()
        print(show_post)

        #signup

        signup_details = cursor.execute("select SIGN_UP.USER_ID,SIGN_UP.USER_NAME,PROFILE.PROFILE_PIC from SIGN_UP inner join PROFILE on SIGN_UP.USER_NAME=PROFILE.USER_NAME").fetchall()
        #print(signup_details)
        return render_template("posted.html",show_post=show_post,exe=exe,signup_details=signup_details)
    return redirect(url_for('login'))



@codekalp.route("/comment",methods=["POST"])
def comment():
    COMMENT = request.form["commentinfo"]  
    POST_ID = request.form["reqpost"]
    #print(comment,post_id)
    values_comments = (session["LOGGED_USER"],POST_ID,COMMENT,DATE,TIME)
    insertion.comments(values_comments)

    
    return jsonify({"comment":"commented successfully!"})




@codekalp.route("/uniq/<id>")
def uniquepost(id):
    print(id)

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()
    
    likers = cursor.execute("select CODEKALP.LIKED_BY,PROFILE.PROFILE_PIC from CODEKALP inner join PROFILE on PROFILE.USER_NAME = CODEKALP.LIKED_BY where LIKED_POST = '{}'".format(id)).fetchall()
    print("LIKES..",likers)
    count_likers = len(likers)

    comments = cursor.execute(f"select COMMENT.COMMENTED_BY,COMMENT.COMMENT,PROFILE.PROFILE_PIC from COMMENT inner join  PROFILE on  COMMENT.COMMENTED_BY = PROFILE.USER_NAME where COMMENTED_POST = '{id}'").fetchall()
    print(comments)
    count_comments = len(comments)

    one = cursor.execute("select POST.LANG,POST.POST_CODE,POST.DATE,POST.POST_DESCRIPT,POST.POSTED_BY ,POST.POST_ID,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from POST inner join PROFILE on POST.POSTED_BY=PROFILE.USER_NAME where POST.POST_ID='{}'".format(id)).fetchone()
    
    return render_template("one.html",one=one,exe=exe,likers =likers,count_comments=count_comments,count_likers=count_likers,comments=comments)


@codekalp.route("/answer/<question_id>",methods=["GET","POST"])
def answer(question_id):

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    one = cursor.execute("select QUESTION.QUESTION_ID,QUESTION.DATE, QUESTION.QUEST_LANG,QUESTION.QUEST_CODE,QUESTION.QUEST_DESCRIPT,QUESTION.QUESTIONED_BY,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from QUESTION inner join PROFILE on QUESTION.QUESTIONED_BY=PROFILE.USER_NAME where QUESTION_ID='{}'".format(question_id)).fetchone()
    print(one)

    USER_NAME = session['LOGGED_USER']
    if request.method == "POST":
        get_answer = request.form['answer']
        get_desc = request.form["ans-desc"]
        print(get_answer)
        values_answer = (question_id,USER_NAME,get_answer,get_desc,DATE,TIME)
        insertion.answer(values_answer)
        return redirect(url_for('answered'))


    
   
    return render_template("answer.html",one=one,exe=exe)

@codekalp.route("/check")
def check():
    return render_template("title.html")


@codekalp.route("/answered")
def answered():

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    
    mix_db = ("""select ANSWER.ANSWERED_BY,ANSWER.DATE,ANSWER.ANSWER,ANSWER.ANS_DESC, QUESTION.QUESTION_ID, QUESTION.QUEST_LANG,QUESTION.QUEST_CODE,QUESTION.QUEST_DESCRIPT,QUESTION.QUESTIONED_BY,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from QUESTION join PROFILE on QUESTION.QUESTIONED_BY=PROFILE.USER_NAME
               
               join ANSWER on ANSWER.QUESTION_ID = QUESTION.QUESTION_ID order by ANSWER.DATE DESC """)
    display_all = cursor.execute(mix_db).fetchall()
    print(display_all)


    return render_template("answered.html",display_all = display_all,exe=exe)

@codekalp.route("/myprofile")
def myprofile():

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()
    user_own_post = cursor.execute("select POST.LIKES,POST.DATE, POST.LANG,POST.POST_CODE,POST.POST_DESCRIPT,POST.POSTED_BY ,POST.POST_ID,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from POST inner join PROFILE on POST.POSTED_BY=PROFILE.USER_NAME where POST.POSTED_BY='{}' order by POST.DATE".format(session['LOGGED_USER'])).fetchall()
    count_post = len(user_own_post)

    get_user_question = cursor.execute(f"select * from QUESTION where QUESTIONED_BY = '{session['LOGGED_USER']}' order by DATE").fetchall()
    count_questions = len(get_user_question)

    get_user_answer = cursor.execute(f"select * from ANSWER where ANSWERED_BY = '{session['LOGGED_USER']}' order by DATE").fetchall()
    count_answers = len(get_user_answer)
   

    print("userpost..",user_own_post)
    liked = cursor.execute("select * from CODEKALP").fetchall()
    print("liked",liked)

    signup_details = cursor.execute("select SIGN_UP.USER_ID,SIGN_UP.USER_NAME,PROFILE.PROFILE_PIC from SIGN_UP inner join PROFILE on SIGN_UP.USER_NAME=PROFILE.USER_NAME").fetchall()
        
    
    
    return render_template("profile.html",user_own_post=user_own_post,exe=exe,liked=liked,get_user_answer=get_user_answer,get_user_question=get_user_question,
                                    count_answers=count_answers,count_post=count_post,count_questions=count_questions)
                                

@codekalp.route("/authorquest")
def authorquest():

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    show_post = cursor.execute(f"select QUESTION.QUESTION_ID, QUESTION.QUEST_LANG,QUESTION.DATE,QUESTION.QUEST_CODE,QUESTION.QUEST_DESCRIPT,QUESTION.QUESTIONED_BY,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from QUESTION inner join PROFILE on QUESTION.QUESTIONED_BY = PROFILE.USER_NAME where QUESTION.QUESTIONED_BY = '{session['LOGGED_USER']}' order by QUESTION.DATE").fetchall()
    count_questions = len(show_post)
    

    return render_template("authorquestion.html",exe=exe,show_post=show_post,count_questions=count_questions)
@codekalp.route("/authoranswer")
def authoranswer():

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    mix_db = (f"""select ANSWER.ANSWERED_BY,ANSWER.DATE,ANSWER.ANSWER,ANSWER.ANS_DESC, QUESTION.QUESTION_ID, QUESTION.QUEST_LANG,QUESTION.QUEST_CODE,QUESTION.QUEST_DESCRIPT,QUESTION.QUESTIONED_BY,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from QUESTION join PROFILE on QUESTION.QUESTIONED_BY=PROFILE.USER_NAME
               
               join ANSWER on ANSWER.QUESTION_ID = QUESTION.QUESTION_ID where ANSWERED_BY = '{session["LOGGED_USER"]}' order by ANSWER.DATE""")
    display_all = cursor.execute(mix_db).fetchall()
    count_answer = len(display_all)

    return render_template("authoranswer.html",exe=exe,display_all=display_all,count_answer=count_answer)
    




@codekalp.route("/updatelike",methods=["POST"])
def updatelike():
    liked_post = request.form["likedpost"]
    liked_by = session['LOGGED_USER']
    liked_user_id = session["USER_ID"]
    checking_like = cursor.execute("select * from CODEKALP where LIKED_POST = '{}' and LIKER_ID = '{}'".format(liked_post,liked_user_id)).fetchone()
    if checking_like == None:
        values_like = (liked_post,liked_by,liked_user_id)
        insertion.likes(values_like)
    elif checking_like:
        cursor.execute("delete from CODEKALP where LIKED_POST = '{}' and LIKER_ID = '{}'".format(liked_post,liked_user_id))
        cursor.commit()
    counter_like = cursor.execute(f"select * from CODEKALP where LIKED_POST = '{liked_post}'").fetchall()
    counted = len(counter_like)

    #update like in post table with the respective post id
    cursor.execute(f"update POST set LIKES = '{counted}' where POST_ID = '{liked_post}'")
    cursor.commit()
    
    return jsonify({"counter":counted})


@codekalp.route("/onequestion/<username>")
def onequestion(username):

    show_post = cursor.execute(f"select QUESTION.QUESTION_ID, QUESTION.QUEST_LANG,QUESTION.QUEST_CODE,QUESTION.QUEST_DESCRIPT,QUESTION.QUESTIONED_BY,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from QUESTION inner join PROFILE on QUESTION.QUESTIONED_BY = PROFILE.USER_NAME where QUESTION.QUESTIONED_BY = '{username}'").fetchall()
    count_questions = len(show_post)
    print(show_post)
    

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    
    return render_template("userquestion.html",show_post=show_post,count_questions=count_questions,exe=exe)

@codekalp.route("/oneanswer/<a>")
def oneanswer(a):

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    mix_db = (f"""select ANSWER.ANSWERED_BY,ANSWER.ANSWER,ANSWER.ANS_DESC, QUESTION.QUESTION_ID, QUESTION.QUEST_LANG,QUESTION.QUEST_CODE,QUESTION.QUEST_DESCRIPT,QUESTION.QUESTIONED_BY,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from QUESTION join PROFILE on QUESTION.QUESTIONED_BY=PROFILE.USER_NAME
               
               join ANSWER on ANSWER.QUESTION_ID = QUESTION.QUESTION_ID where ANSWERED_BY = '{a}' """)
    display_all = cursor.execute(mix_db).fetchall()
    count_answer = len(display_all)

    return render_template('useranswer.html',exe=exe,display_all=display_all,count_answer=count_answer)




@codekalp.route("/profileclicked/<userid>")
def clickedprofile(userid):

    

    get_selected_user_post = cursor.execute("select POST.LIKES, POST.LANG,POST.POST_CODE,POST.POST_DESCRIPT,POST.POSTED_BY ,POST.POST_ID,PROFILE.USER_BIO,PROFILE.PROFILE_PIC from POST inner join PROFILE on POST.POSTED_BY=PROFILE.USER_NAME where POST.POSTED_BY='{}'".format(userid)).fetchall()
    print(get_selected_user_post)
    count_post = len(get_selected_user_post)
    print(count_post)

    get_selected_user_question = cursor.execute(f"select * from QUESTION where QUESTIONED_BY = '{userid}'").fetchall()
    count_questions = len(get_selected_user_question)

    get_selected_user_answer = cursor.execute(f"select * from ANSWER where ANSWERED_BY = '{userid}'").fetchall()
    count_answers = len(get_selected_user_answer)
    
    user_img = cursor.execute("select * from PROFILE where USER_NAME = '{}'".format(userid)).fetchone()

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

   
    
    return render_template("clicked.html",exe=exe,user_img=user_img,
                                          count_post=count_post,
                                          get_selected_user_post=get_selected_user_post,
                                          count_questions=count_questions,
                                          count_answers=count_answers)

@codekalp.route("/editpost/<update>",methods=["POST","GET"])
def editpost(update):

    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()


    one = cursor.execute(f"select * from POST where POST_ID = '{update}'").fetchone()
    
    

    if request.method == "POST":
        
        LANGUAGE = request.form["lang"]
        
        POST_CODE = request.form["ale"]
        DESCRIPT = request.form["description"]
        cursor.execute(f"update POST set POST_CODE = '{POST_CODE}' ,LANG = '{LANGUAGE}' where POST_ID = '{update}' ")
        FILE_OPEN = open("USER_FILES/{}{}".format(update,LANGUAGE),"w")
        writing = FILE_OPEN.write(POST_CODE)
        return redirect(url_for('myprofile'))

    

    return render_template("editpost.html",one=one,exe=exe)
    

@codekalp.route("/deletepost/<did>")
def deletepost(did):
    print(did)
    cursor.execute(f"delete from POST where POST_ID = '{did}'")
    cursor.commit()
    return redirect(url_for('myprofile'))

@codekalp.route("/deletequest/<dqd>")
def deletequest(dqd):
    print(dqd)
    cursor.execute(f"delete from QUESTION where QUESTION_ID = '{dqd}'")
    cursor.commit()
    return redirect(url_for('authorquest'))

@codekalp.route("/download/<dpid>/<lg>")
def download(dpid,lg):
    path = f"USER_FILES/{dpid}{lg}"
    return send_file(path,as_attachment=True)

@codekalp.route("/results",methods=["GET","POST"])
def results():
    result = request.form["resultsdata"]

    searching_db = cursor.execute(f"select * from PROFILE where USER_NAME  LIKE '{result}%' ").fetchall()
    print(searching_db)

    return jsonify({"message":"your results.","response":render_template("results.html",searching_db=searching_db)})


@codekalp.route("/search..")
def search():
    Profile_display = ("select * from PROFILE where USER_NAME='{}'".format(session['LOGGED_USER']))
    exe = cursor.execute(Profile_display).fetchone()

    return render_template("searchbar.html",exe=exe)
        

    

@codekalp.route("/logout")
def logout():
    session.pop("LOGGED_USER",None)
    return redirect(url_for('login'))


if __name__ == ("__main__"):
    # app.run(debug=True)
    codekalp.run(debug=True)
    