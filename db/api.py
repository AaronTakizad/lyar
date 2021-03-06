import sqlite3
import os.path
from . import passwordhash

if os.path.exists('db'):
    con = sqlite3.connect('db/database.db')
else:
    con = sqlite3.connect('database.db')

#Class for the question table
class Question:
    def __init__(self, qid, statement0, statement1, statement2, lie, creator_id, name=''):
        self.qid = qid
        self.statement0 = statement0
        self.statement1 = statement1
        self.statement2 = statement2
        self.lie = lie
        self.name = name
        self.creator_id = creator_id

    # returns the user object of the creator.
    def get_creator(self):
        return User.find(uid=self.creator_id)

# Function for creating questions in the database.
    @classmethod
    def create(cls, statement0, statement1, statement2, lie, creator_id, name=''):
        id_find = con.execute('''SELECT id FROM question ORDER BY id DESC LIMIT 1;''')
        row = id_find.fetchone()
        qid = int(row[0]) + 1
        cur = con.execute('''INSERT INTO question VALUES(?, ?, ?, ?, ?, ?, ?);''', (qid, statement0, statement1, statement2, lie, creator_id, name))
        con.commit()
        return cls(qid, statement0, statement1, statement2, lie, creator_id, name)

# Function for finding questions in the database, run with the class.
    @classmethod
    def find(cls, qid):
        cur = con.execute('''SELECT * FROM question WHERE id=?''', (qid, ))
        locate = cur.fetchone()
        if locate == None:
            return None
        qid, statement0, statement1, statement2, lie, creator_id, name = locate
        return cls(qid, statement0, statement1, statement2, lie, creator_id, name)

# Function for deleting questions in the database, must run with a question object e.g. (quest_obj.delete()).
    def delete(self):
        cur = con.execute('''DELETE FROM question WHERE id=?;''', (self.qid, ))#must be a tuple
        con.commit()
        return True

