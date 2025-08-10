from vana_agent import vn
from app.coree.config import settings, Settings

try:
    vn.connect_to_mysql(host=settings.MYSQL_SERVER, dbname=Settings.MYSQL_DB, user=settings.MYSQL_USER,
                        password=Settings.MYSQL_PASSWORD, port=Settings.MYSQL_PORT)
    print("✅ Successfully connected to MySQL database")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)

# Train the model
vn.train(documentation="""Our business defines formations as users in military and the corps, divs, brigades and units as the formations hierarchy and apartments as the formation appointments.
         The heads and sub_heads tables are used to store the heads and sub_heads of the formations to track the inflows and outflows.
         - inflows means the incoming funds to the formations which are tracked in the command_funds table.
         - outflows means the outgoing funds from the formations which are tracked in the expenses table.
         - both the heads and sub_heads have a column called type which is used to differentiate between the inflows and outflows.
         - the heads and sub_heads type=1 indicates inflows and type=2 indicates outflows.
         """)
