# Standard library imports

# Standard library imports
import json
import os

# Third party imports
import cv2
import rasterio
from PIL import Image
from pyproj import Transformer
from tqdm import tqdm


def check_shapes(iwps):
    """
    Check the shapes of image files and store them in a dictionary.

    Parameters:
    iwps (list): A list of image files with paths.

    Returns:
    tuple: A tuple containing two elements:
        - shapes_dict (dict): A dictionary where the keys are the image shapes and the values are the counts.
        - shapes (list): A list of the shapes of the chip files in the same order as the input list.
    """
    # Create a dictionary to store the shape of the chip files
    shapes_dict = {}
    shapes = []

    for iwp in tqdm(iwps):
        # Read the chip file
        shape = cv2.imread(iwp, -1).shape

        # Store the shape in the dictionary
        if str(shape) in shapes_dict:
            shapes_dict[str(shape)] += 1
        else:
            shapes_dict[str(shape)] = 1

        shapes.append(shape)

    # Return the dictionary
    return shapes_dict, shapes


def get_geo_data(iwp):
    """
    Extracts geo data from a geotif.

    Parameters:
    iwp (str): The image file with path.

    Returns:
    dict: A dictionary containing the extracted geo data. The dictionary includes the following keys:
        - 'left': The left coordinate of the bounding box.
        - 'right': The right coordinate of the bounding box.
        - 'top': The top coordinate of the bounding box.
        - 'bottom': The bottom coordinate of the bounding box.
        - 'width': The width of the bounding box.
        - 'height': The height of the bounding box.
        - 'crs': The coordinate reference system (CRS) of the geotif.
    """
    # Open the image file in binary mode ('rb') for reading Exif data
    with rasterio.open(iwp) as src:

        if src.crs is None:
            raise ValueError(
                "No CRS found in the image file. Please check the file and try again."
            )
        elif src.bounds is None:
            raise ValueError(
                "No bounds found in the image file. Please check the file and try again."
            )

        # Convert the bounds to the expected format
        transformer = Transformer.from_crs(src.crs, "EPSG:4326")
        left, bottom = transformer.transform(src.bounds.left, src.bounds.bottom)
        right, top = transformer.transform(src.bounds.right, src.bounds.top)
        width = right - left
        height = top - bottom

        # Collect and return the extracted geo data
        results = {
            "left": left,
            "right": right,
            "top": top,
            "bottom": bottom,
            "width": width,
            "height": height,
            "crs": src.crs.to_string(),
        }

        return results


def check_and_clamp(values):
    """
    Check and clamp the values in a nested list.

    Parameters:
    values (list): A nested list of values to be checked and clamped.

    Returns:
    list: A nested list of clamped values.

    """
    # Initialize an empty list to store the clamped values
    clamped_values = []

    # Iterate over each sublist in the list
    for sublist in values:
        # Use a list comprehension to check and clamp each value in the sublist
        clamped_sublist = [
            [max(0, min(1, value)) for value in pair] for pair in sublist
        ]

        # Add the processed sublist to the clamped_values list
        clamped_values.append(clamped_sublist)

    return clamped_values


def flatten_list(nested_list):
    """
    Flattens a nested list into a single flat list.

    Parameters:
    nested_list (list): The nested list to be flattened.

    Returns:
    list: The flattened list.
    """
    flat_list = []

    # Iterate over all the elements in the given list
    for item in nested_list:
        # Check if the item is a list itself
        if isinstance(item, list):
            # If the item is a list, extend the flat list by adding elements of this item
            flat_list.extend(flatten_list(item))
        else:
            # If the item is not a list, append the item itself
            flat_list.append(item)
    return flat_list


