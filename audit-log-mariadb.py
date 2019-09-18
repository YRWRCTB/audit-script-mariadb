#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

#执行如下脚本需要修改连接参数
import pymysql as mysqldb
import os
import time
import sys
import datetime

#指定审计日志文件的位置
file_name="/var/lib/mysql_bak/server_audit.log"
file_name_rotate="/var/lib/mysql_bak/server_audit.log.1"

#获取脚本所在目录，在脚本所在目录位置生成两个文件，用于存储读取位置
#和日志文件修改时间相管信息
path=sys.path[0]
#print("path",path)

def check_run():
	#检测pid文件是否存在，存在函数返回为1
	if os.path.exists(path+"/audit.pid"):
		print("pid file exits.")
		return 1
	#如果不存在在创建pid文件，并写入值,函数返回值为0
	else:
		create_pid = open(path+"/audit.pid","w")
		create_pid.write(str(1))
		create_pid.close()
		print("pid file created.")
		return 0

#程序结束后删除pid文件
def del_pid():
	if os.path.exists(path+"/audit.pid"):
		os.remove(path+"/audit.pid")
		print("pid file removed.")
	##
	else:
		print("no pid file.")

#首次执行程序会自动创建两个用于记录文件最后修改时间和读取文件位置的文件，
#再次执行，如果文件存在，将不做任何操作
def check_files():
	if os.path.exists(path+"/location.txt"):
		print("location file exists")
	else:
		create_loc = open(path+"/location.txt","w")
		create_loc.write(str(0))
		create_loc.close()

	if os.path.exists(path+"/check_time.txt"):
		print("check time file exists")
	else:
		create_time = open(path+"/check_time.txt","w")
		create_time.write(str(0))
		create_time.close()

#远程数据库连接,日志存放数据库相关信息，
#需要提前创建好用户和表
db = mysqldb.connect(host="192.168.20.156",\
user="root",password="easytech",\
database="tian",charset="utf8")


#增量读取日志文件，并将其存储在远程数据库中
def read_file(file_name):
	#首先读取location文件信息，即上次读取日志文件的最终位置
	location_f = open(path+"/location.txt","r",encoding="utf-8")
	location = location_f.readline()
	location_f.close()
	print ("old-loaction",location)
	location = int(location)

	cursor = db.cursor() #进行数据库连接i
	#打开文件读取信息
	with open(file_name,"r") as fd:
		fd.seek(location) #将读取文件位置重新定位，初始值在文件中置为0，之后每次将最终位置写入文件进行存储
		for line in fd:
#			print (type(line)) #读取出每行，line的类型为string
			#print (line)
			sql = "insert into audit(log) values(%s);"  #使用占位符的方式进行SQL语句拼接,这种方式可以将
														#line中的特殊符号进行转译，避免拼接时发生语法错误
			res = line.split(",")
			date_time = res[0]
			timeArray = time.strptime(date_time, "%Y%m%d %H:%M:%S")
			
			date_time = (time.mktime(timeArray))
#			print (date_time)
			date_time=datetime.datetime.fromtimestamp(date_time)
			date_time=date_time.strftime("%Y-%m-%d %H:%M:%S.%f")

			host_name = res[1]
			user_name = res[2]
			user_ip   = res[3]
			thread_id = res[4]
			query_id  = res[5]
			db_name   = res[7]
			#SQL语句中出现逗号，则无法获取完整的sql
			sql_conten= res[8]
			exe_status= res[-1]
			sql_row = "insert into audit_mariadb(date_time,host_name,\
			user_name,user_ip,thread_id,query_id,db_name,sql_content,exe_status) \
			values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

			#执行SQL将信息写入数据库
			#使用逗号
			cursor.execute(sql,line)
			cursor.execute(sql_row,(date_time,host_name,user_name,user_ip,thread_id,\
			query_id,db_name,sql_conten,exe_status))
			cursor.execute("commit")
		location = fd.tell()                            #记录最后一次读取文件的位置
	#关闭游标
	cursor.close()
		#将记录写入文件
		#在下次读取时获得增量，location变量为数值类型
#		print (location)
	print ("new-location",location) #可以打印
	#将location的值存储在文本文件中以便下次使用；
	location_f = open(path+"/location.txt","w",encoding="utf-8")
	location_f.write(str(location))   #无法再文本文件中存储数值类型，需将器转换成字符串类型
	location_f.close()


#考虑日志轮换的问题
#mysql-audit.json一直在更新.文件每天进行一次轮换
#日志进行轮换，mysql-audit.json重命名为mysql-audit.json.1
#新建一个mysql-audit.json，开始写入新的日志；
#检测mysql-audit.json.1的修改时间
#根据其变化进行不同操作，以便获取正确的日志内容

def check_time():
#	global json_time_now
	#检测"/var/lib/mysql/mysql-audit.json.1"最后修改时间
	json_time_now=os.path.getmtime(file_name_rotate)
	#将值转换为int
	json_time_now=int(json_time_now)

	print("now",json_time_now)
	
#	global json_time_rec
	#读取check_time.txt文件中的内容，文件中初始值为0
	time_rec = open(path+"/check_time.txt","r",encoding="utf-8")
	json_time_rec = time_rec.readline()
	#将字符串转换为int
	json_time_rec=int(json_time_rec)

	print("rec",json_time_rec)

	#将本次解析文件时间存储在check_time.txt中，默认格式为小数点后四位；
	#将其转换为int，并按照字符串存储在文件中,用于下次比较
	time_f = open(path+"/check_time.txt","w",encoding="utf-8")
	time_f.write(str(json_time_now))
	time_f.close()
	if json_time_rec == 0:
		return -1
	elif json_time_rec == json_time_now:
		return 1
	else:
		return 0
	#如果两个时间相同函数返回值为1
	#如果时间不同返回值为0
	#如果rec_time 为0 ，则返回值为-1
	#这样可以可以不用声明全局变量，充分使用返回值
	

#如下为主逻辑函数
#根据记录时间的不同，分别执行不同函数
#第一次执行前check_time.txt将中内容置为0，将会直接执行如下函数
def main():
	print("start analysing audit log ....")
	#在脚本运行时创建一个pid文件，如果再次运行该程序时，发现该文件存在
	print (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
	#则不会执行读取文件命令
	run = check_run()
	if run == 1:
		print("Programe is running... exit..")
	#首先检查两个文件是否存在，如果存在将不做任何操作，

	#如果不存在则创建两个文件，并写入初始值
	else:
		check_files()  
	
		#检查日志文件的更改时间，根据是否轮换，进行不同操作
		status =check_time()
	
		if status  == -1:
			read_file(file_name)
			print('irst time auditing')

		#之后执行时，将比较记录时间和当前时间
		#如果时间相同，表明没有进行日志的轮换
		#可以相关参数不改变，可以继续执行
		elif status == 1:
			read_file(file_name)
			print("文件未改变file_name",file_name)

		#如果发生日志切换
		else:
			#首先解析的文件名需要调整，但是文件的偏移量不需更改
			read_file(file_name_rotate)
			#执行完成后，因为此时/mysql/mysql-audit.json为一个新文件，需要从头解析
			#重写location值，置为0，再次执行
			location_f = open(path+"/location.txt","w",encoding="utf-8")
			location_f.write(str(0))
			location_f.close()
	
			read_file(file_name)
			print("log-rotate")
	#关闭连接
	db.close()
	#删除pid文件
	del_pid()
	#获取当前系统时间，并打印
	print('analyzing audit log ended .')
	print (time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

if __name__ == '__main__':
	main()

