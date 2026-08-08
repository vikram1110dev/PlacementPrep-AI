import sys
import os
from sqlalchemy.orm import Session

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import SessionLocal, engine, Base
import main # Triggers create_all
from app.models.dsa import DSAProblem, DSATestCase, DifficultyLevel

def seed_dsa_problems():
    db: Session = SessionLocal()
    try:
        # Check if already seeded
        if db.query(DSAProblem).count() > 0:
            print("DSA Problems already seeded.")
            return

        print("Seeding DSA Problems...")
        
        p1 = DSAProblem(
            title="Two Sum",
            slug="two-sum",
            description="<p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return <em>indices of the two numbers such that they add up to <code>target</code></em>.</p>",
            difficulty=DifficultyLevel.EASY,
            category="Arrays",
            starter_code="""class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        pass"""
        )
        db.add(p1)
        db.commit()
        db.refresh(p1)

        t1 = DSATestCase(
            problem_id=p1.id,
            input_data="[2,7,11,15]\n9",
            expected_output="[0, 1]",
            is_hidden=False
        )
        t2 = DSATestCase(
            problem_id=p1.id,
            input_data="[3,2,4]\n6",
            expected_output="[1, 2]",
            is_hidden=True
        )
        db.add_all([t1, t2])

        p2 = DSAProblem(
            title="Number of Islands",
            slug="number-of-islands",
            description="<p>Given an <code>m x n</code> 2D binary grid <code>grid</code> which represents a map of '1's (land) and '0's (water), return the number of islands.</p>",
            difficulty=DifficultyLevel.MEDIUM,
            category="Graphs",
            starter_code="""class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        pass"""
        )
        db.add(p2)
        db.commit()
        db.refresh(p2)
        
        t3 = DSATestCase(
            problem_id=p2.id,
            input_data='[["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]',
            expected_output="1",
            is_hidden=False
        )
        db.add(t3)

        db.commit()
        print("DSA Problems seeded successfully!")
    except Exception as e:
        print(f"Error seeding DSA problems: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_dsa_problems()
