from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

vn = MyVanna(config={'model': 'phi4-mini:latest'})

try:
    vn.connect_to_mysql(host='localhost', dbname='cfms', user='newuser', password='newpassword', port=3306)
    print("✅ Successfully connected to MySQL database")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# The information schema query may need some tweaking depending on your database. This is a good starting point.
print("📊 Extracting database schema...")
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = vn.get_training_plan_generic(df_information_schema)

# If you like the plan, then uncomment this and run it to train
vn.train(plan=plan)

# Add CFMS-specific training data
print("📚 Adding CFMS-specific training data...")

# Add documentation about your CFMS database structure
vn.train(documentation="""
CFMS (Command Fund Management System) is a financial management system designed to manage command funds within a military formation. Below is an overview of the database structure:

- **users**: Stores user details. The `is_active` column indicates whether a user is active (1) or inactive (0). The `role` column contains the user’s role as a string. Each user represents a military formation.
- **command_funds**: Records incoming funds received by the formation (inflows).
- **activity_log**: Logs all system activities performed by users.
- **apartments**: Stores appointment details related to formations.
- **assets**: Maintains records of inventory and asset details.
- **balances**: Represents the current financial balance of each formation (user).
- **brigades**, **corps**, **divs**, **units**: Represent the hierarchical structure of military formations.
- **expenses**: Stores financial outflows made by users.
- **fixed_assets**: Contains details of long-term investments made by users.
- **formation_assignments**: Tracks officeholders (current and past) assigned to specific formations.
- **heads**, **subheads**: Represent fund categories. If `type = 1`, they indicate inflows; if `type = 2`, they indicate outflows.
- **iban_transfers**: Tracks balance allocations and transfers between IBANs assigned to users.
- **investment_balance_histories**: Maintains a historical log of investment balances.
- **liabilities**: Records current liabilities for each user.
- **liability_balances**: Stores historical liability balance changes.
- **multi_ibn_user**: Stores the IBAN account details associated with users.

This structure enables CFMS to track financial operations and hierarchy in a secure and organized manner.
""")

# Add specific documentation about organizational hierarchy relationships
vn.train(documentation="""
IMPORTANT: CFMS Users have DIRECT foreign keys to all hierarchy levels:

Organizational Hierarchy Relationships in CFMS:
- corps table: Contains top-level military corps formations
- divs table: Contains divisions  
- brigades table: Contains brigades
- units table: Contains units
- users table: Contains users with DIRECT foreign keys to all levels:
  * corp_id -> corps.id
  * div_id -> divs.id  
  * brigade_id -> brigades.id
  * unit_id -> units.id

CRITICAL: Users are NOT cascaded through the hierarchy. Each user has direct links to their corps, division, brigade, and unit.

For organizational hierarchy queries with users, ALWAYS use this pattern:
FROM users usr
LEFT JOIN corps c ON usr.corp_id = c.id
LEFT JOIN divs d ON usr.div_id = d.id
LEFT JOIN brigades b ON usr.brigade_id = b.id
LEFT JOIN units u ON usr.unit_id = u.id
WHERE usr.is_active = 1
""")

# Add example DDL for organizational hierarchy tables
vn.train(ddl="""
CREATE TABLE `corps` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `corp_img` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
""")

vn.train(ddl="""
CREATE TABLE `divs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `corp_id` int DEFAULT NULL,
  `div_img` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `corp_id` (`corp_id`),
  CONSTRAINT `divs_ibfk_1` FOREIGN KEY (`corp_id`) REFERENCES `corps` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

""")

vn.train(ddl="""
CREATE TABLE `brigades` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `div_id` int DEFAULT NULL,
  `brigade_img` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `div_id` (`div_id`),
  CONSTRAINT `brigades_ibfk_1` FOREIGN KEY (`div_id`) REFERENCES `divs` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=109 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

""")

vn.train(ddl="""
CREATE TABLE `units` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `brigade_id` int DEFAULT NULL,
  `unit_img` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `brigade_id` (`brigade_id`),
  CONSTRAINT `units_ibfk_1` FOREIGN KEY (`brigade_id`) REFERENCES `brigades` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=217 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
""")

vn.train(ddl="""
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `username` varchar(255) DEFAULT NULL,
  `email` varchar(255) NOT NULL,
  `role` varchar(255) DEFAULT NULL,
  `status` varchar(255) NOT NULL,
  `email_verified_at` datetime DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `remember_token` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime NOT NULL,
  `location_id` int DEFAULT NULL,
  `deleted_at` datetime DEFAULT NULL,
  `corp_id` int DEFAULT NULL,
  `div_id` int DEFAULT NULL,
  `brigade_id` int DEFAULT NULL,
  `unit_id` int DEFAULT NULL,
  `appt` varchar(255) DEFAULT NULL,
  `iban` varchar(255) DEFAULT NULL,
  `update_password_status` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `corp_id` (`corp_id`),
  KEY `div_id` (`div_id`),
  KEY `brigade_id` (`brigade_id`),
  KEY `unit_id` (`unit_id`),
  KEY `ix_users_is_superuser` (`is_superuser`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`corp_id`) REFERENCES `corps` (`id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`div_id`) REFERENCES `divs` (`id`),
  CONSTRAINT `users_ibfk_3` FOREIGN KEY (`brigade_id`) REFERENCES `brigades` (`id`),
  CONSTRAINT `users_ibfk_4` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
""")

