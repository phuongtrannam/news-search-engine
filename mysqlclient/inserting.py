#!/home/namphuong/Code/news-search-engine/myvenv/bin/python
import sys
import os
import configparser
import pymysql
import pandas as pd
from datetime import datetime


class ReadConfig:
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)

    def get_config(self):
        file_path = os.path.abspath(os.path.join(self.base_dir, 'config.cfg'))
        cfg = configparser.RawConfigParser()
        cfg.read(file_path)

        dic = {}
        # mysql configuration
        mysql = 'LOCAL_DATABASE'
        mysql_host = cfg.get(mysql, 'host')
        mysql_user = cfg.get(mysql, 'user')
        mysql_password = cfg.get(mysql, 'password')
        mysql_database = cfg.get(mysql, 'database')
        dic.update({'mysql': {'host': mysql_host, 'user': mysql_user,
                   'password': mysql_password, 'database': mysql_database}})
        return dic


class MySql:
    class MySqlCondition:
        GREATER = '>'
        EQUAL = '='
        SMALLER = '<'

        def __init__(self, field, condition):
            self.field = field
            self.condition = condition

        def __str__(self):
            return self.field + self.condition + '%s'

    def __init__(self, cfg_dic, cfg_name):
        self.cfg_dic = cfg_dic
        config = cfg_dic[cfg_name]
        self.host = config['host']
        self.user = config['user']
        self.password = config['password']
        self.database = config['database']
        self.conn, self.cur = self.connect()

    def connect(self):
        conn = pymysql.connect(host=self.host, user=self.user, password=self.password,
                               database=self.database, charset="utf8mb4", use_unicode=True)
        cur = conn.cursor()
        return conn, cur

    def execute(self, sql, params, many=0):
        if not many:
            self.cur.execute(sql, params)
            self.conn.commit()
        else:
            self.cur.executemany(sql, params)
            self.conn.commit()

    @staticmethod
    def create_insert_sql(table, insert_type, field_len, fields=None):
        if isinstance(fields, list):
            sql = """{} INTO {} ({}) VALUES ({})""".format(insert_type, table, ','.join(fields),
                                                           ','.join(field_len * ['%s']))
        else:
            sql = """{} INTO {} VALUES ({})""".format(
                insert_type, table, ','.join(field_len * ['%s']))
        print(sql)
        return sql

    @staticmethod
    def create_query_sql(table, fields, conditions, order_by=None):
        """select a,b from table where a>1 and b<10 order by a desc"""
        sql = """SELECT {} FROM {} WHERE {}""".format(
            ','.join(fields), table, ' AND '.join(condition.__str__() for condition in conditions))
        if order_by:
            sql = sql + f' ORDER BY {order_by}'
        return sql


if __name__ == '__main__':
    # # Read csv file
    # file_name = sys.argv[1]
    # df = pd.read_csv(file_name)
    # # Read mysql config file
    # cfg = ReadConfig()
    # cfg_dic = cfg.get_config()
    # # Create insert query
    # mysql = MySql(cfg_dic, 'mysql')
    # user_sql = mysql.create_insert_sql('es_table', 'REPLACE', 10)

    # df = df.reset_index()
    # for index, row in df.iterrows():
    #     publish_date = datetime.strptime(row['publish_date'], '%Y-%m-%d')
    #     modification_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #     news = [row['id'], row['title'], row['newspaper'], row['authors'],
    #             publish_date, row['keywords'], row['summary'], row['text'], row['url'], modification_time]
    #     mysql.execute(user_sql, news)
    #     print(index, "record inserted")

    cfg = ReadConfig()
    cfg_dic = cfg.get_config()
    mysql = MySql(cfg_dic, 'mysql')
    conditions = [mysql.MySqlCondition('newspaper', MySql.MySqlCondition.EQUAL), 
                    mysql.MySqlCondition('publish_date', MySql.MySqlCondition.GREATER)]
    user_sql = mysql.create_query_sql('es_table', ['url'], conditions)
    print(user_sql)
    params = ('NBC','2022-09-01')
    mysql.execute(user_sql, params)
    result = [item for t in list(mysql.cur.fetchall()) for item in t]
    print(type(result))
    # print(type(result[0]))
    print(len(result))