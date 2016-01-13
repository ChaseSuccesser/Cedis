#coding=utf-8
__author__ = 'lgx'

import redis
import time
import datetime
from conf.redis_conf import RedisConf

class RedisUtil(object):

    def __init__(self, db):
        self.db = db

    def testConnection(self, host, port, password):
        """
        attemp connection to Redis
        :return:Bool
        """
        try:
            redis_conn = redis.Redis(host=host, port=port, password=password)
            if redis_conn is None:
                return False
            return True
        except Exception:
            return False

    def _getRedisConnection(self):
        """
        get connection of Redis
        :return:
        """
        redis_conf_info = RedisConf().read_cfg()
        # redisConn = redis.Redis(host=redis_conf_info[0], port=redis_conf_info[1], db=self.db, password=redis_conf_info[2])
        redisConn = redis.Redis(host=redis_conf_info[0], port=redis_conf_info[1], db=self.db)
        return redisConn

    def getKeyValue(self, type, key, field):
        """
        获取缓存的值
        :param type:
        :param key:
        :param field:
        :return:
        """
        redisConn = self._getRedisConnection()

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
        redisConn = self._getRedisConnection()

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
        redisConn = self._getRedisConnection()
        redisConn.delete(key)