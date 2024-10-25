# -*- coding: utf-8 -*-
import time 
import oss2

import configparser
from itertools import islice
import os
from urllib.parse import quote
import atexit

class OssUtils():
    def __init__(self,) -> None:
        '''
        Ali oss Help Function: Automatically reads the configs under the "./config" path and connects to the oss server.
        There are two prefixes in the config file.
        image_prefix: the prefix of the image folder in the oss bucket;
        prj_prefix: the prefix of the project folder in the oss bucket.                                                                                       
        '''
        config = configparser.ConfigParser()
        # config.ini位于脚本同级目录下
        
        # Check if the .emalioss.ini file exists in the user's home directory
        home_dir = os.path.expanduser("~")
        emalioss_config_path = os.path.join(home_dir, 'emalioss.ini')


        if os.path.exists('./emalioss.ini'):
            config.read('./emalioss.ini')
        elif os.path.exists(emalioss_config_path):
            config.read(emalioss_config_path)
        else:
            raise FileNotFoundError("Config file not found")


        # read config
        access_key_id = config.get('ossconfig', 'alibaba_cloud_access_key_id')
        access_key_secret = config.get('ossconfig', 'alibaba_cloud_access_key_secret')
        bucket_name = config.get('ossconfig', 'bucket')
        self.bucket_name = bucket_name 
        endpoint = config.get('ossconfig', 'endpoint')
        region = config.get('ossconfig', 'region')

        self.image_prefix = config.get('imageprefix', 'prefix')
        self.prj_prefix = config.get('prjprefix', 'prefix')

        print("[oss_utils]image prefix: "+self.image_prefix)
        print("[oss_utils]project prefix: "+self.prj_prefix)

        # 使用获取的RAM用户的访问密钥配置访问凭证
        self.auth = oss2.AuthV4(access_key_id, access_key_secret)
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name, region=region)
        self.bucket.timeout = 4
        self.oss_global_base_url = "https://" + bucket_name +"."+ endpoint.split("//")[1]
        print("[oss_utils]base_url: "+self.oss_global_base_url)
        try:
            self.bucket_info = self.bucket.get_bucket_info()
        except oss2.exceptions.OssError as e:
            print(f"Failed to connect to OSS: {e}")
            raise ConnectionError("Failed to connect to OSS") from e
        
        atexit.register(self.clear_temp_dir)
        self.latest_upload_url = ""
    def get_folder_list(self,prefix):
        '''
        获取 buckt prefix 路径下的所有文件夹
        '''
        folder_list = []
        try:
            for b in oss2.ObjectIterator(self.bucket,prefix=prefix):
                if(self.is_directory(b.key)):
                    folder_list.append(b.key)
        except oss2.exceptions.RequestError as e:
            print(f"[get_folder_list]Failed to connect to OSS: {e}")
            raise ConnectionError("Failed to connect to OSS") from e

        # print(f"folder list: {folder_list}")
        return folder_list
    def get_all_files(self,prefix):
        '''
        获取 bucket prefix 路径下的所有文件
        '''
        file_list = []
        for b in oss2.ObjectIterator(self.bucket,prefix=prefix):
            file_name = b.key.replace(prefix+"/","", 1)

            file_list.append(file_name)
        print(f"[ossUtils]file list: {file_list}")
        return file_list


    def upload(self,oss_folder_path,local_file_path:str,file_name:str=None):
        '''
        上传文件到oss

        :param oss_folder_path: oss上的文件夹路径
        :param local_file_path: 本地文件的全局路径
        '''
        # 如果oss_folder_path不以/结尾,则加上/
        if(oss_folder_path[-1] != "/"):
            oss_folder_path = oss_folder_path + "/"
        else:
            oss_folder_path = oss_folder_path
        if(file_name is None):
            osspath = oss_folder_path + local_file_path.split("/")[-1]
        else:
            osspath =  oss_folder_path + file_name
        global_url = f"{self.oss_global_base_url}/{osspath}"
        try:
            self.bucket.put_object_from_file(key=osspath, filename=local_file_path)
            print(f"upload success: {osspath}")
            self.latest_upload_url = global_url
        except oss2.exceptions.RequestError as e:
            print(f"Failed to connect to OSS: {e}")
            raise ConnectionError("Failed to connect to OSS") from e
        return global_url

    def get_latest_upload_url(self):
        '''获取最近一次上传的文件的url'''
        return quote(self.latest_upload_url, safe=':/')
    
    def download(self, oss_file_path:str, local_file_name:str):
        '''
        下载 OSS 上的文件到本地。

        :param oss_file_path: OSS 上的文件路径。
        :param local_file_name: 本地文件路径。
        '''
        
        try:
            self.bucket.get_object_to_file(oss_file_path, local_file_name)
            print('download success')
        except oss2.exceptions.RequestError as e:
            print(f"Failed to connect to OSS: {e}")
            raise ConnectionError("Failed to connect to OSS") from e

    def delete(self,oss_local_path,prefix=None):
        '''删除oss上的文件或文件夹'''
        # 区分oss_local_path是否是文件夹
        oss_path=oss_local_path
        if(self.is_directory(oss_path)):
            oss_path= oss_path + "/"
            print("[delete] oss folder path:"+oss_path)
            for obj in oss2.ObjectIterator(self.bucket, prefix=oss_path):
                self.bucket.delete_object(obj.key)
            # TODO: 判断文件是否删除成功
            return True
        else:
            print("[delete] oss file path:"+oss_path)
            result = self.bucket.delete_object(oss_local_path)
            return True
        # print('\n'.join(result.deleted_keys))            

    def create_folder(self,folder_name:str):
        '''
        在OSS 的bucket中创建文件夹
        '''
        try:
            local_path = folder_name+"/"
            print("local_path: "+local_path)
            if self.bucket.put_object(local_path, '').status == 200:
                print('创建目录成功')
                return True
            print('创建目录失败')
            return False
        except:
            return False
    def is_directory(self,path:str):
        """
        判断path是否是文件夹,依据是否有后缀名,路径可以时局部路径或者全局路径
        """
        return not os.path.splitext(path)[1]  # 如果没有后缀名，则是文件夹
    def get_path_suffix(self,path:str):
        '''
        获取路径的后缀名
        '''
        return os.path.splitext(path)[1]
    def get_resize_image(self,key,resize_style:int=-1):
        temp_dir = "./tmp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        current_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        temp_file_path = os.path.join(temp_dir, f"image_{current_time}.png")
        # print(temp_file_path)
        if(resize_style < 0):
            self.bucket.get_object_to_file(key, temp_file_path)
        else:
            style = f'image/resize,mfit,w_{resize_style},h_{resize_style}'
            self.bucket.get_object_to_file(key, temp_file_path, process=style)
        return temp_file_path
    def clear_temp_dir(self):
        temp_dir = "./tmp"
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
        print("clear temp dir success")
    def rename(self,old_path:str,new_path:str):
        '''重命名文件'''
        try:
            if self.is_directory(old_path):
                if(self.is_directory(new_path) is False):
                    print("文件夹不能重命名为文件")
                    raise ValueError("文件夹不能重命名为文件")
                for obj in oss2.ObjectIterator(self.bucket, prefix=old_path):
                    old_object_key = obj.key
                    new_object_key = old_object_key.replace(old_path, new_path, 1)
                    new_object_key = new_object_key
                    print("[rename] new folder path:"+new_object_key)
                    self.bucket.copy_object(self.bucket_name, old_object_key, new_object_key)
                    self.bucket.delete_object(old_object_key)
            else:
                if(self.get_path_suffix(old_path) != self.get_path_suffix(new_path)):
                    new_path = new_path + self.get_path_suffix(old_path)
                self.bucket.copy_object(self.bucket.bucket_name, old_path, new_path)
                self.bucket.delete_object(old_path)
            return new_path.split("/")[-1]
        except oss2.exceptions.RequestError as e:
            print(f"Failed to connect to OSS: {e}")
            raise ConnectionError("Failed to connect to OSS") from e


    # def iter_files(self):
    #     # oss2.ObjectIterator用于遍历文件。
    #     for b in islice(oss2.ObjectIterator(self.bucket,prefix=self.image_prefix), 20):
    #         print(type(b.key))

if __name__ == "__main__":
    oss_utils = OssUtils()
    print(oss_utils.get_folder_list())

