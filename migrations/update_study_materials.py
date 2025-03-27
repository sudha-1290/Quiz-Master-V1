from app import db
from app.models.study_material import StudyMaterial
from datetime import datetime

def update_study_materials_table():
    # Create the updated_at column if it doesn't exist
    with db.engine.connect() as conn:
        try:
            conn.execute(db.text("""
                ALTER TABLE study_material 
                ADD COLUMN updated_at DATETIME
            """))
            conn.commit()
        except Exception as e:
            print(f"Column might already exist or other error: {e}")
            
    # Update existing records to have an updated_at value
    try:
        StudyMaterial.query.update({StudyMaterial.updated_at: datetime.utcnow()})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating records: {e}")

if __name__ == '__main__':
    update_study_materials_table() 