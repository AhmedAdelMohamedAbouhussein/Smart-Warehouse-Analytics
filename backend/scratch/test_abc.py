import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from algorithms.bin_packing import abc_classify

def test_abc():
    cases = [
        # Case 1: Large list (100 products)
        {"name": "Large List (100)", "products": [{"id": i, "name": f"P{i}", "demand_frequency": 100-i} for i in range(100)]},
        # Case 2: Small list (10 products)
        {"name": "Small List (10)", "products": [{"id": i, "name": f"P{i}", "demand_frequency": 10-i} for i in range(10)]},
        # Case 3: Very small list (3 products)
        {"name": "Minimal List (3)", "products": [{"id": i, "name": f"P{i}", "demand_frequency": 3-i} for i in range(3)]},
        # Case 4: 2 products
        {"name": "Tiny List (2)", "products": [{"id": i, "name": f"P{i}", "demand_frequency": 2-i} for i in range(2)]},
        # Case 5: 1 product
        {"name": "Single Item", "products": [{"id": 1, "name": "P1", "demand_frequency": 10}]},
    ]

    for case in cases:
        print(f"\n--- Testing: {case['name']} (n={len(case['products'])}) ---")
        result = abc_classify(case['products'])
        
        a_len = len(result['A'])
        b_len = len(result['B'])
        c_len = len(result['C'])
        total = a_len + b_len + c_len
        
        print(f"Counts -> A: {a_len}, B: {b_len}, C: {c_len} (Total: {total})")
        
        # Verify velocity_class field exists
        all_have_class = all("velocity_class" in p for p in result["classification_details"])
        print(f"Velocity class field present: {all_have_class}")
        
        # Sample output
        if total > 0:
            print(f"First product class: {result['classification_details'][0]['velocity_class']}")
            if total > a_len:
                 print(f"Product after A class: {result['classification_details'][a_len]['velocity_class']}")

if __name__ == "__main__":
    test_abc()
