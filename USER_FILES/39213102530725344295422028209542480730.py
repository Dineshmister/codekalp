@app.route("/inbox")
def inbox():
    received = session['USER_ID']
    inbox = cursor.execute("select POSTED.COUNT_OF_LIKES, POSTED.POST_ID,POSTED.POST_CODE,POSTED.DESCRIPTION,POSTED.POSTED_BY,MSG.SENDER,PROFILE.PROFILE_PIC from POSTED join MSG on POSTED.POST_ID = MSG.MESSAGE join PROFILE on POSTED.POSTED_BY=PROFILE.USER_NAME where MSG.RECEIVER = '{}'".format(received)).fetchall()
    check_inbox_count = len(inbox)
    print(inbox,check_inbox_count)
    return render_template('inbox.html',inbox=inbox,check_inbox_count=check_inbox_count)
