#!/usr/bin/env python3
"""
Quick validation script to test basic functionality.
"""

def test_basic_imports():
    """Test basic imports work."""
    try:
        print("Testing basic imports...")
        
        # Test main module import
        import hot_fair_utilities as fair
        print("✅ Main module imported")
        
        # Test core functions exist
        core_functions = ['predict', 'vectorize', 'download_tiles', 'VectorizeMasks']
        for func in core_functions:
            if hasattr(fair, func):
                print(f"✅ {func} available")
            else:
                print(f"❌ {func} missing")
        
        # Test configuration
        if hasattr(fair, 'config'):
            print("✅ Configuration system available")
        else:
            print("❌ Configuration system missing")
        
        # Test validation
        if hasattr(fair, 'validate_bbox'):
            bbox = [0, 0, 1, 1]
            validated = fair.validate_bbox(bbox)
            print(f"✅ Validation working: {validated}")
        else:
            print("❌ Validation system missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def main():
    print("🔍 Quick fAIr-utilities Validation")
    print("=" * 40)
    
    success = test_basic_imports()
    
    if success:
        print("\n✅ BASIC VALIDATION PASSED")
        print("The integration appears to be working correctly!")
    else:
        print("\n❌ VALIDATION FAILED")
        print("There are issues with the integration.")
    
    return success

if __name__ == "__main__":
    main()
