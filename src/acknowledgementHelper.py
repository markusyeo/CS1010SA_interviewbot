import hashlib
import logging
import json
from env import keyfilename
from os.path import exists

class AcknowledgementHelper:
    def __init__(self, client):
        self.client = client
        self.keys = {}
        self.names = {}
        self.filename = keyfilename
        self.load_keys()
    
    async def generate_keys(self, name, keyToHash):
        hashedKey = self.hash_key(keyToHash)
        if hashedKey in self.keys:
            logging.info(f"Key {hashedKey} already exists")
        else:
            self.keys[hashedKey] = {'name': name, 'acknowledged': False}
            await self.save_keys()
            return hashedKey
    
    def hash_key(self, key):
        hashedKey = hashlib.shake_256(key.encode('utf-8')).hexdigest(5)
        return hashedKey
    
    async def delete_key(self, key):
        if key in self.keys:
            name = self.keys[key]['name']
            del self.keys[key]
            await self.save_keys()
            return True, name
        else:
            return False, None
            logging.info(f"Key {key} does not exist")

    async def check_key(self, key):
        if key in self.keys and self.keys[key]['acknowledged'] == False:
            self.keys[key]['acknowledged'] = True
            await self.save_keys()
            return self.keys[key]['name'], True
        else:
            return None, False
    
    async def get_keys(self):
        msg = ''
        if len(self.keys) == 0:
            return "No keys generated yet"
        for k,v in self.keys.items():
            msg += f"{v['name']}: {k} ({v['acknowledged']})\n"
        return msg
    
    async def registerUserId(self, hashedKey, user_id):
        if user_id in self.names:
            logging.info(f"User {user_id} already exists")
        self.names[user_id] = self.keys[hashedKey]['name']
    
    async def getName(self, user_id):
        return self.names.get(user_id)
    
    async def save_keys(self):
        f = open(self.filename, 'w')
        f.write(json.dumps(self.keys))
        f.close()

    def load_keys(self):
        if exists(self.filename):
            f = open(self.filename, 'r')
            self.keys = json.loads(f.read())
        else:
            f = open(self.filename, 'w')
            f.write(json.dumps(self.keys))
        f.close()