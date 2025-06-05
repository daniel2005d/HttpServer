import json
import os

class Settings:
    paths=[]
    port=8000
    initial_folder = os.getcwd()
    

    @classmethod
    def to_dict(cls):
        return {
            "paths":cls.paths,
            "port":cls.port,
            "start_folder":cls.initial_folder
        }
    
    @classmethod
    def to_json(cls):
        return json.dumps(cls.to_dict(), indent=4)
    
    @classmethod
    def from_dict(cls, data):
        cls.paths = data.get("paths","[]")
        cls.port = data.get("port", 8000)
        cls.initial_folder = data.get("start_folder", os.getcwd())
    
    @classmethod
    def from_json(cls, path):
        with open(path, 'r') as jsonfile:
            data = json.loads(jsonfile.read())
            cls.from_dict(data)



    


