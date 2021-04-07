
# Datetime
import json  
from os.path import basename 
import traceback 
from pprint import pprint 
from utils.str import Str, log
import datetime 


class Users:

    def __init__(self):
        self.users = {}
        res = list(self.db.users.find())
        for u in res: 
            self.users[ u['user_id'] ] = u

       
    def update_user( self, user_id, info ):

        db_update = False 

        for k,v in info.items():
            pprint('%s - %s' % (k, v))
            self.users[user_id][k] = v
            if k not in self.users[user_id]:
                db_update = True 
            else:
                if self.users[user_id][k] != v:
                    db_update = True 
            

        if db_update == True: 
            try:
                self.db.users.update_one( { 'user_id': user_id }, { "$set": info }, upsert=True)
            except Exception as e:
                log.error('Unable to update user db for user_id: %s, data %s' % (user_id, info))
                pprint(e)
        

    def update_user_room( self, user_id, chat_id, status ):
        print('update_user_room')
        if 'rooms' not in self.users[user_id]:
            self.users[user_id]['rooms'] = {}

        self.users[user_id]['rooms'][str(chat_id)] = status
       
        try:
            # self.db.users.update_one( { 'user_id': user_id }, { "$set": self.users[user_id] }, upsert=True)
            self.db.users.update_one( { 'user_id': user_id }, { "$set":  self.users[user_id] }, upsert=True)
        except Exception as e:
            pprint(e)
            log.error('db insert errror, user_id: %s, info: %s' % (user_id, self.users[user_id]))

        return 

    def del_user_room( self, user_id, chat_id ):
        print('del user _room')
        if 'rooms' not in self.users[user_id]:
            print('rooms not in users info.. ')
            return

        if str(chat_id) not in self.users[user_id]['rooms']:
            print(str(chat_id)+' not in rooms.. ')
            pprint(self.users[user_id]['rooms'])
            return

        del self.users[user_id]['rooms'][str(chat_id)]

        try:
            # self.db.users.update_one( { 'user_id': user_id }, { "$set": self.users[user_id] }, upsert=True)
            self.db.users.update_one( { 'user_id': user_id }, { "$set":  self.users[user_id] }, upsert=True)
        except Exception as e:
            pprint(e)
            log.error('db insert errror, user_id: %s, info: %s' % (user_id, self.users[user_id]))

        return 

    
    def check_user_exists( self, user_id, name, username ):

        if user_id in self.users:
            return

        timestamp = datetime.datetime.utcnow()
        info = {
            'user_id': user_id,
            'name': name,
            'username': username,
            'last_seen': timestamp
        }
        self.users[user_id] = info 
        try:
            self.db.users.update_one( { 'user_id': user_id }, { "$set": info }, upsert=True)
        except Exception:
            log.error('db insert errror, user_id: %s, info: %s' % (user_id, info))

        return 
