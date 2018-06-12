#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pymysql as mdb
import pdb
"""
con=None
try:
    con = mdb.connect('localhost','root','123456','mysql')
    cur = con.cursor()
    cur.execute("SELECT VERSION()")
    data = cur.fetchone()
    print("Database version:%s", data)
finally:
    if con:
        con.close();
"""

class mydb:

    def __init__(self, host, user, pw, db):
    #def __init__(self, **kwargs)
        """初始化"""
        self.host=host
        self.user=user
        self.pw=pw
        self.db=db
        # 打开数据库连接返回值
        self.con=None
        #self.con=mdb.connect(host=kwargs["host"], user=kwargs["user"], passwd=kwargs["password"], db=kwargs["db"])
        
        # 存放操作游标
        #self.cur=self.con.cursor()
        self.cur=None
        # 数据查询结果标志位
        self.flag=None
        # 存放查询的user和passwd
        self.username=[]
        self.passwd=[]
    
    """连接数据库"""    
    def connect(self):
        
        self.con=mdb.connect(self.host,self.user,self.pw,self.db)
        self.cur=self.con.cursor()
        print("connect")
        #self.cur.execute("SELECT VERSION()")
        #data = self.cur.fetchone()
        #print("Database version:%s", data)


    """用户登录时根据收到的用户名筛选数据库"""
    def select(self, find_user, find_pass):
        try: 
            self.cur.execute('select * from user where user_name="%s"' % find_user)
            results = self.cur.fetchall()
            for row in results:
                self.username=row[1]
                self.passwd=row[2]
                #print("username=%s,passwd=%s" % (self.username,self.passwd))
            #print("hello")
            # 判断数据是否存在数据库,如果存在,再判断密码是否一致
            if results:
                self.flag=1
                if find_pass == self.passwd:
                    return True
                else:
                    return False
                #print("have data")
            else:
                return False
                #self.flag=0
                #print("no data")
        except:
            #self.flag=1
            print("Error:unable to fetch data")
            #pass


    """插入新注册的用户名和密码"""
    def insert(self, ins_user, ins_pass):

        try:
            self.cur.execute('select * from user where user_name="%s"' % ins_user)
            results = self.cur.fetchall()
            #如果用户名已存在，返回False
            if results:
                return False
            else:
                self.cur.execute('insert into user(user_name,password,online) values("%s","%s",0)' % (ins_user,ins_pass))
                #self.cur.execute(m)
                self.con.commit()
                #print("insert")
                return True
        except:
            self.con.rollback()

    """关闭数据库"""
    def close(self):

        self.con.close()

    
    """当用户登录成功(或者下线)时更新数据库中在线状态,通过flag来控制,flag=1表示用户上线,0表示下线"""
    def update(self, up_user, flag):
        
        try:
            if flag:
                self.cur.execute('update user set online=1 where user_name="%s"' % up_user)
                self.con.commit()
            else:
                self.cur.execute('update user set online=0 where user_name="%s"' % up_user)
                self.con.commit()
        except:
            self.con.rollback()
        
    """当用户注册成功后建立一张用户好友表"""
    def create(self, cre_user):
    
        try:
            #pdb.set_trace()
            self.cur.execute('create table %s(id int(10) NOT NULL AUTO_INCREMENT, user_name varchar(100) NOT NULL, online int(10), PRIMARY KEY(id))' % cre_user)
            #self.cur.execute(sql)
            self.con.commit()
            print("create successfully")
            """
            self.cur.execute('create trigger updateonline after update on user for each row begin\
                                if new.online=1 then\
                                  update "%s" set online=1 where "%s".user_name=old.user_name;\
                                    else\
                                      update "%s" set online=NULL where "%s".user_name=old.user_name;\
                                        end if; end$' % cre_user)
            self.cur.execute('DELIMITER ,')
            self.con.commit()
            """
        except: 
            print("ERROR:create friend table fail")


    """添加好友后插入好友表,先判断user表该用户是否存在;然后再判断好友表中该用户是否存在;如果返回0，则user表中不存在;如果返回1，则好友表中已存在;返回2，则表示好友添加成功"""
    def inse_fri(self, user, inse_user):
    
        try:
            #pdb.set_trace()
            self.cur.execute('select * from user where user_name="%s"' % inse_user)
            result1 = self.cur.fetchall()
            if result1:
                self.cur.execute('select * from %s where user_name="%s"' % (user, inse_user))
                results = self.cur.fetchall()
                if results:
                    return 1
                else:
                    self.cur.execute('insert into %s (user_name) values("%s")' % (user, inse_user))
                    self.con.commit()
                    return 2
            else:
                return 0
        except:
            self.con.rollback()
    
    """当用户登录后查找在线好友,首先筛选好友表，然后根据好友表中的用户名到user表中查找online列,如果为1则好友在线,反之不在线; find_user传入当前用户名; 返回在线的好友名;还用来在添加或删除好友后更新在线好友列表"""
    def find_fri(self, find_user):

        try:
            #pdb.set_trace()
            name = []
            flag = []
            #筛选好友表
            self.cur.execute('select * from %s' % find_user)
            results = self.cur.fetchall()
            #针对好友表中每一个用户名对user表进行查找，返回好友名以及好友在线状态
            for row in results:
                self.cur.execute('select * from user where user_name="%s"' % row[1])
                online_flag = self.cur.fetchone()
                #if online_flag[4] == 1:    ###未完善，需要考虑返回值!!!
                name.append(row[1])
                flag.append(online_flag[4])   ###可以考虑当flag=1，列表中插入online
            return name, flag
        except:
            pass
    
    """删除好友,user传入当前用户;del_user传入要删除的好友名;首先判断好友是否存在;好友不存在，返回False;好友存在返回True"""
    def del_fri(self, user, del_user):

        try:
            self.cur.execute('select * from %s where user_name="%s"' % (user, del_user))
            results = self.cur.fetchall()
            if results:
                self.cur.execute('delete from %s where user_name="%s"' % (user, del_user))
                self.con.commit()
                return True
            else:
                return False
        except:
            self.con.rollback()
    
    """聊天时判断好友是否存在以及是否在线,如果好友不存在返回false"""
    def check_online(self, user, fri_user):
        try:
            self.cur.execute('select * from %s where user_name="%s"' % (user, fri_user))
            results = self.cur.fetchone()
            if results:
                self.cur.execute('select * from user where user_name="%s"' % fri_user)
                result = self.cur.fetchone()
                #print(result)
                online_flag = result[4]
                #print(online_flag)
                if online_flag == 0:
                    return "outline"
                elif online_flag == 1:
                    return "online"
            else:
                return False
        except:
            pass

           
    """列出好友表,在好友表更新后刷新; list_user传入当前用户名"""
    #def list(self, list_user):
    #   self.cur.execute('select *from %s' % list_user)
