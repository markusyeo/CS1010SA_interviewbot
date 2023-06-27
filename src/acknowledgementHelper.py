import hashlib
import logging

class acknowledgementHelper:
    def __init__(self, client):
        self.client = client
        self.keys = {}
        self.names = {}
    
    def generate_keys(self, name, keyToHash):
        hashedKey = self.hash_key(keyToHash)
        if hashedKey in self.keys:
            logging.info(f"Key {hashedKey} already exists")
        else:
            self.keys[hashedKey] = {'name': name, 'acknowledged': False}
            return hashedKey
    
    def hash_key(self, key):
        hashedKey = hashlib.shake_256(key.encode('utf-8')).hexdigest(5)
        return hashedKey
    
    def delete_key(self, key):
        try:
            del self.keys[key]
            return True
        except:
            return False
            logging.info(f"Key {key} does not exist")

    async def check_key(self, key):
        if key in self.keys and self.keys[key]['acknowledged'] == False:
            self.keys[key]['acknowledged'] = True
            return self.keys[key]['name'], True
        else:
            return None, False
    
    async def get_keys(self):
        msg = ''
        for k,v in self.keys.items():
            msg += f"{v['name']}: {k}\n"
        return msg
    
    async def registerUserId(self, hashedKey, user_id):
        if user_id in self.names:
            logging.info(f"User {user_id} already exists")
        self.names[user_id] = self.keys[hashedKey]['name']
    
    async def getUserId(self, user_id):
        return self.names.get(user_id)