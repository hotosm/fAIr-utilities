#!/usr/bin/env python3
"""
Structure Validation Script

This script validates the file structure and basic syntax of the 
fAIr-utilities integration without requiring full dependencies.
"""

import os
import sys
import ast
import json
from pathlib import Path


def validate_file_structure():
    """Validate the expected file structure exists."""
    print("🔍 Validating File Structure...")
    
    expected_files = [
        # Core module files
        "hot_fair_utilities/__init__.py",
        "hot_fair_utilities/config.py",
        "hot_fair_utilities/validation.py",
        "hot_fair_utilities/monitoring.py",
        
        # Data acquisition module
        "hot_fair_utilities/data_acquisition/__init__.py",
        "hot_fair_utilities/data_acquisition/tms_downloader.py",
        "hot_fair_utilities/data_acquisition/osm_downloader.py",
        
        # Vectorization module
        "hot_fair_utilities/vectorization/__init__.py",
        "hot_fair_utilities/vectorization/regularizer.py",
        "hot_fair_utilities/vectorization/orthogonalize.py",
        
        # Enhanced inference
        "hot_fair_utilities/inference/enhanced_predict.py",
        
        # Training module
        "hot_fair_utilities/training/__init__.py",
        
        # Test files
        "tests/__init__.py",
        "tests/test_data_acquisition.py",
        "tests/test_vectorization.py",
        
        # Configuration and documentation
        "pyproject.toml",
        "README.md",
        
        # Validation scripts
        "comprehensive_final_test.py",
        "production_validation.py",
        "WORKFLOW_TEST_SUITE.py",
    ]
    
    missing_files = []
    existing_files = []
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            existing_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ {file_path} - MISSING")
    
    print(f"\n📊 File Structure Summary:")
    print(f"  Existing files: {len(existing_files)}")
    print(f"  Missing files: {len(missing_files)}")
    print(f"  Completion: {len(existing_files)/(len(existing_files)+len(missing_files))*100:.1f}%")
    
    return len(missing_files) == 0


def validate_python_syntax():
    """Validate Python syntax of key files."""
    print("\n🔍 Validating Python Syntax...")
    
    python_files = [
        "hot_fair_utilities/__init__.py",
        "hot_fair_utilities/config.py",
        "hot_fair_utilities/validation.py",
        "hot_fair_utilities/monitoring.py",
        "hot_fair_utilities/data_acquisition/__init__.py",
        "hot_fair_utilities/data_acquisition/tms_downloader.py",
        "hot_fair_utilities/data_acquisition/osm_downloader.py",
        "hot_fair_utilities/vectorization/__init__.py",
        "hot_fair_utilities/vectorization/regularizer.py",
        "hot_fair_utilities/vectorization/orthogonalize.py",
        "hot_fair_utilities/inference/enhanced_predict.py",
        "comprehensive_final_test.py",
        "production_validation.py",
    ]
    
    syntax_errors = []
    valid_files = []
    
    for file_path in python_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse the AST to check syntax
                ast.parse(content)
                valid_files.append(file_path)
                print(f"✅ {file_path} - Valid syntax")
                
            except SyntaxError as e:
                syntax_errors.append((file_path, str(e)))
                print(f"❌ {file_path} - Syntax error: {e}")
            except Exception as e:
                syntax_errors.append((file_path, str(e)))
                print(f"⚠️  {file_path} - Error reading: {e}")
        else:
            print(f"⚠️  {file_path} - File not found")
    
    print(f"\n📊 Syntax Validation Summary:")
    print(f"  Valid files: {len(valid_files)}")
    print(f"  Syntax errors: {len(syntax_errors)}")
    
    return len(syntax_errors) == 0


