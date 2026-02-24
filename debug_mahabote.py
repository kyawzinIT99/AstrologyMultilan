
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.getcwd())

from mahabote_engine import MahaboteEngine

def test_su_mon_myint_oo():
    print("Testing Mahabote Calculation for Dr.Tarot (1978-10-10)...")
    engine = MahaboteEngine()
    reading = engine.calculate("Dr.Tarot", 1978, 10, 10)
    
    print(f"Birth: {reading.birth_date.date()} (MY {reading.myanmar_year}, Rem {reading.year_remainder})")
    print(f"House: {reading.house['name_en']} (ID: {reading.house['id']})")
    
    # Su Mon (Rem 3, Tuesday=3): (3-3)%7 = 0 (Binga)
    assert reading.year_remainder == 3
    assert reading.house['id'] == "binga"
    print("✅ Su Mon Birth House Correct (Binga)!")

def test_1957_case():
    print("\nTesting Mahabote Calculation for 1957-02-13...")
    engine = MahaboteEngine()
    reading = engine.calculate("User Test 1957", 1957, 2, 13)
    
    print(f"Birth: {reading.birth_date.date()} (MY {reading.myanmar_year}, Rem {reading.year_remainder})")
    print(f"House: {reading.house['name_en']} (ID: {reading.house['id']})")
    
    # 1957-02-13 (Rem 2, Wednesday=4): (4-2)%7 = 2 (Thike)
    assert reading.year_remainder == 2
    assert reading.house['id'] == "thike"
    print("✅ 1957 Birth House Correct (Thike)!")

if __name__ == "__main__":
    try:
        test_su_mon_myint_oo()
        test_1957_case()
        print("\n✅ All logic checks passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
