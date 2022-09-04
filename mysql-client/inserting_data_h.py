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
        #mysql configuration
        mysql = 'LOCAL_DATABASE'
        mysql_host = cfg.get(mysql, 'host')
        mysql_user = cfg.get(mysql, 'user')
        mysql_password = cfg.get(mysql, 'password')
        mysql_database = cfg.get(mysql, 'database')
        dic.update({'mysql': {'host': mysql_host, 'user': mysql_user, 'password': mysql_password, 'database': mysql_database}})
        return dic

class MySql:
    def __init__(self, cfg_dic, cfg_name):
        self.cfg_dic = cfg_dic
        config = cfg_dic[cfg_name]
        self.host = config['host']
        self.user = config['user']
        self.password = config['password']
        self.database = config['database']
        self.conn, self.cur = self.connect()

    def connect(self):
        conn = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database, charset="utf8mb4", use_unicode=True)
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
    def create_insert_sql(table, insert_type, field_len, fields):
        sql = """{} INTO {} ({}) VALUES ({})""".format(insert_type, table, ','.join(fields), ','.join(field_len * ['%s']))
        return sql

if __name__ == '__main__':
    file_name = 'D:\dthcsm\\2022_sw_pro\\news-search-engine\mysql-client\data\cnn_2021_test.csv'
    df = pd.read_csv(file_name)
    fields = list(df.columns)

    cfg = ReadConfig()
    cfg_dic = cfg.get_config()
    mysql = MySql(cfg_dic, 'mysql')
    user_sql = mysql.create_insert_sql('es_table', 'REPLACE', len(fields), fields)

    df = df.reset_index()
    for index, row in df.iterrows():
        publish_date = datetime.strptime(row['publish_date'], '%Y-%m-%d')
        news = [row['id'], row['title'], row['newspaper'], row['authors'], publish_date, row['keywords'], row['summary'], row['text'], row['url']]
        mysql.execute(user_sql, news)
        print(index, "record inserted")