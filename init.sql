-- 初始化表结构SQL
create dataebase audit;

use audit;

CREATE TABLE `audit_mariadb` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date_time` datetime(6) NOT NULL COMMENT 'SQL执行时间',
  `host_name` varchar(32) NOT NULL COMMENT '用户主机名',
  `user_name` varchar(32) NOT NULL COMMENT '用户名',
  `user_ip` varchar(32) NOT NULL COMMENT '用户IP',
  `thread_id` int(11) NOT NULL COMMENT '线程id',
  `query_id` int(11) NOT NULL COMMENT '查询id',
  `db_name` varchar(32) NOT NULL COMMENT '数据库名',
  `sql_content` text NOT NULL COMMENT 'SQL语句',
  `exe_status` int(11) NOT NULL COMMENT '执行状态，0正常，其他为报错',
  PRIMARY KEY (`id`),
  KEY `idx_date_time` (`date_time`)
) ENGINE=InnoDB AUTO_INCREMENT=4166 DEFAULT CHARSET=utf8mb4;
