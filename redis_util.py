#coding=utf-8
__author__ = 'lgx'

import redis
import time
import datetime
import json

class RedisUtil(object):

    def __init__(self,db):
        self.db = db

    def getRedisConnection(self):
        """
        get connection of Redis
        :return:
        """
        redisConn = redis.Redis(host='123.57.66.199', port='6379', db=self.db, password='eyuankuwant')
        # redisConn = redis.Redis(host='127.0.0.1', port='6379', db=self.db)
        return redisConn

    def getKeyValue(self, type, key, field):
        """
        获取缓存的值
        :param type:
        :param key:
        :param field:
        :return:
        """
        redisConn = self.getRedisConnection()

        if type == 'string':
            value = redisConn.get(key)
            return value
        elif type == 'hash':
            hash_field_list = [item.decode('utf-8') for item in redisConn.hkeys(key)]
            return hash_field_list
        elif type == 'set':
            set_fields = redisConn.smembers(key)
            set_fields_list = []
            for item in set_fields:
                set_fields_list.append(item.decode('utf-8'))
            return set_fields_list
        elif type == 'list':
            return '没有API支持直接从list集合获取所有记录，或按索引获取记录'
        elif type == 'hash_field':
            try:
                hash_field_value = redisConn.hget(key, field).decode('utf-8')
            except Exception:
                hash_field_value = redisConn.hget(key, field)
            return hash_field_value
        elif type == 'set_field':
            return '没有API支持从set集合中按指定的field获取value.'


    def getAllKeys(self):
        """
        获取当前数据库中所有的key
        :return:list
        """
        redisConn = self.getRedisConnection()

        allKeys = redisConn.keys('*')
        key_detail_info_list = []
        format = '%Y-%m-%d %H:%M:%S'
        for key in allKeys:
            key_expire_time = datetime.datetime.fromtimestamp(int(time.time())+redisConn.ttl(key)).strftime(format) if redisConn.ttl(key) is not None else ''
            key_type = redisConn.type(key).decode('utf-8')
            key_detail_info_list.append(key.decode('utf-8')+'   '+key_type+'   超时时间:'+key_expire_time)
        return key_detail_info_list


    def delKey(self, key):
        """
        删除缓存
        :param key:
        :return:
        """
        redisConn = self.getRedisConnection()
        redisConn.delete(key)