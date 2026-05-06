#!/usr/bin/env python3
"""
Script to check if the new document fields exist in the cars table.
"""
import asyncio
import sys
from sqlalchemy import text
from app.db.session import get_db_session

async def check_database_columns():
    """Check if the new columns exist in the cars table."""
    print("🔍 Checking database columns for cars table...")
    
    try:
        async with get_db_session() as session:
            # Get table info
            result = await session.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'cars' 
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            
            if not columns:
                print("❌ Could not retrieve table information")
                return False
            
            print("\n📋 Current columns in cars table:")
            print("-" * 50)
            
            document_columns = []
            for column in columns:
                col_name, data_type, is_nullable = column
                print(f"  {col_name:<25} | {data_type:<15} | {is_nullable}")
                
                # Check for our new document columns
                if col_name in ['vignette_url', 'controle_technique_url', 'assurance_paper_url']:
                    document_columns.append(col_name)
            
            print("-" * 50)
            
            # Check if all expected columns exist
            expected_columns = ['vignette_url', 'controle_technique_url', 'assurance_paper_url']
            missing_columns = [col for col in expected_columns if col not in document_columns]
            
            if missing_columns:
                print(f"\n❌ Missing columns: {', '.join(missing_columns)}")
                print("\n💡 To add missing columns, run:")
                for col in missing_columns:
                    if col == 'vignette_url':
                        print("   ALTER TABLE cars ADD COLUMN vignette_url TEXT;")
                    elif col == 'controle_technique_url':
                        print("   ALTER TABLE cars ADD COLUMN controle_technique_url TEXT;")
                    elif col == 'assurance_paper_url':
                        print("   ALTER TABLE cars ADD COLUMN assurance_paper_url TEXT;")
                return False
            else:
                print(f"\n✅ All document columns found: {', '.join(document_columns)}")
                return True
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

async def check_table_exists():
    """Check if the cars table exists."""
    try:
        async with get_db_session() as session:
            result = await session.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'cars'
            """))
            
            table_exists = result.scalar() > 0
            
            if table_exists:
                print("✅ Cars table exists")
                return True
            else:
                print("❌ Cars table does not exist")
                return False
                
    except Exception as e:
        print(f"❌ Error checking table existence: {e}")
        return False

async def main():
    print("🚀 SmartPlate Database Column Checker")
    print("=" * 50)
    
    # Check if table exists first
    if not await check_table_exists():
        print("\n💡 To create the table, start the backend server")
        print("   The create_tables() function will create the table with all columns")
        sys.exit(1)
    
    # Check columns
    success = await check_database_columns()
    
    if success:
        print("\n🎉 Database is ready for document uploads!")
    else:
        print("\n⚠️  Database needs manual column additions")

if __name__ == "__main__":
    asyncio.run(main())
