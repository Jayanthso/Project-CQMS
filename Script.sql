CREATE DATABASE IF NOT EXISTS cqms;

create table cqms.query_detail(
query_id int AUTO_INCREMENT Primary Key,
client_email varchar(100), 
client_mobile varchar(15), 
query_heading varchar(50), 
query_description varchar(4000), 
status varchar(20), 
date_raised date, 
date_closed date, 
user_id varchar(200), 
user_resolved varchar(20)
);

create table cqms.user_detail(
user_id int auto_increment Primary key, 
user_fullname varchar(100),
user_name varchar(20), 
user_mobile varchar(15), 
user_email varchar(40), 
user_password varchar(255), 
user_role enum('Client','Support','Admin')
);


ALTER TABLE cqms.user_detail
ADD UNIQUE (user_name),
ADD UNIQUE (user_email);