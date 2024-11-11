import os
import shutil
import re
import hashlib
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import threading


class FolderSynch:
    def __init__(self, source_path, replica_path, synch_interval, log_path):
        self.source_path = source_path
        self.replica_path = replica_path
        self.synch_interval = synch_interval
        self.log_path = log_path
        
        self.log = self.get_logger()
        self.files_hash = {}
    
    
    def get_logger(self):
        formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        file_handler = TimedRotatingFileHandler(self.log_path + "synch.log", when='midnight')
        file_handler.setFormatter(formatter)
        
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG) 
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        logger.propagate = False
        
        return logger
    
    def synch(self):
        source = self.get_content(self.source_path)
        replica = self.get_content(self.replica_path)
        for file in source:
            source_file_name = os.path.join(self.source_path, file)
            replica_file_name = os.path.join(self.replica_path, file)
            
            if file not in replica:
                self.copy_file(source_file_name, replica_file_name)
                continue
            
            if os.path.isfile(source_file_name) and not self.compare_hash(source_file_name, replica_file_name):
                self.copy_file(source_file_name, replica_file_name)
            
            replica.remove(file)
        
        if replica != []:
            for file in replica:
                replica_file_name = os.path.join(self.replica_path, file)
                self.remove_file(replica_file_name)
        
        self.start_scheduler()
    
    
    def get_content(self, path):
        file_list = []
        for root, folders, files in os.walk(path):
            relative_root = os.path.relpath(root, path)
            files = folders + files
            
            for file in files:
                file_list.append(os.path.join(relative_root, file).replace("./", ""))
                
        return file_list


    def copy_file(self, source_path, replica_path):
        if os.path.isdir(source_path):
            os.makedirs(replica_path)
            self.log.info("Created folder: " + replica_path)
            return
        
        shutil.copy2(source_path, replica_path)
        self.log.info("Copied file: " + replica_path)
        
        
    def remove_file(self, path):
        if os.path.isdir(path):
            shutil.rmtree(path)
            self.log.info("Removed folder: " + path)
            return

        os.remove(path)
        self.log.info("Removed file: " + path)
        
        
    def compare_hash(self, source_path, replica_path):
        if replica_path not in self.files_hash:
            self.files_hash[replica_path] = self.get_hash(replica_path)

        return self.get_hash(source_path) == self.files_hash[replica_path]
        
        
    def get_hash(self, path):
        with open(path, "rb") as file:
            digest = hashlib.file_digest(file, "sha256")
        
        return digest.hexdigest()


    def start_scheduler(self):   
        threading.Timer(self.synch_interval * 60, self.synch).start()

if __name__ == "__main__":
    #FIXME add help
    #FIXME add input args
    #FIXME add comments
    folder_synch = FolderSynch("/home/skillflame/Documents/Folder_synch/Source", "/home/skillflame/Documents/Folder_synch/Replica", 1, "/home/skillflame/Documents/Folder_synch/Log/")
    folder_synch.synch()
    