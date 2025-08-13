from app.vana_agent import vn
from app.core.config import settings

try:
    vn.connect_to_mysql(host=settings.MYSQL_SERVER, dbname=settings.MYSQL_DB, user=settings.MYSQL_USER,
                        password=settings.MYSQL_PASSWORD, port=settings.MYSQL_PORT)
    print("✅ Successfully connected to MySQL database")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

vn.train(ddl="""CREATE TABLE `discipline_data` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT 'Primary key',
  `doc` date DEFAULT NULL COMMENT 'Date of commission / date of joining',
  `cat` varchar(255) DEFAULT NULL COMMENT 'Category of offence (e.g., violation of SOP)',
  `initiation_date` datetime DEFAULT NULL COMMENT 'Exact initiation datetime (yyyy-mm-dd 00:00:00)',
  `arm` varchar(128) DEFAULT NULL COMMENT 'Employment/arm reflecting war fighting capability',
  `course` varchar(64) DEFAULT NULL COMMENT 'Unique batch number on passing out from academy',
  `svc_no` varchar(64) DEFAULT NULL COMMENT 'Unique service number (e.g., PA-12345)',
  `rank` varchar(64) DEFAULT NULL COMMENT 'Rank of the person',
  `name` varchar(255) DEFAULT NULL COMMENT 'Name of the person',
  `parent_unit` varchar(255) DEFAULT NULL COMMENT 'First joining unit after academy',
  `initiated_by` varchar(255) DEFAULT NULL COMMENT 'Unit/formation initiating the award (organization name)',
  `award` text COMMENT 'Punishment awarded by formation/HQ (e.g., severe displeasure, warning, reprimand)',
  `initiation_year` int DEFAULT NULL COMMENT 'Year when the case was initiated (e.g., 2020)',
  `svc_bracket` int DEFAULT NULL COMMENT 'Service in years at time of award (e.g., 5)',
  `awardee_unit` varchar(255) DEFAULT NULL COMMENT 'Unit where the person received the award',
  PRIMARY KEY (`id`),
  KEY `ix_discipline_data_name` (`name`),
  KEY `ix_discipline_data_svc_no` (`svc_no`),
  KEY `ix_discipline_data_initiation_year` (`initiation_year`),
  KEY `ix_discipline_data_course` (`course`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""")