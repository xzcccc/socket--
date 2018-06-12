###该程序为客户端程序
import socket
import json
import threading
import pdb
import time

##建立socket连接
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("127.0.0.1",9999))
true=True
lock=threading.Lock()
##创建注册和登录的标志位
re_flag=0
login_flag=0
##创建聊天标志位，如果聊天对象存在则为1
talk_flag=0

##定义类处理客户端的请求，最终返回字典格式数据
class client_handle:

    def __init__(self, user_name=[],fri_name=[], passwd=[], choice_type=[]):

        self.name = user_name
        self.friname = fri_name
        self.passwd = passwd
        self.data = []
        self.choice = choice_type
##注册请求
    def register(self):

        self.choice = 'register'
        print("welcome to register")
        print("input username:")
        self.name = input()

        print("input password:")
        self.passwd = input()
##登录请求
    def login(self):

        self.choice = 'login'
        print("login")
        print("input username:")
        self.name = input()
        print("input password:")
        self.passwd = input()
##发起聊天请求
    def talk(self):
        self.choice = 'talk'
        print("please input the friend name who you want to talk:")
        self.friname = input()
        #print("please input the content you want to send:")
        #self.data = input()
##发送聊天数据请求
    def talk_data(self, data):
        self.choice = 'talk_data'
        #print("please input the content you want to send:")
        self.data = data
##退出聊天请求
    def talk_quit(self):
        self.choice = 'talk_quit'
##查找好友请求
    def find_fri(self):

        self.choice = 'find_fri'
##添加好友请求,目前做的是添加是无需对方同意,后续有待完善
    def add(self):

        self.choice = 'add'
        print("please input the friend name who you want to add:")
        self.friname = input()
##删除好友请求
    def delete(self,name):

        self.choice = 'delete' 
        self.friname = name 
##登出请求
    def login_out(self):
        
        self.choice = 'login_out'   
##将上面的请求的数据存到字典中并返回
    def as_dict(self):
        return({'name':self.name, 'passwd':self.passwd, 'choice':self.choice, 'fri_name':self.friname, 'data':self.data})

#def lock_flag(flag,n):    

##客户端接收线程函数，接收服务器端发送过来的对请求的响应
def rec(s):
    global true
    global re_flag
    global login_flag
    global talk_flag
    try:
        while true:
            t=s.recv(1024).decode("utf8")  #客户端也同理
            json_str=json.loads(t)
            ##服务器对注册的响应
            if json_str['type'] == "register":
                if json_str['data_1'] == "re_True":
                    #lock.acquire()
                    re_flag = 1
                    #lock.release()
                    print("register successfully")
                elif json_str['data_1'] == "re_False":
                    re_flag = 0
                    print("register failed: user name is exist alreadly")
            
            ##服务器对登录的响应
            if json_str['type'] == "login":
                if json_str['data_1'] == "login_True":
                    login_flag = 1
                    print("login successfully")
                elif json_str['data_1'] == "login_False":
                    login_flag = 0
                    print("login failed: user name or passwd is wrong")
            
            ##服务器对查找好友的响应
            if json_str['type'] == "find_fri":
                name = json_str['data_1']
                flag = json_str['data_2']
                print("frind_name        online/outline")
                for i in range(len(name)):
                    print("   %s          %s" % (name[i], flag[i]))

            ##服务器对删除好友的响应
            if json_str['type'] == "delete":
                if json_str['data_1'] == "de_True":
                    print("delete friend successfully")
                elif json_str['data_1'] == "de_False":
                    print("the friend name is not exist")

            ##服务器对添加好友的响应
            if json_str['type'] == "add":
                if json_str['data_1'] == "add_True":
                    print("add friend successfully!")
                elif json_str['data_1'] == "add_False":
                    print("the name you input is not a user!")
                elif json_str['data_1'] == "exist":
                    print("the name you input is already you friend!")

            ##服务器对聊天的响应
            if json_str['type']  == "talk":
                if json_str['data_1'] == "talk_True":
                    talk_flag = 1
                elif json_str['data_1'] == "not_online":
                    print("the friend you choose is not online")
                elif json_str['data_1'] == "talk_False":
                    print("the name you input is not your friend")


            ##服务器响应别的客户端发送给本客户端的聊天内容
            if json_str['type']  == "talk_data":
                #print(json_str['type'])
                print("your firend '%s' say:'%s'" % (json_str['data_2'],json_str['data_1']))

            elif t == "exit":
                true=False
            #print(t)
    except:
        pass

###处理客户端发送给服务器的指令
def client_callback(s,handle):
    dic = handle.as_dict()
    json_str = json.dumps(dic)
    s.send(json_str.encode('utf8'))

def menu_main():
    print("************************************")
    print("please choose which thing you wanna do(input 1 or 2):")
    print("1.register    2.login")
    print("************************************")

def menu_login():
    print("************************************")
    print("Now you have registered successfully, please login in:")

def menu_fri():
    print("************************************")
    print("Now you have login successfully,please choose the follow step:")
    print("1.list the friend table")
    print("2.choose one friend to talk")
    print("3.add friend")
    print("4.delete friend")
    print("5.login out")

trd=threading.Thread(target=rec,args=(s,))
trd.start()
a=client_handle()

while true:
    menu_main()
    chose=input()
    if chose == '1':
        a.register()
        client_callback(s,a)
        time.sleep(2)  ##等待2s为了让接收线程响应,后面同理
        #pdb.set_trace()
        #if re_flag == 1:
        #    menu_login()
        #    a.login()
        #    client_callback(s,a)
        #    time.sleep(2)
        #    if login_flag == 1:
        #        menu_fri()
        #        chose_x=input()
    elif chose == '2':
        a.login()
        client_callback(s,a)
        time.sleep(2)
        if login_flag == 1:
            while True:
                menu_fri()
                chose_x=input()
                if chose_x == '1':
                    a.find_fri()
                    client_callback(s,a)
                    time.sleep(3)
                    continue
                if chose_x == '2':
                    a.talk()
                    client_callback(s,a)
                    time.sleep(2)
                    while talk_flag == 1:
                        print("please input the content you want to send(q for quit):")
                        x = input()
                        if x == 'q':
                            talk_flag = 0
                        else:
                            a.talk_data(x)
                            client_callback(s,a)
                            time.sleep(2)
                    a.talk_quit()
                    client_callback(s,a)
                    time.sleep(2)
                    continue
                if chose_x == '3':
                    a.add()
                    client_callback(s,a)
                    time.sleep(2)
                    continue
                if chose_x == '4':
                    print("please input the content you want to delete:")
                    x = input()
                    a.delete(x)
                    client_callback(s,a)
                    time.sleep(2)
                    continue
                if chose_x == '5':
                    login_flag=0
                    a.login_out()
                    client_callback(s,a)
                    time.sleep(2)
                    break;
                else:
                    print("input error")
                    continue
    else:      
        print("input error")
        re_flag = 0
        login_flag = 0
        s.send(bytes('exit','UTF-8'))
        trd.join()
        true = False
    #if t == "exit":
        #true=False
s.close() 
