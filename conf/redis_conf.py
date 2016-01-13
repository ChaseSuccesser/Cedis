#coding=utf-8
import configparser
import os
__author__ = 'lgx'

class RedisConf(object):

    def __init__(self):
        pass

    def write_cfg(self, env, host, port, password):
        folder_path = os.getcwd()+'\\redis_conf.cfg'
        conf = configparser.ConfigParser()

        conf.add_section(env)
        conf.set(env, 'host', host)
        conf.set(env, 'port', port)
        conf.set(env, 'password', password)

        conf.write(open(folder_path, 'w'))

    def read_cfg(self):
        folder_path = os.getcwd()+'\\redis_conf.cfg'
        conf = configparser.ConfigParser()
        conf.read(folder_path)

        env = conf.sections()[0]
        host = conf.get(env, 'host')
        port = conf.get(env, 'port')
        password = conf.get(env, 'password')

        return (host, port, password, env)

    def clear_cfg(self):
        folder_path = os.getcwd()+'\\redis_conf.cfg'
        with open(folder_path,mode='w') as f:
            f.write('')