def convert_coordinates(coordinates, geo_dict):
    """
    Convert coordinates from one coordinate system to another based on the provided geo_dict.

    Args:
        coordinates (list): A list of coordinate sets.
        geo_dict (dict): A dictionary containing information about the coordinate system.

    Returns:
        list: The converted coordinates.

    Raises:
        AssertionError: If the maximum coordinate value is greater than 1 or the minimum coordinate value is less than 0.
    """
    # Iterate over the outer list
    for i in range(len(coordinates)):
        # Iterate over each coordinate set in the inner list
        for j in range(len(coordinates[i])):
            if geo_dict["crs"] == "EPSG:4326":
                # Convert the coordinates for the EPSG:4326
                coordinates[i][j] = [
                    round(
                        (coordinates[i][j][0] - geo_dict["left"]) / geo_dict["width"], 6
                    ),
                    round(
                        (geo_dict["top"] - coordinates[i][j][1]) / geo_dict["height"], 6
                    ),
                ]
            else:
                # Convert the coordinates for not EPSG:4326
                coordinates[i][j] = [
                    round(
                        (coordinates[i][j][0] - geo_dict["bottom"])
                        / geo_dict["height"],
                        6,
                    ),
                    round(
                        (geo_dict["right"] - coordinates[i][j][1]) / geo_dict["width"],
                        6,
                    ),
                ]

    coordinates = check_and_clamp(coordinates)

    # Make sure that the coordinates are within the expected range
    assert (
        max(flatten_list(coordinates)) <= 1
    ), "The maximum coordinate value is greater than 1"
    assert (
        min(flatten_list(coordinates)) >= 0
    ), "The minimum coordinate value is less than 0"

    return coordinates






def write_yolo_file(iwp, folder, output_path, class_index=0):
    """
    Writes YOLO label file based on the given image with path and class index.

    Args:
        iwp (str): The image with path.
        output_path(path) : output path for the yolo label file
        class_index (int, optional): The class index for the YOLO label. Defaults to 0.

    Returns:
        None
    """

    # Get the GeoJSON filename with path from the chip filename with path
    lwp = iwp.replace(".tif", ".geojson").replace("chips", "labels")

    # Create the YOLO label filename with path from the chip filename with path
    ywp = os.path.join(output_path,'labels',folder, os.path.basename(iwp).replace(".tif", ".txt"))
    # Create the YOLO label folder if it does not exist
    os.makedirs(os.path.dirname(ywp), exist_ok=True)

    # Remove the YOLO label file if it already exists
    if os.path.exists(ywp):
        os.remove(ywp)

    # Fetch the chip's Exif data
    geo_dict = get_geo_data(iwp)

    # Open the GeoJSON file
    with open(lwp, "r") as file:
        data = json.load(file)

    # Initialize the polygon count
    polygon_count = 0

    # Navigate through the GeoJSON structure
    for feature in data["features"]:
        if feature["geometry"]["type"] == "Polygon":
            # Increment the polygon count
            polygon_count += 1

            # Get the coordinates of the polygon
            coordinates = feature["geometry"]["coordinates"]

            # Convert the coordinates
            new_coordinates = flatten_list(convert_coordinates(coordinates, geo_dict))
            new_coordinate_str = " ".join(map(str, flatten_list(new_coordinates)))

            # Write the converted coordinates to a file
            with open(ywp, "a+") as file:
                # Move the file pointer to the start of the file to check its contents.
                file.seek(0)  # Go to the beginning of the file
                first_character = file.read(
                    1
                )  # Read the first character to determine if the file is empty

                # If the first character does not exist, the file is empty
                if not first_character:
                    # Write the first string without a new line before it
                    file.write(f"{class_index} " + new_coordinate_str)

                else:
                    # The file is not empty, write the new string on a new line
                    file.write(f"\n{class_index} " + new_coordinate_str)

    if polygon_count == 0:
        # Open the file in write mode, which creates a new file if it doesn't exist
        with open(ywp, "w") as file:
            pass  # No need to write anything, just creating the file


def convert_tif_to_jpg(cwp, folder, output_path, quality_level=100):
    """
    Converts a TIFF image file to JPEG format.

    Parameters:
    cwp (str): The path to the TIFF image file.
    folder (str): The folder name (train, val, or test).
    output_path (str): The path to the output YOLO data folders.
    quality_level (int, optional): The quality level of the JPEG image (default is 100).

    Returns:
    str: The output path of the JPEG image file.
    """
    # Open the tif image file
    with Image.open(cwp) as img:
        # Convert the image to RGB and save it as a JPEG
        rgb_img = img.convert("RGB")

        # Define the output path with .jpg extension
        jwp = os.path.join(
            os.path.join(output_path, "images", folder),
            cwp.split("/")[-1].replace(".tif", ".jpg"),
        )

        # Create the output folder if it does not exist
        os.makedirs(os.path.dirname(jwp), exist_ok=True)

        # Save the image at quality level ql
        rgb_img.save(jwp, "JPEG", quality=quality_level)

        # Print the output path
        return f"Writing: {jwp}"
