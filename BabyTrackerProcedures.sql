-- Run this file after inital setup steps
-- $mysql -u babyflask -p < ./BabyTrackerProcedures.sql
-- WARNING: If this is run after the appliction is started, the database will be reset

USE babytracker;
DROP PROCEDURE IF EXISTS sp_validateLogin;
DROP PROCEDURE IF EXISTS sp_createUser;
DROP PROCEDURE IF EXISTS sp_addDiaper;
DROP PROCEDURE IF EXISTS sp_addBottle;
DROP PROCEDURE IF EXISTS sp_addNote;
DROP PROCEDURE IF EXISTS sp_getEventsByUser;
DROP PROCEDURE IF EXISTS sp_deleteEvent;
DROP TABLE IF EXISTS tbl_user;
DROP TABLE IF EXISTS tbl_event;

CREATE TABLE `babytracker`.`tbl_user` (
	`user_id` BIGINT NOT NULL AUTO_INCREMENT,
	`user_name` VARCHAR(45) DEFAULT NULL,
	`user_username` VARCHAR(45) DEFAULT NULL,
	`user_password` VARCHAR(255) DEFAULT NULL,
	PRIMARY KEY (`user_id`));

CREATE TABLE `babytracker`.`tbl_event` (
	`event_id` BIGINT NOT NULL AUTO_INCREMENT,
	`event_user_id` BIGINT DEFAULT NULL,
	`event_time` DATETIME DEFAULT NULL,
	`event_type` VARCHAR(16) DEFAULT NULL,
	`diaper_dirty` BOOLEAN DEFAULT 0,
	`diaper_wet` BOOLEAN DEFAULT 0,
	`bottle_oz` INT UNSIGNED DEFAULT 0,
	`event_comment` VARCHAR(255) DEFAULT NULL,
	PRIMARY KEY (`event_id`));

DELIMITER $$
CREATE DEFINER=`babyflask`@`localhost` PROCEDURE `sp_validateLogin`(
IN p_username VARCHAR(45)
)
BEGIN
	select * from tbl_user where user_username = p_username;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`babyflask`@`localhost` PROCEDURE `sp_addDiaper`(
	IN p_dirty BOOLEAN,
	IN p_wet BOOLEAN,
	IN p_time DATETIME,
	IN p_user_id BIGINT,
	IN p_comment VARCHAR(255)
)
BEGIN
	insert into tbl_event(
		event_user_id,
		event_time,
		event_type,
		diaper_dirty,
		diaper_wet,
		event_comment
	)
	values
	(
		p_user_id,
		p_time,
		'diaper',
		p_dirty,
		p_wet,
		p_comment
	);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`babyflask`@`localhost` PROCEDURE `sp_addBottle`(
	IN p_oz INT UNSIGNED,
	IN p_time DATETIME,
	IN p_user_id BIGINT,
	IN p_comment VARCHAR(255)
)
BEGIN
	insert into tbl_event(
		event_user_id,
		event_time,
		event_type,
		bottle_oz,
		event_comment
	)
	values
	(
		p_user_id,
		p_time,
		'bottle',
		p_oz,
		p_comment
	);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`babyflask`@`localhost` PROCEDURE `sp_addNote`(
	IN p_time DATETIME,
	IN p_user_id BIGINT,
	IN p_comment VARCHAR(255)
)
BEGIN
	insert into tbl_event(
		event_user_id,
		event_time,
		event_type,
		event_comment
	)
	values
	(
		p_user_id,
		p_time,
		'note',
		p_comment
	);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`babyflask`@`localhost` PROCEDURE `sp_getEventsByUser`(
	IN p_user_id BIGINT
)
BEGIN
	select * from tbl_event where event_user_id = p_user_id order by event_time DESC;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`babyflask`@`localhost` PROCEDURE `sp_deleteEvent`(
	IN p_event_id BIGINT,
	IN p_user_id BIGINT
)
BEGIN
	delete from tbl_event where (event_user_id = p_user_id and event_id = p_event_id);
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`babyflask`@`localhost` PROCEDURE `sp_createUser`(
	IN p_name VARCHAR(45),
	IN p_username VARCHAR(45),
	IN p_password VARCHAR(255)
)
BEGIN
	if ( select exists (select 1 from tbl_user where user_username = p_username) ) THEN
		select 'Username Exists !!';
	ELSE
		insert into tbl_user
		(
			user_name,
			user_username,
			user_password
		)
		values
		(
			p_name,
			p_username,
			p_password
		);
	END IF;
END$$
DELIMITER ;
