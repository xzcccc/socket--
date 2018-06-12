import socket
import json
import threading
import mysql
import time
##创建接收线程所需要的参数
sock = socket.socket()
sock1 = socket.socket()
addr = ()
addr1 = ()
json_str = {}
json_str1 = {}

##创建字典用来存储连接上的客户端的sock和姓名(姓名作为唯一标识)
sock_addr = {}

##用来存储客户端想找谁聊天
who_talk = []
who_talk1 = []

##用来存储客户端的聊天内容
json_data = {}

###聊天时的标志位
talk_flag = 0
quit_flag = 0

##连接数据库
a=mysql.mydb('localhost','root','123456','python')
a.connect()

##建立socket连接
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("127.0.0.1",9999))
s.listen(2)
true=True

###服务器返回客户端的json规范
def as_dic(t_type,data_1,data_2=[]):
    as_type=t_type
    as_data_1=data_1
    as_data_2=data_2
    dic={'type':as_type, 'data_1':as_data_1, 'data_2':as_data_2}
    json_dic=json.dumps(dic)
    return json_dic
    
##服务器接收线程，用来处理客户端发过来的各种请求
def rec(s,sock,addr,json_str):
    global true
    global sock_addr
    global who_talk
    global json_data
    global talk_flag
    global quit_flag
    sock,addr=s.accept()
    while true:
        t=sock.recv(1024).decode('utf8')  #函数的核心语句就一条接收方法
        #print(t)
        json_str=json.loads(t)
        sock_addr[json_str['name']] = sock
        print(sock_addr[json_str['name']])
        ##注册请求
        if json_str['choice'] == 'register':
            result=a.insert(json_str['name'],json_str['passwd'])
            a.create(json_str['name'])
            if result:
                json_re=as_dic('register','re_True')
                sock.send(json_re.encode('utf8'))
            else:
                json_re=as_dic('register','re_False')
                sock.send(json_re.encode('utf8'))
        
        ##登录请求
        if json_str['choice'] == 'login':
            result=a.select(json_str['name'],json_str['passwd'])
            a.update(json_str['name'],1)
            if result:
                json_lo=as_dic('login','login_True')
                sock.send(json_lo.encode('utf8'))
            else:
                json_lo=as_dic('login','login_False')
                sock.send(json_lo.encode('utf8'))

        ##查找好友请求
        if json_str['choice'] == 'find_fri':
            name,flag=a.find_fri(json_str['name'])
            json_fi=as_dic('find_fri',name,flag)
            sock.send(json_fi.encode('utf8'))

        ##删除好友请求
        if json_str['choice'] == 'delete':
            result = a.del_fri(json_str['name'],json_str['fri_name'])
            if result:
                json_de=as_dic('delete','de_True')
                sock.send(json_de.encode('utf8'))
            else:
                json_de=as_dic('delete','de_False')
                sock.send(json_de.encode('utf8'))

        ##添加好友请求
        if json_str['choice']  == 'add':
            result = a.inse_fri(json_str['name'],json_str['fri_name'])
            if result == 1:
                json_add=as_dic('add','exist')
                sock.send(json_add.encode('utf8'))
            if result == 2:
                json_add=as_dic('add','add_True')
                sock.send(json_add.encode('utf8'))
            if result == 0:
                json_add=as_dic('add','add_False')
                sock.send(json_add.encode('utf8'))

        ##登出请求
        if json_str['choice'] == 'login_out':
            a.update(json_str['name'],0)

        ##发起聊天请求
        if json_str['choice'] == 'talk':
            #talk_flag = 1
            #print(talk_flag)
            result = a.check_online(json_str['name'],json_str['fri_name'])
            if result == "online":
                print('x')
                who_talk = json_str['fri_name']
                json_talk=as_dic('talk','talk_True')
                sock.send(json_talk.encode('utf8'))
            elif result == "outline":
                print('xx')
                json_talk=as_dic('talk','not_online')
                sock.send(json_talk.encode('utf8'))
            else:
                print('xxx')
                json_talk=as_dic('talk','talk_False')
                sock.send(json_talk.encode('utf8'))

        ##发出聊天内容请求
        if json_str['choice'] == 'talk_data':
            #data = json_str['data']
            talk_flag = 1
            json_data = as_dic('talk_data',json_str['data'],json_str['name'])
            print(json_data)

        ##退出聊天请求
        if json_str['choice'] == 'talk_quit':
            talk_flag = 0
        #print('json_str["name"]')
        print(json_str)
        if t == 'exit':
            true=False
        ##json_str=json.loads(t)
        ##print(t)

##开启两个接收线程，后期可以将这个做成线程池
trd=threading.Thread(target=rec,args=(s,sock,addr,json_str))
trd1=threading.Thread(target=rec,args=(s,sock1,addr1,json_str1))
trd.start()
trd1.start()

##主线程中主要完成的是发送消息给指定的客户端
try:
    while true:
        #t=input()
        #sock.send(t.encode('utf8'))
        #if t == "exit":
        #    true=False
        #sock.send(t.encode('utf8'))
        time.sleep(3)
        if talk_flag == 1:
            #while True:
            #print("xxxxx")
            sock_send = sock_addr[who_talk]
            #print(sock_send)
            print(json_data)
            sock_send.send(json_data.encode('utf-8'))
            #break
            #print(talk_flag)
            #if quit_flag == 1:
            #    talk_flag = 0            ####可能要上锁
            #    break
        talk_flag = 0
        #quit_flag = 0
except:
    pass
finally:
    trd.join()
    trd1.join()
    a.close()
    s.close()
