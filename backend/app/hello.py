import os
# import sys

# # Ensure the project root (parent of this file's directory) is on sys.path so
# # that the local `vanna` package can be imported when running this file directly.
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

class MyVanna(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

# Create RAG-Layer directory if it doesn't exist
rag_layer_dir = "RAG-Layer"
if not os.path.exists(rag_layer_dir):
    os.makedirs(rag_layer_dir)
    print(f"📁 Created directory: {rag_layer_dir}")

# Initialize Vanna with RAG-Layer path for ChromaDB storage
vn = MyVanna(config={
    'model': 'phi4-mini:latest',
    'path': rag_layer_dir  # Store ChromaDB data in RAG-Layer directory
})

print(f"📊 Using RAG-Layer directory: {os.path.abspath(rag_layer_dir)}")

# try:
#     vn.connect_to_mysql(host='localhost', dbname='cfms', user='newuser', password='newpassword', port=3306)
#     print("✅ Successfully connected to MySQL database")
# except Exception as e:
#     print(f"❌ Database connection failed: {e}")
#     exit(1)


# vn.train(ddl="""CREATE TABLE `users` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `username` varchar(255) DEFAULT NULL,
#   `email` varchar(255) NOT NULL,
#   `role` varchar(255) DEFAULT NULL,
#   `status` varchar(255) NOT NULL,
#   `email_verified_at` datetime DEFAULT NULL,
#   `password` varchar(255) NOT NULL,
#   `remember_token` varchar(255) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   `location_id` int DEFAULT NULL,
#   `deleted_at` datetime DEFAULT NULL,
#   `corp_id` int DEFAULT NULL,
#   `div_id` int DEFAULT NULL,
#   `brigade_id` int DEFAULT NULL,
#   `unit_id` int DEFAULT NULL,
#   `appt` varchar(255) DEFAULT NULL,
#   `iban` varchar(255) DEFAULT NULL,
#   `update_password_status` tinyint(1) NOT NULL,
#   `is_active` tinyint(1) NOT NULL,
#   `is_superuser` tinyint(1) NOT NULL,
#   PRIMARY KEY (`id`),
#   KEY `brigade_id` (`brigade_id`),
#   KEY `corp_id` (`corp_id`),
#   KEY `div_id` (`div_id`),
#   KEY `unit_id` (`unit_id`),
#   KEY `ix_users_is_superuser` (`is_superuser`),
#   CONSTRAINT `users_ibfk_1` FOREIGN KEY (`brigade_id`) REFERENCES `brigades` (`id`),
#   CONSTRAINT `users_ibfk_2` FOREIGN KEY (`corp_id`) REFERENCES `corps` (`id`),
#   CONSTRAINT `users_ibfk_3` FOREIGN KEY (`div_id`) REFERENCES `divs` (`id`),
#   CONSTRAINT `users_ibfk_4` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)

# vn.train(ddl="""CREATE TABLE `corps` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `corp_img` varchar(255) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   PRIMARY KEY (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `divs` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `corp_id` int DEFAULT NULL,
#   `div_img` varchar(255) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `corp_id` (`corp_id`),
#   CONSTRAINT `divs_ibfk_1` FOREIGN KEY (`corp_id`) REFERENCES `corps` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `brigades` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `div_id` int DEFAULT NULL,
#   `brigade_img` varchar(255) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `div_id` (`div_id`),
#   CONSTRAINT `brigades_ibfk_1` FOREIGN KEY (`div_id`) REFERENCES `divs` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `units` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `brigade_id` int DEFAULT NULL,
#   `unit_img` varchar(255) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `brigade_id` (`brigade_id`),
#   CONSTRAINT `units_ibfk_1` FOREIGN KEY (`brigade_id`) REFERENCES `brigades` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=99 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `apartments` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `description` varchar(255) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   PRIMARY KEY (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `heads` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int DEFAULT NULL,
#   `heads` varchar(255) DEFAULT NULL,
#   `type` int NOT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   `status` int DEFAULT NULL,
#   `deleted_at` datetime DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `ix_heads_type` (`type`),
#   KEY `ix_heads_user_id` (`user_id`),
#   CONSTRAINT `heads_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `sub_heads` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int DEFAULT NULL,
#   `head_id` int DEFAULT NULL,
#   `subheads` varchar(255) DEFAULT NULL,
#   `type` int NOT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   PRIMARY KEY (`id`),
#   KEY `ix_sub_heads_head_id` (`head_id`),
#   KEY `ix_sub_heads_type` (`type`),
#   KEY `ix_sub_heads_user_id` (`user_id`),
#   CONSTRAINT `sub_heads_ibfk_1` FOREIGN KEY (`head_id`) REFERENCES `heads` (`id`),
#   CONSTRAINT `sub_heads_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `command_funds` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `fund_details` text,
#   `amount` decimal(16,2) DEFAULT NULL,
#   `payment_method` varchar(255) DEFAULT NULL,
#   `iban_id` int DEFAULT NULL,
#   `date` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   `created_at` datetime NOT NULL,
#   `user_id` int NOT NULL,
#   `received_from` varchar(255) DEFAULT NULL,
#   `old_amount` int DEFAULT NULL,
#   `is_old_amount` tinyint(1) NOT NULL,
#   `head_id` int DEFAULT NULL,
#   `subhead_id` int DEFAULT NULL,
#   `deleted_at` datetime DEFAULT NULL,
#   `is_deleted` tinyint(1) NOT NULL,
#   `liability_id` int DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `ix_command_funds_date` (`date`),
#   KEY `ix_command_funds_head_id` (`head_id`),
#   KEY `ix_command_funds_iban_id` (`iban_id`),
#   KEY `ix_command_funds_is_deleted` (`is_deleted`),
#   KEY `ix_command_funds_liability_id` (`liability_id`),
#   KEY `ix_command_funds_subhead_id` (`subhead_id`),
#   KEY `ix_command_funds_user_id` (`user_id`),
#   CONSTRAINT `command_funds_ibfk_1` FOREIGN KEY (`head_id`) REFERENCES `heads` (`id`),
#   CONSTRAINT `command_funds_ibfk_2` FOREIGN KEY (`iban_id`) REFERENCES `multi_ibn_user` (`id`),
#   CONSTRAINT `command_funds_ibfk_3` FOREIGN KEY (`subhead_id`) REFERENCES `sub_heads` (`id`),
#   CONSTRAINT `command_funds_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
#   CONSTRAINT `command_funds_ibfk_5` FOREIGN KEY (`liability_id`) REFERENCES `liabilities` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""")
# vn.train(ddl="""CREATE TABLE `expenses` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int NOT NULL,
#   `expense_id` varchar(255) DEFAULT NULL,
#   `type` varchar(255) DEFAULT NULL,
#   `cost` decimal(16,2) DEFAULT NULL,
#   `payment_type` varchar(255) DEFAULT NULL,
#   `payment_to` varchar(255) DEFAULT NULL,
#   `expense_date` datetime DEFAULT NULL,
#   `picture` varchar(255) DEFAULT NULL,
#   `reciept` varchar(255) DEFAULT NULL,
#   `site_id` int DEFAULT NULL,
#   `category_id` int DEFAULT NULL,
#   `iban_id` int DEFAULT NULL,
#   `corps_id` int DEFAULT NULL,
#   `div_id` int DEFAULT NULL,
#   `brigade_id` int DEFAULT NULL,
#   `unit_id` int DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   `asset_id` int DEFAULT NULL,
#   `liability_id` int DEFAULT NULL,
#   `fixed_asset_id` int DEFAULT NULL,
#   `head_id` int DEFAULT NULL,
#   `subhead_id` int DEFAULT NULL,
#   `is_deleted` tinyint(1) NOT NULL,
#   `deleted_at` datetime DEFAULT NULL,
#   `head_details` text,
#   `place_type` varchar(255) DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `brigade_id` (`brigade_id`),
#   KEY `corps_id` (`corps_id`),
#   KEY `div_id` (`div_id`),
#   KEY `unit_id` (`unit_id`),
#   KEY `ix_expenses_asset_id` (`asset_id`),
#   KEY `ix_expenses_expense_date` (`expense_date`),
#   KEY `ix_expenses_fixed_asset_id` (`fixed_asset_id`),
#   KEY `ix_expenses_head_id` (`head_id`),
#   KEY `ix_expenses_iban_id` (`iban_id`),
#   KEY `ix_expenses_is_deleted` (`is_deleted`),
#   KEY `ix_expenses_liability_id` (`liability_id`),
#   KEY `ix_expenses_subhead_id` (`subhead_id`),
#   KEY `ix_expenses_user_id` (`user_id`),
#   CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`asset_id`) REFERENCES `assets` (`id`),
#   CONSTRAINT `expenses_ibfk_10` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`),
#   CONSTRAINT `expenses_ibfk_11` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
#   CONSTRAINT `expenses_ibfk_2` FOREIGN KEY (`brigade_id`) REFERENCES `brigades` (`id`),
#   CONSTRAINT `expenses_ibfk_3` FOREIGN KEY (`corps_id`) REFERENCES `corps` (`id`),
#   CONSTRAINT `expenses_ibfk_4` FOREIGN KEY (`div_id`) REFERENCES `divs` (`id`),
#   CONSTRAINT `expenses_ibfk_5` FOREIGN KEY (`fixed_asset_id`) REFERENCES `fixed_assets` (`id`),
#   CONSTRAINT `expenses_ibfk_6` FOREIGN KEY (`head_id`) REFERENCES `heads` (`id`),
#   CONSTRAINT `expenses_ibfk_7` FOREIGN KEY (`iban_id`) REFERENCES `multi_ibn_user` (`id`),
#   CONSTRAINT `expenses_ibfk_8` FOREIGN KEY (`liability_id`) REFERENCES `liabilities` (`id`),
#   CONSTRAINT `expenses_ibfk_9` FOREIGN KEY (`subhead_id`) REFERENCES `sub_heads` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `assets` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `subhead` varchar(255) DEFAULT NULL,
#   `type` varchar(255) DEFAULT NULL,
#   `purchase_date` datetime DEFAULT NULL,
#   `model` varchar(255) DEFAULT NULL,
#   `asset_id` varchar(255) DEFAULT NULL,
#   `purchased_from` varchar(255) DEFAULT NULL,
#   `brand` varchar(255) DEFAULT NULL,
#   `serial_number` varchar(255) DEFAULT NULL,
#   `cost` decimal(16,2) DEFAULT NULL,
#   `site_id` int DEFAULT NULL,
#   `location_id` int DEFAULT NULL,
#   `category_id` int DEFAULT NULL,
#   `department_id` int DEFAULT NULL,
#   `depreciation_method_id` int DEFAULT NULL,
#   `assign_to_id` int DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   `status` varchar(255) DEFAULT NULL,
#   `deleted_at` datetime DEFAULT NULL,
#   `salvage_value` varchar(255) DEFAULT NULL,
#   `useful_life` int DEFAULT NULL,
#   `image` varchar(255) DEFAULT NULL,
#   `remarks` varchar(255) DEFAULT NULL,
#   `receipt` varchar(255) DEFAULT NULL,
#   `purchased_by` int DEFAULT NULL,
#   `user_id` int DEFAULT NULL,
#   `place_type` varchar(255) DEFAULT NULL,
#   `payment_type` varchar(255) DEFAULT NULL,
#   `payment_to` varchar(255) DEFAULT NULL,
#   `dispose_status` varchar(255) DEFAULT NULL,
#   `sell_price` decimal(10,0) DEFAULT NULL,
#   `sold_to` varchar(255) DEFAULT NULL,
#   `gift_to` varchar(255) DEFAULT NULL,
#   `disposed_reason` varchar(255) DEFAULT NULL,
#   `disposed_date` datetime DEFAULT NULL,
#   `head_details` text,
#   `quantity` int DEFAULT NULL,
#   `depreciation_percentage` float DEFAULT NULL,
#   `depreciation_type` varchar(255) DEFAULT NULL,
#   `iban_id` int DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `user_id` (`user_id`),
#   KEY `ix_assets_iban_id` (`iban_id`),
#   CONSTRAINT `assets_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
#   CONSTRAINT `assets_ibfk_2` FOREIGN KEY (`iban_id`) REFERENCES `multi_ibn_user` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=41 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""")
# vn.train(ddl="""CREATE TABLE `fixed_assets` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int DEFAULT NULL,
#   `name` varchar(255) DEFAULT NULL,
#   `asset_details` text,
#   `amount` decimal(16,2) DEFAULT NULL,
#   `payment_method` varchar(255) DEFAULT NULL,
#   `iban_id` int DEFAULT NULL,
#   `date` datetime DEFAULT NULL,
#   `type` varchar(255) DEFAULT NULL,
#   `is_deleted` tinyint(1) NOT NULL,
#   `deleted_at` datetime DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `ix_fixed_assets_date` (`date`),
#   KEY `ix_fixed_assets_iban_id` (`iban_id`),
#   KEY `ix_fixed_assets_is_deleted` (`is_deleted`),
#   KEY `ix_fixed_assets_user_id` (`user_id`),
#   CONSTRAINT `fixed_assets_ibfk_1` FOREIGN KEY (`iban_id`) REFERENCES `multi_ibn_user` (`id`),
#   CONSTRAINT `fixed_assets_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `investment_balance_histories` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int DEFAULT NULL,
#   `investment_id` int DEFAULT NULL,
#   `first_balance` decimal(10,0) NOT NULL,
#   `last_balance` decimal(10,0) NOT NULL,
#   `date` varchar(255) NOT NULL,
#   `status` varchar(255) NOT NULL,
#   `description` text,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `investment_id` (`investment_id`),
#   KEY `user_id` (`user_id`),
#   CONSTRAINT `investment_balance_histories_ibfk_1` FOREIGN KEY (`investment_id`) REFERENCES `fixed_assets` (`id`),
#   CONSTRAINT `investment_balance_histories_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""")
# vn.train(ddl="""CREATE TABLE `liabilities` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) DEFAULT NULL,
#   `subhead` varchar(255) DEFAULT NULL,
#   `fund_details` text,
#   `amount` decimal(16,2) DEFAULT NULL,
#   `payment_method` varchar(255) DEFAULT NULL,
#   `date` datetime NOT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   `user_id` int NOT NULL,
#   `iban_id` int DEFAULT NULL,
#   `payment_to` varchar(255) DEFAULT NULL,
#   `schedule` varchar(255) DEFAULT NULL,
#   `type` varchar(255) DEFAULT NULL,
#   `is_deleted` tinyint(1) NOT NULL,
#   `is_new_entry_created` tinyint(1) DEFAULT NULL,
#   `is_paid` tinyint(1) NOT NULL,
#   `deleted_at` datetime DEFAULT NULL,
#   `remaining_balance` decimal(16,2) DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `ix_liabilities_date` (`date`),
#   KEY `ix_liabilities_iban_id` (`iban_id`),
#   KEY `ix_liabilities_is_deleted` (`is_deleted`),
#   KEY `ix_liabilities_is_paid` (`is_paid`),
#   KEY `ix_liabilities_user_id` (`user_id`),
#   CONSTRAINT `liabilities_ibfk_1` FOREIGN KEY (`iban_id`) REFERENCES `multi_ibn_user` (`id`),
#   CONSTRAINT `liabilities_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `liability_balances` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int DEFAULT NULL,
#   `liability_id` int DEFAULT NULL,
#   `first_balance` decimal(10,0) DEFAULT NULL,
#   `last_balance` decimal(10,0) DEFAULT NULL,
#   `payment_type` varchar(255) NOT NULL,
#   `date` varchar(255) NOT NULL,
#   `status` varchar(255) NOT NULL,
#   `description` text,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime DEFAULT NULL,
#   `payment_to` varchar(255) DEFAULT NULL,
#   `current_amount` decimal(16,2) DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `liability_id` (`liability_id`),
#   KEY `user_id` (`user_id`),
#   CONSTRAINT `liability_balances_ibfk_1` FOREIGN KEY (`liability_id`) REFERENCES `liabilities` (`id`),
#   CONSTRAINT `liability_balances_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""")
# vn.train(ddl="""CREATE TABLE `formation_assignments` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `name` varchar(255) NOT NULL,
#   `oas_id` varchar(255) DEFAULT NULL,
#   `user_id` int NOT NULL,
#   `start_at` datetime NOT NULL,
#   `end_at` datetime DEFAULT NULL,
#   `status` varchar(20) NOT NULL,
#   `handover_notes` text,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   PRIMARY KEY (`id`),
#   KEY `ix_formation_assignments_end_at` (`end_at`),
#   KEY `ix_formation_assignments_oas_id` (`oas_id`),
#   KEY `ix_formation_assignments_start_at` (`start_at`),
#   KEY `ix_formation_assignments_status` (`status`),
#   KEY `ix_formation_assignments_user_id` (`user_id`),
#   CONSTRAINT `formation_assignments_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `activity_log` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `log_name` varchar(255) DEFAULT NULL,
#   `description` text,
#   `subject_type` varchar(255) DEFAULT NULL,
#   `event` varchar(255) DEFAULT NULL,
#   `subject_id` int DEFAULT NULL,
#   `causer_type` varchar(255) DEFAULT NULL,
#   `causer_id` int DEFAULT NULL,
#   `properties` varchar(255) DEFAULT NULL,
#   `batch_uuid` varchar(36) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   `my_custom_field` varchar(255) DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `causer_id` (`causer_id`),
#   KEY `ix_activity_log_causer_type` (`causer_type`),
#   KEY `ix_activity_log_log_name` (`log_name`),
#   KEY `ix_activity_log_subject_type` (`subject_type`),
#   CONSTRAINT `activity_log_ibfk_1` FOREIGN KEY (`causer_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=129 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `balances` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int NOT NULL,
#   `cash_in_hand` decimal(16,2) DEFAULT NULL,
#   `cash_in_bank` decimal(16,2) DEFAULT NULL,
#   `balance` decimal(16,2) DEFAULT NULL,
#   `created_at` datetime NOT NULL,
#   `updated_at` datetime NOT NULL,
#   PRIMARY KEY (`id`),
#   KEY `user_id` (`user_id`),
#   CONSTRAINT `balances_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `multi_ibn_user` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int DEFAULT NULL,
#   `ibn` varchar(255) DEFAULT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   `bank_name` varchar(255) DEFAULT NULL,
#   `allocated_balance` decimal(16,2) DEFAULT NULL,
#   PRIMARY KEY (`id`),
#   KEY `user_id` (`user_id`),
#   CONSTRAINT `multi_ibn_user_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
# """)
# vn.train(ddl="""CREATE TABLE `iban_transfers` (
#   `id` int NOT NULL AUTO_INCREMENT,
#   `user_id` int NOT NULL,
#   `from_iban_id` int NOT NULL,
#   `to_iban_id` int NOT NULL,
#   `amount` decimal(16,2) NOT NULL,
#   `transaction_id` varchar(100) DEFAULT NULL,
#   `transfer_date` datetime NOT NULL,
#   `remarks` text,
#   `status` varchar(20) NOT NULL,
#   `created_at` datetime DEFAULT NULL,
#   `updated_at` datetime NOT NULL,
#   PRIMARY KEY (`id`),
#   KEY `ix_iban_transfers_from_iban_id` (`from_iban_id`),
#   KEY `ix_iban_transfers_status` (`status`),
#   KEY `ix_iban_transfers_to_iban_id` (`to_iban_id`),
#   KEY `ix_iban_transfers_transaction_id` (`transaction_id`),
#   KEY `ix_iban_transfers_transfer_date` (`transfer_date`),
#   KEY `ix_iban_transfers_user_id` (`user_id`),
#   CONSTRAINT `iban_transfers_ibfk_1` FOREIGN KEY (`from_iban_id`) REFERENCES `multi_ibn_user` (`id`),
#   CONSTRAINT `iban_transfers_ibfk_2` FOREIGN KEY (`to_iban_id`) REFERENCES `multi_ibn_user` (`id`),
#   CONSTRAINT `iban_transfers_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci""")




vn.train(documentation="""Our business defines formations as users in military and the corps, divs, brigades and units as the formations hierarchy and apartments as the formation appointments.
         The heads and sub_heads tables are used to store the heads and sub_heads of the formations to track the inflows and outflows.
         - inflows means the incoming funds to the formations which are tracked in the command_funds table.
         - outflows means the outgoing funds from the formations which are tracked in the expenses table.
         - both the heads and sub_heads have a column called type which is used to differentiate between the inflows and outflows.
         - the heads and sub_heads type=1 indicates inflows and type=2 indicates outflows.
         """)
# vn.train(documentation="""Our bussiness define Inventory tracking as assets table. which are basically the outflows of the formations but with type=NONEXPENDABLE.
#          - The Investment tracking as fixed_assets table. which is also outflows of the formations but tracked separately as fixed_assets. and the history of each investment is tracked in the investment_balance_histories table.
#          - The Liabilities tracking as liabilities table. which is the liability on formations that need to be paid back. and the history of each liability is tracked in the liability_balances table.
#          - The Commanding Officers (CO) or Acct Offr or Acctountants of each formations are tracked in formation_assignments table. the differece between CO and Acct Offr is hadled through status column in the formation_assignments table. for CO, status=CO and for Acct Offr, status=	2IC.
#          - The each activity of each formation is tracked in activity_log table.
#          - The balance of each formation is tracked in balances table. this is the actual balance of the formations. cash_in_hand is the cash in hand of the formations. cash_in_bank is the cash in bank of the formations. balance is the total balance of the formations.
#          - The ibn of each formation is tracked in multi_ibn_user table. this is the ibn of the formations. ibn is the ibn of the formations.
#          - The ibn transfers are tracked in iban_transfers table. this is the ibn transfers of the formations. like from one ibn to another ibn.
#          """)

# # Enhanced business documentation for better context
# vn.train(documentation="""CFMS (Command Funds Management System) Business Rules:
#          - Users represent military personnel assigned to different formations
#          - Status field in users: 'active', 'inactive', 'transferred'
#          - Role field common values: 'CO' (Commanding Officer), 'Accountant', 'Clerk', 'Personnel'
#          - Each user belongs to a formation hierarchy: Corps > Division > Brigade > Unit
#          - cash_in_hand represents physical cash available to the formation
#          - cash_in_bank represents bank account balances
#          - balance field in balances table = cash_in_hand + cash_in_bank
#          """)

# vn.train(documentation="""Financial Terms and Processes:
#          - Command Funds: Budget allocations from higher command (inflows)
#          - Expenses: Money spent on operations, supplies, salaries (outflows)  
#          - Assets: Non-expendable items purchased (equipment, vehicles, furniture)
#          - Fixed Assets: Long-term investments and infrastructure
#          - Liabilities: Debts or obligations that need to be repaid
#          - IBAN: International Bank Account Number for each formation
#          - When is_paid = 0 in liabilities, it means the liability is outstanding
#          - When is_deleted = 1, the record is soft-deleted (not physically removed)
#          """)

# vn.train(documentation="""Common Query Patterns:
#          - Always check deleted_at IS NULL for active records
#          - Use is_active = 1 for active users
#          - Join users table to get formation names and responsible personnel
#          - Date filtering: Use MONTH() and YEAR() functions for monthly/yearly reports
#          - For hierarchy queries, join corps -> divs -> brigades -> units
#          - For financial summaries, use SUM() and GROUP BY formation
#          """)

# # Add sample SQL patterns for complex joins
# vn.train(sql="SELECT u.name, c.name as corps, d.name as division FROM users u LEFT JOIN corps c ON u.corp_id = c.id LEFT JOIN divs d ON u.div_id = d.id WHERE u.deleted_at IS NULL")

# vn.train(sql="SELECT u.name as formation, SUM(e.amount) as total_expenses FROM users u JOIN expenses e ON u.id = e.user_id GROUP BY u.id, u.name")

# vn.train(sql="SELECT l.name, l.amount, l.date FROM liabilities l WHERE l.is_paid = 0 AND l.is_deleted = 0")

# # Add comprehensive question-SQL pairs for military formations financial management
# vn.train(
#     question="How many active users are there in the system?",
#     sql="SELECT COUNT(*) FROM users WHERE is_active = 1 AND deleted_at IS NULL"
# )

# vn.train(
#     question="Show me all users in a specific brigade",
#     sql="SELECT u.name, u.username, u.email, u.role FROM users u JOIN brigades b ON u.brigade_id = b.id WHERE b.name = 'Brigade Name' AND u.deleted_at IS NULL"
# )

# vn.train(
#     question="What is the current balance for each formation?",
#     sql="SELECT u.name as formation_name, b.cash_in_hand, b.cash_in_bank, b.balance FROM users u JOIN balances b ON u.id = b.user_id ORDER BY b.balance DESC"
# )

# vn.train(
#     question="What are the total inflows for each formation?",
#     sql="SELECT u.name as formation_name, SUM(cf.amount) as total_inflows FROM users u JOIN command_funds cf ON u.id = cf.user_id GROUP BY u.id, u.name ORDER BY total_inflows DESC"
# )

# vn.train(
#     question="Show me all unpaid liabilities",
#     sql="SELECT l.name, l.amount, l.payment_to, l.date, u.name as responsible_user FROM liabilities l JOIN users u ON l.user_id = u.id WHERE l.is_paid = 0 AND l.is_deleted = 0 ORDER BY l.date"
# )

# vn.train(
#     question="Who are the current commanding officers?",
#     sql="SELECT u.name, u.email, fa.name as appointment, fa.start_at FROM users u JOIN formation_assignments fa ON u.id = fa.user_id WHERE fa.status = 'CO' AND fa.end_at IS NULL"
# )

# vn.train(
#     question="What is the hierarchy structure from corps to units?",
#     sql="SELECT c.name as corps, d.name as division, b.name as brigade, un.name as unit FROM corps c JOIN divs d ON c.id = d.corp_id JOIN brigades br ON d.id = br.div_id JOIN units un ON br.id = un.brigade_id ORDER BY c.name, d.name, b.name, un.name"
# )

# vn.train(
#     question="Show me all IBAN transfers for this month",
#     sql="SELECT it.amount, it.transfer_date, from_iban.ibn as from_account, to_iban.ibn as to_account, u.name as user_name FROM iban_transfers it JOIN multi_ibn_user from_iban ON it.from_iban_id = from_iban.id JOIN multi_ibn_user to_iban ON it.to_iban_id = to_iban.id JOIN users u ON it.user_id = u.id WHERE MONTH(it.transfer_date) = MONTH(CURRENT_DATE()) AND YEAR(it.transfer_date) = YEAR(CURRENT_DATE())"
# )

# vn.train(
#     question="What are the total assets by formation?",
#     sql="SELECT u.name as formation_name, COUNT(a.id) as total_assets, SUM(a.cost) as total_cost FROM users u JOIN assets a ON u.id = a.user_id WHERE a.is_deleted = 0 GROUP BY u.id, u.name ORDER BY total_cost DESC"
# )

# vn.train(
#     question="Show me activity log for a specific user",
#     sql="SELECT al.description, al.event, al.created_at, u.name as causer FROM activity_log al LEFT JOIN users u ON al.causer_id = u.id WHERE al.subject_id = ? ORDER BY al.created_at DESC"
# )

# vn.train(
#     question="What are the fixed assets (investments) and their current values?",
#     sql="SELECT fa.name, fa.initial_value, fa.current_value, fa.date_acquired, u.name as responsible_user FROM fixed_assets fa JOIN users u ON fa.user_id = u.id WHERE fa.is_deleted = 0 ORDER BY fa.current_value DESC"
# )

# # Military-specific queries
# vn.train(
#     question="Show me the chain of command hierarchy",
#     sql="SELECT c.name as corps, d.name as division, b.name as brigade, un.name as unit, u.name as personnel, u.role FROM users u LEFT JOIN corps c ON u.corp_id = c.id LEFT JOIN divs d ON u.div_id = d.id LEFT JOIN brigades b ON u.brigade_id = b.id LEFT JOIN units un ON u.unit_id = un.id WHERE u.deleted_at IS NULL ORDER BY c.name, d.name, b.name, un.name"
# )

# vn.train(
#     question="What are the budget allocations vs expenditures?",
#     sql="SELECT u.name as formation, COALESCE(SUM(cf.amount), 0) as total_allocated, COALESCE(SUM(e.amount), 0) as total_spent, (COALESCE(SUM(cf.amount), 0) - COALESCE(SUM(e.amount), 0)) as remaining FROM users u LEFT JOIN command_funds cf ON u.id = cf.user_id LEFT JOIN expenses e ON u.id = e.user_id WHERE u.deleted_at IS NULL GROUP BY u.id, u.name ORDER BY remaining DESC"
# )

# vn.train(
#     question="Show me personnel with specific appointments",
#     sql="SELECT u.name, u.email, u.appt as appointment, c.name as corps, d.name as division FROM users u LEFT JOIN corps c ON u.corp_id = c.id LEFT JOIN divs d ON u.div_id = d.id WHERE u.appt IS NOT NULL AND u.deleted_at IS NULL ORDER BY u.appt"
# )

# # Financial analysis queries
# vn.train(
#     question="Monthly expense breakdown by category",
#     sql="SELECT sh.heads as expense_category, MONTH(e.date) as month, SUM(e.amount) as total_amount FROM expenses e JOIN sub_heads sh ON e.sub_head_id = sh.id WHERE YEAR(e.date) = YEAR(CURRENT_DATE()) GROUP BY sh.heads, MONTH(e.date) ORDER BY month, total_amount DESC"
# )

# # Auto-generate training plan from database schema
# print("📊 Extracting database schema for training plan...")
# df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'cfms'")

# # This will break up the information schema into bite-sized chunks that can be referenced by the LLM
# plan = vn.get_training_plan_generic(df_information_schema)

# print("="*100)
# print("📋 Training Plan Generated:")
# print(plan)
# print("="*100)

# # Execute the training plan (previously commented out)
# print("🚀 Executing training plan...")
# vn.train(plan=plan)
# print("✅ Training plan executed successfully!")

# print("🎯 Training Summary:")
# print("- ✅ DDL Statements: All major tables trained")
# print("- ✅ Business Documentation: Military formations and financial context")
# print("- ✅ Question-SQL Pairs: 15+ domain-specific examples")
# print("- ✅ Schema Training Plan: Auto-generated from information schema")
# print("- ✅ SQL Examples: Common query patterns")