#Function to find all questions if no argument is supplied. If an argument is supplied (creator_id) it acts as a filter to find specific entries based on creator_id.
    @classmethod
    def find_all(self, creator_id=None):
        query = con.execute('''SELECT * FROM question WHERE creator_id=?  ''', (creator_id,))
        if creator_id is None:
            query = con.execute('''SELECT * FROM question''')
        all_rows = query.fetchall()
        return [Question(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in all_rows]

    @classmethod
    def find_all_home_specific(self, creator_id=None):
        query = con.execute('''SELECT * FROM question WHERE creator_id = ?;''', (creator_id,))
        if creator_id is None:
            query = con.execute('''SELECT * FROM question ORDER BY id DESC;''')
        all_rows = query.fetchall()
        return [Question(row[0], row[1], row[2], row[3], row[4], row[5], row[6]) for row in all_rows]
        
    def __repr__(self):
        return 'id: {}, s0: {}, s1: {}, s2: {}, lie: {}, name: {}, creator: {}'.format(self.qid, self.statement0, self.statement1, self.statement2, self.lie, self.name, self.creator_id)

#Class for the vote table
class Vote:
    def __init__(self, vid, qid, vote, voter_id):
        self.vid = vid
        self.qid = qid
        self.vote = vote
        self.voter_id = voter_id
        
    #The function to create a vote and add it to the database, returns a vote object
    @classmethod
    def create(self, qid, vote, voter_id):
        id_find = con.execute('''SELECT id FROM vote ORDER BY id DESC LIMIT 1;''')
        row = id_find.fetchone()
        vid = row[0] + 1
        cur = con.execute('''INSERT INTO vote VALUES(?, ?, ?, ?);''', (vid, qid, vote, voter_id))
        con.commit()
        return Vote(vid, qid, vote, voter_id)
    
    #The function to find a vote based on it's vid (vote id) which is unique returns a vote object
    @classmethod
    def find(self, vid):
        query = con.execute('''SELECT * FROM vote WHERE ? = id;''', (vid,))
        row = query.fetchone()
        if row is None:
            return None
        return Vote(row[0], row[1], row[2], row[3])
    
    #The function to delete a vote object from the database, run it with a vote object
    def delete(self):
        con.execute('''DELETE FROM vote WHERE ? = id;''', (self.vid,))
        con.commit()
        return True
    
    #The function to find all votes if no argument is supplied. If an argument is supplied, it is treated as a filter to find specific entries. 
    
    @classmethod
    def find_all(self, qid=None, vote=None, voter_id=None):
        filters = []
        sql_string = []
        sql_and = ' AND '
        if qid is not None:
            filters.append(qid)
            sql_string.append('''qid = ?''')
        if vote is not None:
            filters.append(vote)
            sql_string.append('''vote = ?''')
        if voter_id is not None:
            filters.append(voter_id)
            sql_string.append('''voter_id = ?''')
        query = sql_and.join(sql_string)
        filters = tuple(filters)
        sql_command = '''SELECT * FROM vote WHERE '''
        query = (sql_command + query)
        if filters == ():
            cur = con.execute('''SELECT * FROM vote''')
        else:
            cur = con.execute(query,filters)
        all_result = cur.fetchall()
        votes = []
        for result in all_result:
            votes.append(Vote(result[0], result[1], result[2], result[3]))
        return votes

    @classmethod
    def number_of_correct_votes(cls, voter_id = None):
        sql_command = '''SELECT count(*) FROM question q JOIN vote v ON (q.id = v.qid) WHERE q.lie = v.vote'''
        if voter_id is None:
            cur = con.execute(sql_command)
        else:
            filters = (voter_id,)
            cur = con.execute(sql_command + " and v.voter_id=?",filters)
        result = cur.fetchone()[0]
        # print("number of correct votes:", result)
        return result

    def __repr__(self):
        return 'id: {} qid: {} vote: {} voter: {}'.format(self.vid, self.qid, self.vote, self.voter_id)

# Class for the user table
class User:

    def __init__(self, uid, username, password, points = 0):
        self.uid = uid
        self.username = username
        self.password = password.encode('ascii')
        self.points = points

    @classmethod
    def hash_password(cls, password):
        return passwordhash.hash_password(password)

    # Function for creating users in the database.
    @classmethod
    def create(cls, username, password):
        id_find = con.execute('''SELECT id FROM user ORDER BY id DESC LIMIT 1;''')
        row = id_find.fetchone()
        uid = int(row[0]) + 1
        cur = con.execute('''INSERT INTO user VALUES(?, ?, ?, 0);''', (uid, username, password))
        con.commit()
        return cls(uid, username, password, 0)

    # Function for finding users in the database.
    @classmethod
    def find(cls, username=None, uid=None):
        filters = []
        sql_string = []
        sql_and = ' AND '
        if uid is not None:
            filters.append(uid)
            sql_string.append('''id = ?''')
        if username is not None:
            filters.append(username)
            sql_string.append('''username = ?''')
        query = sql_and.join(sql_string)
        filters = tuple(filters)
        sql_command = '''SELECT * FROM user WHERE '''
        query = (sql_command + query)
        if filters == ():
            cur = con.execute('''SELECT * FROM user''')
        else:
            cur = con.execute(query,filters)
        all_result = cur.fetchone()
        if all_result == None:
            return None
        uid, username, password, points = all_result
        return cls(uid, username, password, points)

    #Function for adding points to the user object
    def add_points(self, points = 1):
        self.points += points
        #print("THIS SHOULD HAPPEN")
        #print(self.points)
        cur = con.execute('''UPDATE user SET points = ? WHERE id = ?;''', (self.points, self.uid))
        con.commit()
        cur = con.execute('''SELECT points FROM user WHERE id = ?''', (self.uid, ))
        row = cur.fetchone()[0]
        #print(row)
        return row

    # Function for deleting users in the database.
    def delete(self):
        cur = con.execute('''DELETE FROM user WHERE id=?''', (self.uid, ))
        con.commit()
        return True

    def __repr__(self):
        return 'id: {}, username: {}, password: {}, points: {}'.format(self.uid, self.username, self.password, self.points)

    # Function for listing all usernames and passwords (debugging only)
    @classmethod
    def find_all(cls):
        all_users = con.execute('''SELECT * FROM user ORDER BY id ASC''')
        rows = all_users.fetchall()
        output = []
        for u in rows:
            uid, username, password, points = u
            out = cls(uid, username, password, points)
            output.append(out)
        return output

    @classmethod
    def find_best(cls, limit):
        limit = str(limit)
        best_users = con.execute('''SELECT * FROM user ORDER BY points DESC LIMIT ?''', (limit,))
        rows = best_users.fetchall()
        output = []
        for u in rows:
            uid, username, password, points = u
            out = cls(uid, username, password, points)
            output.append(out)
        return output

        
    def update(self, username=None, password=None):
        filters = []
        sql_string = []
        sql_and = ', '
        if username is not None:
            filters.append(username)
            sql_string.append('''username = ? ''')
        if password is not None:
            filters.append(password)
            sql_string.append('''password = ? ''')
        query = sql_and.join(sql_string)
        filters.append(self.uid)
        end = '''WHERE id = ?;'''
        filters = tuple(filters)
        sql_command = '''UPDATE user SET '''
        query = (sql_command + query)
        if filters == ():
            return False
        else:
            query = query + end
            cur = con.execute(query, filters)
        output = cur.fetchone()
        con.commit()
        return True
