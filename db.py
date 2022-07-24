
import pyodbc
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







class insert:
    def signup(self,values_signup):
        query =("insert into SIGN_UP values(?,?,?,?,?,?,?)")
        cursor.execute(query,values_signup)
        cursor.commit()
    def post(self,values_post):
        query = ("insert into POST values(?,?,?,?,?,?,?,?)")
        cursor.execute(query,values_post)
        cursor.commit()
    def profile(self,values_profile):
        query = ("insert into PROFILE values(?,?,?,?)")
        cursor.execute(query,values_profile)
        cursor.commit()
    
    def question(self,values_question):
        query = ("insert into QUESTION values(?,?,?,?,?,?,?)")
        cursor.execute(query,values_question)
        cursor.commit()

    def answer(self,values_answer):
        query = ("insert into ANSWER values(?,?,?,?,?,?)")
        cursor.execute(query,values_answer)
        cursor.commit()
    
    def message(self,values_message):
        query = ("insert into MSG values(?,?,?,?,?)")
        cursor.execute(query,values_message)
        cursor.commit()
    def comments(self,values_comments):
        query = ("insert into COMMENT values(?,?,?,?,?)")
        cursor.execute(query,values_comments)
        cursor.commit()
    
    def likes(self,values_likes):
        query = ("insert into CODEKALP values(?,?,?)")
        cursor.execute(query,values_likes)
        cursor.commit()
    