# Add example queries for common CFMS operations
vn.train(sql="SELECT username, role FROM users WHERE is_active = 1")
vn.train(sql="SELECT username, name, email, role FROM users WHERE is_active = 1 AND role = 'admin'")
vn.train(sql="SELECT COUNT(*) as active_users FROM users WHERE is_active = 1")
vn.train(sql="SELECT role, COUNT(*) as user_count FROM users WHERE is_active = 1 GROUP BY role")

# Add organizational hierarchy queries - CORRECT PATTERN based on actual schema
# Users have DIRECT foreign keys to all hierarchy levels, not cascading

vn.train(sql="""SELECT 
    c.name as corps_name,
    d.name as division_name,
    b.name as brigade_name,
    u.name as unit_name,
    usr.username,
    usr.name as user_name,
    usr.role
FROM users usr
LEFT JOIN corps c ON usr.corp_id = c.id
LEFT JOIN divs d ON usr.div_id = d.id
LEFT JOIN brigades b ON usr.brigade_id = b.id
LEFT JOIN units u ON usr.unit_id = u.id
WHERE usr.is_active = 1
ORDER BY c.name, d.name, b.name, u.name, usr.name""")

vn.train(sql="""SELECT 
    c.name as corps_name,
    d.name as division_name,
    b.name as brigade_name,
    u.name as unit_name,
    COUNT(usr.id) as users_count
FROM users usr
LEFT JOIN corps c ON usr.corp_id = c.id
LEFT JOIN divs d ON usr.div_id = d.id
LEFT JOIN brigades b ON usr.brigade_id = b.id
LEFT JOIN units u ON usr.unit_id = u.id
WHERE usr.is_active = 1
GROUP BY c.id, c.name, d.id, d.name, b.id, b.name, u.id, u.name
ORDER BY c.name, d.name, b.name, u.name""")

vn.train(sql="""SELECT usr.username, usr.role, c.name as corps, d.name as division, b.name as brigade, u.name as unit
FROM users usr
LEFT JOIN corps c ON usr.corp_id = c.id
LEFT JOIN divs d ON usr.div_id = d.id
LEFT JOIN brigades b ON usr.brigade_id = b.id
LEFT JOIN units u ON usr.unit_id = u.id
WHERE usr.is_active = 1""")

# Add the exact query format for the user's specific question
vn.train(sql="""SELECT
    usr.username,
    usr.role,
    c.name as corps_name,
    d.name as division_name,
    b.name as brigade_name,
    u.name as unit_name
FROM users usr
LEFT JOIN corps c ON usr.corp_id = c.id
LEFT JOIN divs d ON usr.div_id = d.id
LEFT JOIN brigades b ON usr.brigade_id = b.id
LEFT JOIN units u ON usr.unit_id = u.id
WHERE usr.is_active = 1
ORDER BY c.name, d.name, b.name, u.name""")

# Add training for specific question patterns about organizational hierarchy
vn.train(documentation="When asked for 'complete organizational hierarchy' or 'organizational hierarchy with users', join users table with corps, divs, brigades, and units using DIRECT foreign keys from users table.")
vn.train(documentation="Questions about 'active users with roles with Complete organizational hierarchy' should generate: SELECT c.name as corps_name, d.name as division_name, b.name as brigade_name, u.name as unit_name, usr.username, usr.role FROM users usr LEFT JOIN corps c ON usr.corp_id = c.id LEFT JOIN divs d ON usr.div_id = d.id LEFT JOIN brigades b ON usr.brigade_id = b.id LEFT JOIN units u ON usr.unit_id = u.id WHERE usr.is_active = 1")

# Reinforce exact table names to prevent typos
vn.train(documentation="Table names are EXACTLY: users, corps, divs, brigades, units. Never use corpres, corp, or other variations.")
vn.train(sql="SELECT * FROM corps")
vn.train(sql="SELECT * FROM divs") 
vn.train(sql="SELECT * FROM brigades")
vn.train(sql="SELECT * FROM units")
vn.train(sql="SELECT * FROM users WHERE is_active = 1")

print("✅ CFMS training complete!")
print("🚀 The model now understands your CFMS database structure better.")