#coding=utf-8
import configparser
import os
__author__ = 'lgx'

class RedisConf(object):

    def __init__(self):
        pass

    def write_cfg(self, file_path, env, host, port, password):
        conf = configparser.ConfigParser()

        conf.add_section(env)
        conf.set(env, 'host', host)
        conf.set(env, 'port', port)
        conf.set(env, 'password', password)

        conf.write(open(file_path, 'w'))

    def read_cfg(self, file_path):
        conf = configparser.ConfigParser()
        conf.read(file_path)

        env_list = conf.sections()
        if env_list is None or len(env_list) == 0:
            return None
        else:
            env = env_list[0]
        host = conf.get(env, 'host')
        port = conf.get(env, 'port')
        password = conf.get(env, 'password')

        return (host, port, password, env)

    def clear_cfg(self):
        folder_path = os.getcwd()+'\\redis_conf.cfg'
        with open(folder_path,mode='w') as f:
            f.write('')