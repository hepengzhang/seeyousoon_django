BEGIN;
CREATE TABLE `webapi_user_info` (
    `last_login` datetime NOT NULL,
    `user_created_date` datetime NOT NULL,
    `email` varchar(254) NOT NULL UNIQUE,
    `phone` varchar(16) NOT NULL,
    `user_access` smallint UNSIGNED NOT NULL,
    `longitude` numeric(12, 8) NOT NULL,
    `latitude` numeric(12, 8) NOT NULL,
    `gender` smallint UNSIGNED NOT NULL,
    `fb_id` bigint UNSIGNED NOT NULL,
    `wb_id` bigint UNSIGNED NOT NULL,
    `primary_sns` smallint UNSIGNED NOT NULL,
    `name` varchar(90) NOT NULL,
    `user_id` bigint UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY
)
;
CREATE TABLE `webapi_user_auth` (
    `username` varchar(32) NOT NULL UNIQUE,
    `password` varchar(32) NOT NULL,
    `access_token` varchar(27) NOT NULL,
    `user_id` integer NOT NULL PRIMARY KEY
)
;
ALTER TABLE `webapi_user_auth` ADD CONSTRAINT `user_id_refs_user_id_ddaad938` FOREIGN KEY (`user_id`) REFERENCES `webapi_user_info` (`user_id`);
CREATE TABLE `webapi_user_search` (
    `username` varchar(32) NOT NULL,
    `user_id` integer NOT NULL PRIMARY KEY,
    `name` varchar(32) NOT NULL
)
;
ALTER TABLE `webapi_user_search` ADD CONSTRAINT `user_id_refs_user_id_2677c09c` FOREIGN KEY (`user_id`) REFERENCES `webapi_user_info` (`user_id`);
CREATE TABLE `webapi_push_notification` (
    `user_id` integer NOT NULL PRIMARY KEY,
    `device_id` varchar(32) NOT NULL,
    `push_token` varchar(64) NOT NULL,
    `config` smallint UNSIGNED NOT NULL,
    `friend_request` integer UNSIGNED NOT NULL,
    `activities` integer UNSIGNED NOT NULL
)
;
ALTER TABLE `webapi_push_notification` ADD CONSTRAINT `user_id_refs_user_id_aa5966f2` FOREIGN KEY (`user_id`) REFERENCES `webapi_user_info` (`user_id`);
CREATE TABLE `webapi_friends` (
    `status` smallint UNSIGNED NOT NULL,
    `user_id` integer NOT NULL,
    `friend_id` integer NOT NULL,
    `together_time` integer NOT NULL,
    `entry_id` bigint UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
    UNIQUE (`user_id`, `friend_id`)
)
;
ALTER TABLE `webapi_friends` ADD CONSTRAINT `user_id_refs_user_id_4a150324` FOREIGN KEY (`user_id`) REFERENCES `webapi_user_info` (`user_id`);
ALTER TABLE `webapi_friends` ADD CONSTRAINT `friend_id_refs_user_id_4a150324` FOREIGN KEY (`friend_id`) REFERENCES `webapi_user_info` (`user_id`);
CREATE TABLE `webapi_activities` (
    `activity_id` bigint UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `creator_id` integer NOT NULL,
    `access` smallint UNSIGNED NOT NULL,
    `type` smallint UNSIGNED NOT NULL,
    `status` smallint UNSIGNED NOT NULL,
    `activity_created_date` datetime NOT NULL,
    `description` varchar(255) NOT NULL,
    `longitude` numeric(12, 8) NOT NULL,
    `latitude` numeric(12, 8) NOT NULL,
    `destination` varchar(128) NOT NULL,
    `keyword` varchar(32) NOT NULL,
    `start_date` datetime NOT NULL,
    `end_date` datetime NOT NULL
)
;
ALTER TABLE `webapi_activities` ADD CONSTRAINT `creator_id_refs_user_id_325005a7` FOREIGN KEY (`creator_id`) REFERENCES `webapi_user_info` (`user_id`);
CREATE TABLE `webapi_participants` (
    `activity_id` integer NOT NULL,
    `participant_id` integer NOT NULL,
    `status` smallint UNSIGNED NOT NULL,
    `distance` integer UNSIGNED NOT NULL,
    `longitude` numeric(12, 8) NOT NULL,
    `latitude` numeric(12, 8) NOT NULL,
    `entry_id` bigint UNSIGNED AUTO_INCREMENT NOT NULL PRIMARY KEY,
    UNIQUE (`activity_id`, `participant_id`)
)
;
ALTER TABLE `webapi_participants` ADD CONSTRAINT `activity_id_refs_activity_id_8ad06c30` FOREIGN KEY (`activity_id`) REFERENCES `webapi_activities` (`activity_id`);
ALTER TABLE `webapi_participants` ADD CONSTRAINT `participant_id_refs_user_id_2949c3f8` FOREIGN KEY (`participant_id`) REFERENCES `webapi_user_info` (`user_id`);
CREATE INDEX `webapi_user_info_de5d4d92` ON `webapi_user_info` (`fb_id`);
CREATE INDEX `webapi_user_info_8dc6cb94` ON `webapi_user_info` (`wb_id`);
CREATE INDEX `webapi_friends_6340c63c` ON `webapi_friends` (`user_id`);
CREATE INDEX `webapi_friends_db2d0ac4` ON `webapi_friends` (`friend_id`);
CREATE INDEX `webapi_activities_ad376f8d` ON `webapi_activities` (`creator_id`);
CREATE INDEX `webapi_activities_fa32c756` ON `webapi_activities` (`activity_created_date`);
CREATE INDEX `webapi_activities_0d3a0c9d` ON `webapi_activities` (`longitude`, `latitude`);
CREATE INDEX `webapi_participants_8005e431` ON `webapi_participants` (`activity_id`);
CREATE INDEX `webapi_participants_90a2f7f7` ON `webapi_participants` (`participant_id`);

COMMIT;
