# audit-script-mariadb
A script to analyse audit log generated by mariadb server_aduit plugin and write to mysql-db.
You need to install the plugin and set the logging on.
server_aduit plugin adition: MariaDB Audit Plugin version 1.4.4

MariaDB Audit Plugin插件兼容MySQL5.7
1、下载mariadb-5.5.65-linux-x86_64.tar.gz解压获取server_audit.so插件

2、登录MySQL，执行命令获取MySQL的plugin目录
mysql> SHOW GLOBAL VARIABLES LIKE 'plugin_dir';
+---------------+--------------------------+
| Variable_name | Value |
+---------------+--------------------------+
| plugin_dir | /usr/lib64/mysql/plugin/ |
+---------------+--------------------------+
1 row in set (0.02 sec)

3、将server_audit.so上传到 /usr/lib64/mysql/plugin/下
```sh
chown -R mysql:mysql server_audit.so
```
4、在命令下安装server_audit.so
mysql> INSTALL PLUGIN server_audit SONAME 'server_audit.so';

error中出现如下信息

190822 6:49:28 server_audit: MariaDB Audit Plugin version 1.4.4 STARTED.
5、查看变量开启设置情况，默认都是关闭的
mysql> show variables like 'server_audit%';

6、在线更改配置
set global server_audit_file_path = "/var/lib/mysql";
将在该目录下生成server_audit.log文件

开启日志审计功能

set global server_audit_events='QUERY_DML_NO_SELECT,QUERY_DDL,QUERY_DCL';

记录不包括select的DML语句，所有DDL语句和所有DCL语句；
set global server_audit_file_rotations =2 ;
set global server_audit_file_rotate_size =100000000; 100M
此时将开启审计功能
```mysql
set global server_audit_logging = 1;
```
6、编辑my.cnf,添加配置（如果通过在mysql中改变全局变量的方式，重启mysql后会丢失）
持久化上述配置更改
server_audit_events='QUERY_DML_NO_SELECT,QUERY_DDL,QUERY_DCL'



备注：指定哪些操作被记录到日志文件中:QUERY_DML_NO_SELECT记录除了select之外的DML，QUERY_DDL所有DDL，QUERY_DCL：所有DCL
server_audit_logging=on
server_audit_file_path =/var/lib/mysql（在个路径Mysql不会自动创建，要自己创建并且用户和组都设置为mysql）
备注：审计日志存放路径，该路径下会生成一个server_audit.log文件，就会记录相关操作记录了
日志轮换相关参数
server_audit_file_rotate_size=100000000
server_audit_file_rotations=2



7、查看日志文件记录内容日志解析,按照逗号分隔
20190807 04:14:02,et-dba-tianzhaofeng,tianzhaofeng,192.168.4.121,12,122,QUERY,tian,'SHOW TABLE STATUS',0
日期 时间 主机名 用户名 用户IP 线程id 查询id 命令类型 SQL语句 命令状态


