# Add comprehensive training after the basic DDL training

# Add more comprehensive business documentation
vn.train(documentation="""
CFMS (Command Fund Management System) is a military financial management system that handles:
- Formation hierarchy: Corps -> Divs -> Brigades -> Units
- Personnel management with roles and appointments
- Financial tracking including balances, expenses, and assets
- IBAN transfers and investment tracking
- Activity logging and audit trails
""")

vn.train(documentation="""
Key business terminology:
- Corps: Top-level military formation
- Div: Division under a corps
- Brigade: Formation under a division
- Unit: Smallest formation under a brigade
- Appointment (appt): Military role/position
- Formation: General term for military organizational unit
- IBAN: International Bank Account Number for transfers
""")

# Add question-SQL training pairs (MOST IMPORTANT for accuracy)
vn.train(
    question="How many active users are in the system?",
    sql="SELECT COUNT(*) FROM users WHERE is_active = 1"
)

vn.train(
    question="Show me all corps with their divisions",
    sql="""SELECT c.name as corps_name, d.name as division_name 
           FROM corps c 
           LEFT JOIN divs d ON c.id = d.corp_id 
           ORDER BY c.name, d.name"""
)

vn.train(
    question="What is the complete hierarchy for a specific user?",
    sql="""SELECT u.name as user_name, c.name as corps, d.name as division, 
                  b.name as brigade, un.name as unit
           FROM users u
           LEFT JOIN corps c ON u.corp_id = c.id
           LEFT JOIN divs d ON u.div_id = d.id  
           LEFT JOIN brigades b ON u.brigade_id = b.id
           LEFT JOIN units un ON u.unit_id = un.id
           WHERE u.id = ?"""
)

vn.train(
    question="How many users are in each corps?",
    sql="""SELECT c.name as corps_name, COUNT(u.id) as user_count
           FROM corps c
           LEFT JOIN users u ON c.id = u.corp_id
           GROUP BY c.id, c.name
           ORDER BY user_count DESC"""
)

vn.train(
    question="Show me all superusers and their formations",
    sql="""SELECT u.name, u.email, c.name as corps, d.name as division,
                  b.name as brigade, un.name as unit
           FROM users u
           LEFT JOIN corps c ON u.corp_id = c.id
           LEFT JOIN divs d ON u.div_id = d.id
           LEFT JOIN brigades b ON u.brigade_id = b.id  
           LEFT JOIN units un ON u.unit_id = un.id
           WHERE u.is_superuser = 1"""
)

vn.train(
    question="What are the different user roles in the system?",
    sql="SELECT DISTINCT role FROM users WHERE role IS NOT NULL ORDER BY role"
)

# Add more domain-specific question-SQL pairs
vn.train(
    question="Show me all inactive users",
    sql="SELECT name, email, role FROM users WHERE is_active = 0"
)

vn.train(
    question="How many brigades are in each division?",
    sql="""SELECT d.name as division_name, COUNT(b.id) as brigade_count
           FROM divs d
           LEFT JOIN brigades b ON d.id = b.div_id
           GROUP BY d.id, d.name
           ORDER BY brigade_count DESC"""
)

vn.train(
    question="Find users who haven't verified their email",
    sql="SELECT name, email, created_at FROM users WHERE email_verified_at IS NULL"
)

vn.train(
    question="Show the formation structure with counts",
    sql="""SELECT 'Corps' as level, COUNT(*) as count FROM corps
           UNION ALL
           SELECT 'Divisions' as level, COUNT(*) as count FROM divs
           UNION ALL  
           SELECT 'Brigades' as level, COUNT(*) as count FROM brigades
           UNION ALL
           SELECT 'Units' as level, COUNT(*) as count FROM units"""
)

# Add example SQL queries for common patterns
vn.train(sql="""SELECT u.name, u.role, c.name as corps_name
                FROM users u 
                JOIN corps c ON u.corp_id = c.id 
                WHERE u.is_active = 1""")

vn.train(sql="""SELECT c.name as corps, COUNT(d.id) as division_count
                FROM corps c
                LEFT JOIN divs d ON c.id = d.corp_id
                GROUP BY c.id, c.name""")

vn.train(sql="""SELECT b.name as brigade, COUNT(un.id) as unit_count
                FROM brigades b
                LEFT JOIN units un ON b.id = un.brigade_id
                GROUP BY b.id, b.name""")

# Use the training plan for comprehensive schema coverage
print("📊 Extracting database schema...")
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'cfms'")

# This will break up the information schema into bite-sized chunks that can be referenced by the LLM
plan = vn.get_training_plan_generic(df_information_schema)

print("="*100)
print("Training Plan Preview:")
print(plan)
print("="*100)

# Actually execute the training plan to get all tables
print("🚀 Training on complete database schema...")
vn.train(plan=plan)

print("✅ Training completed successfully!")
print("💡 You can now ask questions like:")
print("   - 'How many active users are there?'")
print("   - 'Show me the hierarchy of corps and divisions'") 
print("   - 'Who are the superusers in the system?'")
print("   - 'How many users are in each formation level?'")

# Test the trained model with a sample question
print("\n" + "="*60)
print("🧪 TESTING THE TRAINED MODEL")
print("="*60)

try:
    # Test question
    test_question = "How many active users are there in the system?"
    print(f"❓ Question: {test_question}")
    
    # Generate and display SQL
    sql_response = vn.generate_sql(test_question)
    print(f"🔍 Generated SQL: {sql_response}")
    
    # Execute the query (optional - uncomment to run)
    # result = vn.run_sql(sql_response)
    # print(f"📊 Result: {result}")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    print("💡 Try running: vn.ask('How many active users are there?')")

print("\n💡 To ask questions interactively, use:")
print("   vn.ask('Your question here')")
print("   vn.generate_sql('Your question here')  # SQL only")
print("   vn.run_sql('SELECT * FROM users LIMIT 5')  # Execute SQL directly")