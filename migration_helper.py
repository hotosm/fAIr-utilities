"""
Migration helper script for transitioning to the new integrated fAIr-utilities.

This script helps users migrate from the old workflow to the new integrated
workflow, providing side-by-side comparisons and automated migration suggestions.
"""

import ast
import os
import re
from typing import Dict, List, Tuple


class CodeMigrationHelper:
    """
    Helper class to analyze and suggest migrations for fAIr-utilities code.
    """
    
    def __init__(self):
        self.old_patterns = {
            # Old import patterns
            'old_imports': [
                r'from hot_fair_utilities import.*',
                r'import hot_fair_utilities.*',
                r'from hot_fair_utilities\..*',
            ],
            
            # Old function calls
            'old_functions': [
                r'bbox2tiles\(',
                r'tms2img\(',
                r'predict\(',
                r'polygonize\(',
                r'vectorize\(',
            ],
            
            # Old workflow patterns
            'old_workflows': [
                r'preprocess\(.*\)',
                r'predict\(.*\)',
                r'postprocess\(.*\)',
            ]
        }
        
        self.migration_suggestions = {
            'bbox2tiles': 'Use download_tiles() with bbox parameter',
            'tms2img': 'Use download_tiles() for tile downloading',
            'predict': 'Use predict_with_tiles() for end-to-end prediction',
            'polygonize': 'Use VectorizeMasks for advanced vectorization',
            'vectorize': 'Use VectorizeMasks for advanced vectorization',
        }

    def analyze_file(self, file_path: str) -> Dict:
        """
        Analyze a Python file for migration opportunities.
        
        Args:
            file_path: Path to the Python file to analyze
            
        Returns:
            Dictionary with analysis results and suggestions
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'file_path': file_path,
            'old_imports': [],
            'old_functions': [],
            'migration_suggestions': [],
            'modernized_code': None
        }
        
        # Find old imports
        for pattern in self.old_patterns['old_imports']:
            matches = re.findall(pattern, content, re.MULTILINE)
            analysis['old_imports'].extend(matches)
        
        # Find old function calls
        for pattern in self.old_patterns['old_functions']:
            matches = re.findall(pattern, content)
            analysis['old_functions'].extend(matches)
        
        # Generate suggestions
        for func_call in analysis['old_functions']:
            func_name = func_call.replace('(', '')
            if func_name in self.migration_suggestions:
                analysis['migration_suggestions'].append({
                    'old': func_call,
                    'suggestion': self.migration_suggestions[func_name]
                })
        
        # Generate modernized code
        analysis['modernized_code'] = self.generate_modern_code(content)
        
        return analysis

    def generate_modern_code(self, old_code: str) -> str:
        """
        Generate modernized code suggestions.
        
        Args:
            old_code: Original code content
            
        Returns:
            Modernized code with suggestions
        """
        modern_code = old_code
        
        # Replace old imports
        modern_code = re.sub(
            r'from hot_fair_utilities import.*',
            'import hot_fair_utilities as fair',
            modern_code
        )
        
        # Add async import if needed
        if 'predict(' in old_code or 'bbox2tiles(' in old_code:
            if 'import asyncio' not in modern_code:
                modern_code = 'import asyncio\n' + modern_code
        
        # Replace common patterns
        replacements = {
            r'bbox2tiles\((.*?)\)': r'await fair.download_tiles(bbox=\1, zoom=18)',
            r'predict\((.*?)\)': r'await fair.predict_with_tiles(model_path=\1)',
            r'polygonize\((.*?)\)': r'fair.VectorizeMasks().convert(\1)',
        }
        
        for old_pattern, new_pattern in replacements.items():
            modern_code = re.sub(old_pattern, new_pattern, modern_code)
        
        return modern_code

    def generate_migration_report(self, file_paths: List[str]) -> str:
        """
        Generate a comprehensive migration report for multiple files.
        
        Args:
            file_paths: List of Python files to analyze
            
        Returns:
            Formatted migration report
        """
        report = []
        report.append("=" * 60)
        report.append("fAIr-utilities Migration Report")
        report.append("=" * 60)
        report.append("")
        
        total_files = len(file_paths)
        files_needing_migration = 0
        
        for file_path in file_paths:
            analysis = self.analyze_file(file_path)
            
            if analysis.get('error'):
                report.append(f"❌ Error analyzing {file_path}: {analysis['error']}")
                continue
            
            if analysis['old_imports'] or analysis['old_functions']:
                files_needing_migration += 1
                report.append(f"📁 File: {file_path}")
                report.append("-" * 40)
                
                if analysis['old_imports']:
                    report.append("🔍 Old imports found:")
                    for imp in analysis['old_imports']:
                        report.append(f"  - {imp}")
                    report.append("")
                
                if analysis['old_functions']:
                    report.append("🔍 Old function calls found:")
                    for func in analysis['old_functions']:
                        report.append(f"  - {func}")
                    report.append("")
                
                if analysis['migration_suggestions']:
                    report.append("💡 Migration suggestions:")
                    for suggestion in analysis['migration_suggestions']:
                        report.append(f"  - {suggestion['old']} → {suggestion['suggestion']}")
                    report.append("")
                
                report.append("")
        
        # Summary
        report.append("📊 Summary")
        report.append("-" * 20)
        report.append(f"Total files analyzed: {total_files}")
        report.append(f"Files needing migration: {files_needing_migration}")
        report.append(f"Migration coverage: {((total_files - files_needing_migration) / total_files * 100):.1f}%")
        report.append("")
        
        # Migration guide
        report.append("📚 Quick Migration Guide")
        report.append("-" * 30)
        report.append("1. Replace imports:")
        report.append("   OLD: from hot_fair_utilities import predict, bbox2tiles")
        report.append("   NEW: import hot_fair_utilities as fair")
        report.append("")
        report.append("2. Use async/await for new functions:")
        report.append("   OLD: tiles = bbox2tiles(bbox, zoom)")
        report.append("   NEW: tiles = await fair.download_tiles(bbox=bbox, zoom=zoom)")
        report.append("")
        report.append("3. Use integrated prediction:")
        report.append("   OLD: predict(model, input_path, output_path)")
        report.append("   NEW: await fair.predict_with_tiles(model_path=model, bbox=bbox)")
        report.append("")
        report.append("4. Use advanced vectorization:")
        report.append("   OLD: polygonize(mask_path, output_path)")
        report.append("   NEW: fair.VectorizeMasks().convert(mask_path, output_path)")
        report.append("")
        
        return "\n".join(report)


def create_example_migration():
    """
    Create example files showing before/after migration.
    """
    # Old style example
    old_example = '''
# Old fAIr-utilities workflow
from hot_fair_utilities import bbox2tiles, predict, polygonize
import os

def old_workflow():
    # Step 1: Get tiles
    bbox = [85.514668, 27.628367, 85.528875, 27.638514]
    tiles = bbox2tiles(bbox, zoom=18)
    
    # Step 2: Download images (manual process)
    # ... manual tile downloading code ...
    
    # Step 3: Run prediction
    predict(
        checkpoint_path="model.pt",
        input_path="images/",
        prediction_path="predictions/",
        confidence=0.5
    )
    
    # Step 4: Vectorize results
    polygonize(
        prediction_path="predictions/",
        output_path="results.geojson",
        confidence=0.5
    )

if __name__ == "__main__":
    old_workflow()
'''
    
    # New style example
    new_example = '''
# New integrated fAIr-utilities workflow
import asyncio
import hot_fair_utilities as fair

async def new_workflow():
    # Complete end-to-end workflow in one function!
    bbox = [85.514668, 27.628367, 85.528875, 27.638514]
    
    predictions = await fair.predict_with_tiles(
        model_path=fair.DEFAULT_RAMP_MODEL,  # or your custom model
        zoom_level=18,
        bbox=bbox,
        confidence=0.5,
        area_threshold=5.0,
        orthogonalize=True,
        vectorization_algorithm="rasterio"
    )
    
    print(f"Found {len(predictions['features'])} buildings!")
    return predictions

# Alternative: Step-by-step workflow
async def step_by_step_workflow():
    bbox = [85.514668, 27.628367, 85.528875, 27.638514]
    
    # Step 1: Download tiles with georeferencing
    tiles_dir = await fair.download_tiles(
        tms=fair.DEFAULT_OAM_TMS_MOSAIC,
        zoom=18,
        bbox=bbox,
        georeference=True
    )
    
    # Step 2: Run prediction on downloaded tiles
    prediction_dir = fair.run_prediction(
        model_path=fair.DEFAULT_RAMP_MODEL,
        input_path=tiles_dir,
        prediction_path="predictions/"
    )
    
    # Step 3: Advanced vectorization
    converter = fair.VectorizeMasks(
        simplify_tolerance=0.2,
        min_area=5.0,
        orthogonalize=True
    )
    gdf = converter.convert("prediction_mask.tif", "results.geojson")
    
    return gdf

if __name__ == "__main__":
    # Run the new workflow
    predictions = asyncio.run(new_workflow())
'''
    
    # Save examples
    os.makedirs("migration_examples", exist_ok=True)
    
    with open("migration_examples/old_workflow.py", "w") as f:
        f.write(old_example)
    
    with open("migration_examples/new_workflow.py", "w") as f:
        f.write(new_example)
    
    print("✅ Migration examples created in migration_examples/")


def main():
    """
    Main function to run migration analysis.
    """
    print("🔄 fAIr-utilities Migration Helper")
    print("=" * 40)
    
    # Create migration examples
    create_example_migration()
    
    # Find Python files in current directory
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip certain directories
        if any(skip in root for skip in ['.git', '__pycache__', 'venv', 'env']):
            continue
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    if not python_files:
        print("No Python files found for analysis.")
        return
    
    # Analyze files
    helper = CodeMigrationHelper()
    report = helper.generate_migration_report(python_files[:10])  # Limit to first 10 files
    
    # Save report
    with open("migration_report.txt", "w") as f:
        f.write(report)
    
    print(report)
    print(f"\n📄 Full report saved to: migration_report.txt")
    print("📁 Example files created in: migration_examples/")


if __name__ == "__main__":
    main()
