"""
Comprehensive example demonstrating the integrated fAIr-utilities workflow.

This example shows how to use the newly integrated functionality from
geoml-toolkits and fairpredictor for a complete end-to-end workflow.
"""

import asyncio
import os
from pathlib import Path

# Import the enhanced fAIr-utilities
import hot_fair_utilities as fair


async def example_complete_workflow():
    """
    Complete workflow example: from data acquisition to final predictions.
    """
    print("=== fAIr-utilities Integrated Workflow Example ===\n")
    
    # Define area of interest (example: small area in Kathmandu, Nepal)
    bbox = [85.514668, 27.628367, 85.528875, 27.638514]
    zoom_level = 18
    
    # Working directory
    work_dir = "example_workflow"
    os.makedirs(work_dir, exist_ok=True)
    
    print("1. Data Acquisition")
    print("=" * 50)
    
    # Download aerial imagery tiles
    print("Downloading aerial imagery tiles...")
    tms_url = fair.DEFAULT_OAM_TMS_MOSAIC
    
    image_dir = await fair.download_tiles(
        tms=tms_url,
        zoom=zoom_level,
        bbox=bbox,
        out=os.path.join(work_dir, "imagery"),
        georeference=True,
        dump=True,
        crs="3857"
    )
    print(f"✓ Images downloaded to: {image_dir}")
    
    # Download OSM building data for comparison
    print("\nDownloading OSM building data...")
    osm_data = await fair.download_osm_data(
        bbox=bbox,
        feature_type="building",
        dump=True,
        out=os.path.join(work_dir, "osm_data"),
        crs="4326"
    )
    print(f"✓ OSM data downloaded to: {osm_data}")
    
    print("\n2. Model Prediction")
    print("=" * 50)
    
    # Run end-to-end prediction with tiles
    print("Running end-to-end prediction...")
    predictions = await fair.predict_with_tiles(
        model_path=fair.DEFAULT_RAMP_MODEL,
        zoom_level=zoom_level,
        bbox=bbox,
        tms_url=tms_url,
        base_path=work_dir,
        confidence=0.5,
        area_threshold=5.0,  # 5 sq meters minimum
        tolerance=0.3,       # 30cm tolerance
        orthogonalize=True,
        vectorization_algorithm="rasterio",
        remove_metadata=False  # Keep files for inspection
    )
    
    print(f"✓ Prediction completed! Found {len(predictions['features'])} buildings")
    
    # Save predictions
    prediction_file = os.path.join(work_dir, "predictions.geojson")
    import json
    with open(prediction_file, 'w') as f:
        json.dump(predictions, f, indent=2)
    print(f"✓ Predictions saved to: {prediction_file}")
    
    print("\n3. Advanced Vectorization Example")
    print("=" * 50)
    
    # Demonstrate advanced vectorization with different algorithms
    print("Testing different vectorization algorithms...")
    
    # Find a prediction mask to work with
    mask_files = list(Path(work_dir).rglob("*.tif"))
    if mask_files:
        mask_file = str(mask_files[0])
        print(f"Using mask file: {mask_file}")
        
        # Test Potrace algorithm (if available)
        try:
            potrace_converter = fair.VectorizeMasks(
                simplify_tolerance=0.2,
                min_area=3.0,
                orthogonalize=True,
                algorithm="potrace"
            )
            potrace_output = os.path.join(work_dir, "potrace_result.geojson")
            potrace_gdf = potrace_converter.convert(mask_file, potrace_output)
            print(f"✓ Potrace vectorization: {len(potrace_gdf)} features")
        except Exception as e:
            print(f"⚠ Potrace not available: {e}")
        
        # Test rasterio algorithm
        rasterio_converter = fair.VectorizeMasks(
            simplify_tolerance=0.2,
            min_area=3.0,
            orthogonalize=True,
            algorithm="rasterio"
        )
        rasterio_output = os.path.join(work_dir, "rasterio_result.geojson")
        rasterio_gdf = rasterio_converter.convert(mask_file, rasterio_output)
        print(f"✓ Rasterio vectorization: {len(rasterio_gdf)} features")
    
    print("\n4. Summary")
    print("=" * 50)
    print("Workflow completed successfully!")
    print(f"Working directory: {os.path.abspath(work_dir)}")
    print("\nGenerated files:")
    for file_path in Path(work_dir).rglob("*"):
        if file_path.is_file():
            print(f"  - {file_path}")


async def example_basic_usage():
    """
    Basic usage examples for individual components.
    """
    print("\n=== Basic Usage Examples ===\n")
    
    bbox = [85.514668, 27.628367, 85.528875, 27.638514]
    
    print("1. Download tiles only")
    print("-" * 30)
    tiles_dir = await fair.download_tiles(
        tms="https://tiles.openaerialmap.org/6501a65c0906de000167e64d/0/6501a65c0906de000167e64e/{z}/{x}/{y}",
        zoom=18,
        bbox=bbox,
        out="basic_example/tiles",
        georeference=True
    )
    print(f"✓ Tiles downloaded to: {tiles_dir}")
    
    print("\n2. Download OSM data only")
    print("-" * 30)
    osm_result = await fair.download_osm_data(
        bbox=bbox,
        feature_type="building",
        dump=True,
        out="basic_example/osm"
    )
    print(f"✓ OSM data: {osm_result}")
    
    print("\n3. Vectorization only")
    print("-" * 30)
    # This would work if you have a mask file
    # converter = fair.VectorizeMasks()
    # result = converter.convert("input_mask.tif", "output.geojson")
    print("✓ Use VectorizeMasks class for advanced vectorization")


def example_model_integration():
    """
    Example showing how to easily integrate new models.
    """
    print("\n=== Model Integration Example ===\n")
    
    print("Available default models:")
    print(f"- RAMP Model: {fair.DEFAULT_RAMP_MODEL}")
    print(f"- YOLO v1 Model: {fair.DEFAULT_YOLO_MODEL_V1}")
    print(f"- YOLO v2 Model: {fair.DEFAULT_YOLO_MODEL_V2}")
    print(f"- Default TMS: {fair.DEFAULT_OAM_TMS_MOSAIC}")
    
    print("\nTo integrate a new model:")
    print("1. Add model URL or path")
    print("2. Use predict_with_tiles() with your model")
    print("3. The framework handles the rest!")
    
    # Example of using a custom model
    custom_model_example = """
    # Example with custom model
    predictions = await fair.predict_with_tiles(
        model_path="https://your-domain.com/custom-model.pt",
        zoom_level=18,
        bbox=[xmin, ymin, xmax, ymax],
        confidence=0.6,
        area_threshold=10.0,
        vectorization_algorithm="potrace"
    )
    """
    print(f"\nCustom model example:\n{custom_model_example}")


async def main():
    """
    Main function to run all examples.
    """
    print("🚀 Starting fAIr-utilities Integration Examples")
    print("=" * 60)
    
    try:
        # Run the complete workflow
        await example_complete_workflow()
        
        # Show basic usage
        await example_basic_usage()
        
        # Show model integration
        example_model_integration()
        
        print("\n🎉 All examples completed successfully!")
        print("\nNext steps:")
        print("- Explore the generated files")
        print("- Try with your own areas of interest")
        print("- Integrate your own models")
        print("- Experiment with different parameters")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure you have all dependencies installed:")
        print("pip install hot-fair-utilities[dev]")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