def validate_pyproject_toml():
    """Validate pyproject.toml structure."""
    print("\n🔍 Validating pyproject.toml...")
    
    if not os.path.exists("pyproject.toml"):
        print("❌ pyproject.toml not found")
        return False
    
    try:
        # Try to parse as TOML (basic validation)
        with open("pyproject.toml", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = [
            "[build-system]",
            "[project]",
            "[project.optional-dependencies]",
        ]
        
        missing_sections = []
        for section in required_sections:
            if section in content:
                print(f"✅ {section} section found")
            else:
                missing_sections.append(section)
                print(f"❌ {section} section missing")
        
        # Check for requires-python in correct location
        if 'requires-python = ">=3.7"' in content:
            # Check it's not in optional-dependencies section
            lines = content.split('\n')
            in_optional_deps = False
            requires_python_location = "unknown"
            
            for i, line in enumerate(lines):
                if '[project.optional-dependencies]' in line:
                    in_optional_deps = True
                elif line.startswith('[') and 'optional-dependencies' not in line:
                    in_optional_deps = False
                elif 'requires-python' in line:
                    if in_optional_deps:
                        requires_python_location = "optional-dependencies (WRONG)"
                    else:
                        requires_python_location = "project section (CORRECT)"
                    break
            
            print(f"✅ requires-python found in {requires_python_location}")
            if "WRONG" in requires_python_location:
                print("❌ requires-python in wrong section!")
                return False
        else:
            print("❌ requires-python not found")
            return False
        
        print("✅ pyproject.toml structure valid")
        return len(missing_sections) == 0
        
    except Exception as e:
        print(f"❌ Error validating pyproject.toml: {e}")
        return False


def validate_imports_structure():
    """Validate import structure in __init__.py files."""
    print("\n🔍 Validating Import Structure...")
    
    init_files = [
        "hot_fair_utilities/__init__.py",
        "hot_fair_utilities/data_acquisition/__init__.py",
        "hot_fair_utilities/vectorization/__init__.py",
        "hot_fair_utilities/training/__init__.py",
        "tests/__init__.py",
    ]
    
    import_errors = []
    valid_imports = []
    
    for file_path in init_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for basic import patterns
                if file_path == "hot_fair_utilities/__init__.py":
                    expected_imports = [
                        "from .config import",
                        "from .validation import",
                        "from .monitoring import",
                        "from .data_acquisition import",
                        "from .vectorization import",
                    ]
                    
                    for expected in expected_imports:
                        if expected in content:
                            print(f"✅ {file_path} - {expected}")
                        else:
                            print(f"⚠️  {file_path} - Missing: {expected}")
                
                valid_imports.append(file_path)
                
            except Exception as e:
                import_errors.append((file_path, str(e)))
                print(f"❌ {file_path} - Error: {e}")
        else:
            print(f"⚠️  {file_path} - File not found")
    
    print(f"\n📊 Import Structure Summary:")
    print(f"  Valid import files: {len(valid_imports)}")
    print(f"  Import errors: {len(import_errors)}")
    
    return len(import_errors) == 0


def validate_documentation():
    """Validate documentation files exist."""
    print("\n🔍 Validating Documentation...")
    
    doc_files = [
        "README.md",
        "INTEGRATION_GUIDE.md",
        "FINAL_TEST_RESULTS.md",
        "INTEGRATION_COMPLETION_SUMMARY.md",
        "WORKFLOW_VALIDATION_CHECKLIST.md",
        "PYPROJECT_FIX_SUMMARY.md",
    ]
    
    existing_docs = []
    missing_docs = []
    
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            existing_docs.append(doc_file)
            print(f"✅ {doc_file}")
        else:
            missing_docs.append(doc_file)
            print(f"❌ {doc_file} - MISSING")
    
    print(f"\n📊 Documentation Summary:")
    print(f"  Existing docs: {len(existing_docs)}")
    print(f"  Missing docs: {len(missing_docs)}")
    print(f"  Completion: {len(existing_docs)/(len(existing_docs)+len(missing_docs))*100:.1f}%")
    
    return len(missing_docs) <= 2  # Allow a few missing docs


def main():
    """Run all structure validations."""
    print("🔍 fAIr-utilities Structure Validation")
    print("=" * 50)
    
    validations = [
        ("File Structure", validate_file_structure),
        ("Python Syntax", validate_python_syntax),
        ("pyproject.toml", validate_pyproject_toml),
        ("Import Structure", validate_imports_structure),
        ("Documentation", validate_documentation),
    ]
    
    passed = 0
    total = len(validations)
    
    for name, validation_func in validations:
        try:
            if validation_func():
                passed += 1
                print(f"\n✅ {name}: PASSED")
            else:
                print(f"\n❌ {name}: FAILED")
        except Exception as e:
            print(f"\n💥 {name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("📊 STRUCTURE VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Validations passed: {passed}/{total}")
    print(f"Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL VALIDATIONS PASSED!")
        print("✅ Structure is ready for functional testing")
        status = "READY"
    elif passed >= total * 0.8:
        print("\n⚠️  MOSTLY VALID - Minor issues found")
        print("✅ Structure is mostly correct")
        status = "MOSTLY_READY"
    else:
        print("\n❌ VALIDATION FAILED")
        print("❌ Significant structural issues found")
        status = "NOT_READY"
    
    print(f"\nNext steps:")
    if status == "READY":
        print("1. Run functional tests: python WORKFLOW_TEST_SUITE.py")
        print("2. Run production validation: python production_validation.py")
    else:
        print("1. Fix structural issues identified above")
        print("2. Re-run structure validation")
    
    return status == "READY"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
