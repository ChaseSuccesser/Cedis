#coding=utf-8
__author__ = 'lgx'

import redis
import time
import datetime
import os
from conf.redis_conf import RedisConf

class RedisUtil(object):

    def __init__(self, db):
        self.db = db

    def testConnection(self, host, port, password):
        """
        测试是否能成功连接Redis
        :return:Bool
        """
        try:
            redis_conn = redis.Redis(host=host, port=port, password=password)
            redis_conn.ping()
            return True
        except Exception:
            return False

    def _getRedisConnection(self):
        """
        获取Redis Connection
        :return:
        """
        file_path = os.getcwd()+'\\conf\\redis_conf.cfg'
        redis_conf_info = RedisConf().read_cfg(file_path)

        if redis_conf_info is not None:
            redisConn = redis.Redis(host=redis_conf_info[0], port=redis_conf_info[1],
                                    db=self.db, password=redis_conf_info[2])
            # redisConn = redis.Redis(host=redis_conf_info[0], port=redis_conf_info[1], db=self.db)
            return redisConn
        else:
            return None


    def get_key_value(self, type, key, field):
        """
        获取缓存的值
        :param type:
        :param key:
        :param field:
        :return:
        """
        redis_conn = self._getRedisConnection()
        if redis_conn is None:
            raise ConnectionError

        if type == 'string':
            value = redis_conn.get(key)
            return value
        elif type == 'hash':
            hash_field_list = [item.decode('utf-8') for item in redis_conn.hkeys(key)]
            return hash_field_list
        elif type == 'set':
            set_fields = redis_conn.smembers(key)
            set_fields_list = []
            for item in set_fields:
                set_fields_list.append(item.decode('utf-8'))
            return set_fields_list
        elif type == 'list':
            return '没有API支持直接从list集合获取所有记录，或按索引获取记录'
        elif type == 'hash_field':
            try:
                hash_field_value = redis_conn.hget(key, field).decode('utf-8')
            except Exception:
                hash_field_value = redis_conn.hget(key, field)
            return hash_field_value
        elif type == 'set_field':
            return '没有API支持从set集合中按指定的field获取value.'

    def get_key_info(self, key):
        redis_conn = self._getRedisConnection()
        if redis_conn is None:
            raise ConnectionError

        if key is not None and len(key)>0:
            key_expire_time = datetime.datetime.fromtimestamp(int(time.time())+redis_conn.ttl(key))\
                             .strftime('%Y-%m-%d %H:%M:%S') if redis_conn.ttl(key) is not None else ''
            key_type = redis_conn.type(key).decode('utf-8')
            return (key_type, key_expire_time)
        else:
            return None


    def get_all_keys(self):
        """
        获取当前数据库中所有的key
        :return:list
        """
        redis_conn = self._getRedisConnection()
        if redis_conn is None:
            raise ConnectionError

        allKeys = redis_conn.keys('*')
        key_detail_info_list = []
        format = '%Y-%m-%d %H:%M:%S'
        for key in allKeys:
            key_expire_time = datetime.datetime.fromtimestamp(int(time.time())+redis_conn.ttl(key))\
                             .strftime(format) if redis_conn.ttl(key) is not None else ''
            key_type = redis_conn.type(key).decode('utf-8')
            key_detail_info_list.append(key.decode('utf-8')+'   '+key_type+'   超时时间:'+key_expire_time)
        return key_detail_info_list


    def del_key(self, key):
        """
        删除缓存
        :param key:
        :return:
        """
        redis_conn = self._getRedisConnection()
        if redis_conn is None:
            raise ConnectionError

        redis_conn.delete(key)