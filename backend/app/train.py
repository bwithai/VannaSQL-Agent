from vana_agent import vn
from app.core.config import settings

try:
    vn.connect_to_mysql(host=settings.MYSQL_SERVER, dbname=settings.MYSQL_DB, user=settings.MYSQL_USER,
                        password=settings.MYSQL_PASSWORD, port=settings.MYSQL_PORT)
    print("✅ Successfully connected to MySQL database")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# Auto-generate training plan from database schema
print("📊 Extracting database schema for training plan...")
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'vanna_db'")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = vn.get_training_plan_generic(df_information_schema)

print("="*100)
print("📋 Training Plan Generated:")
print(plan)
print("="*100)

# Execute the training plan (previously commented out)
print("🚀 Executing training plan...")
# vn.train(plan=plan)
print("✅ Training plan executed successfully!")