## Sample Benchmark Datasets 

| id  | id_train | ds_size | Urban Region       | Country      | Continent      | Urban Type     | Density | Roof Type  | Download |
|---- |---------|--------|------------------|-------------|--------------|-------------|---------|----------|-----------|
| 1   | 364     | 399    | Kakuma           | Kenya       | Africa       | Refugee Camp | Sparse  | Metal    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_364/preprocessed.zip/) |
| 2   | 370     | 168    | Denver           | USA         | America North | Peri-Urban   | Grid    | Shingles | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_370/preprocessed.zip/) |
| 3   | 372     | 420    | Montevideo       | Uruguay     | America South | Urban        | Grid    | Cement   | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_372/preprocessed.zip/) |
| 4   | 373     | 399    | Montevideo Dense | Uruguay     | America South | Urban        | Dense   | Cement   | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_373/preprocessed.zip/) |
| 5   | 391     | 231    | Kutupalong       | Bangladesh  | Asia         | Refugee Camp | Dense   | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_391/preprocessed.zip/) |
| 6   | 394     | 504    | Gornja Rijeka    | Croatia     | Europe       | Rural        | Sparse  | Shingles | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_394/preprocessed.zip/) |
| 7   | 397     | 756    | Melbourne        | Australia   | Oceania      | Urban        | Grid    | Cement   | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_397/preprocessed.zip/) |
| 8   | 398     | 152    | Pemba            | Tanzania    | Africa       | Rural        | Sparse  | Metal    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_398/preprocessed.zip/) |
| 9   | 399     | 294    | Christchurch     | New Zealand | Oceania      | Peri-Urban   | Sparse  | Shingles | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_399/preprocessed.zip/) |
| 10  | 456     | 147    | Pergamino        | Argentina   | America South | Peri-Urban   | Grid    | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_456/preprocessed.zip/) |
| 11  | 459     | 105    | Silvania         | Brazil      | America South | Rural        | Sparse  | Shingles | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_459/preprocessed.zip/) |
| 12  | 462     | 147    | Desa Kulaba     | Indonesia   | Asia         | Rural        | Sparse  | Metal    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_462/preprocessed.zip/) |
| 13  | 463     | 168    | Roseau          | Dominica    | America Central | Peri-Urban   | Sparse  | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_463/preprocessed.zip/) |
| 14  | 485     | 147    | Pallabi Dhaka   | Bangladesh  | Asia         | Urban        | Dense   | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_485/preprocessed.zip/) |
| 15  | 488     | 168    | Dhaka           | Bangladesh  | Asia         | Urban        | Dense   | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_488/preprocessed.zip/) |
| 16  | 489     | 147    | Ggaba           | Uganda      | Africa       | Peri-Urban   | Dense   | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_489/preprocessed.zip/) |
| 17  | 529     | 546    | Inagi           | Japan       | Asia         | Peri-Urban   | Sparse  | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_529/preprocessed.zip/) |
| 18  | 508     | 226    | Tchiniambi      | DRC         | Africa       | Peri-Urban   | Dense   | Metal    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_508/preprocessed.zip/) |
| 19  | 539     | 672    | Staraya Russa   | Russia      | Europe       | Rural        | Sparse  | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_539/preprocessed.zip/) |
| 20  | 530     | 189    | Banyuwangi      | Indonesia   | Asia         | Urban        | Dense   | Shingles | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_530/preprocessed.zip/) |
| 21  | 526     | 672    | Dzaleka         | Malawi      | Africa       | Refugee Camp | Dense   | Metal    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_526/preprocessed.zip/) |
| 22  | 523     | 252    | Bogota          | Colombia    | America South | Urban        | Grid    | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_523/preprocessed.zip/) |
| 23  | 524     | 315    | Soudure         | Niger       | Africa       | Rural        | Dense   | Mixed    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_524/preprocessed.zip/) |
| 24  | 525     | 420    | Quincy          | USA         | America North | Peri-Urban   | Grid    | Shingles | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_525/preprocessed.zip/) |
| 25  | 528     | 756    | Ngaoundere      | Cameroon    | Africa       | Peri-Urban   | Grid    | Metal    | [Download](https://fair-dev.hotosm.org/api/v1/workspace/download/training_528/preprocessed.zip/) |

Source and Credit : Anna

## **How to Get the Data**

You can use the following Python script to generate download links for all available training datasets:

```python
# List of training IDs from the table
training_ids = [
    364, 370, 372, 373, 391, 394, 397, 398, 399, 456, 
    459, 462, 463, 485, 488, 489, 529, 508, 539, 530, 
    526, 523, 524, 525, 528
]

base_url = "https://fair-dev.hotosm.org/api/v1/workspace/download/training_{}/preprocessed.zip/"

download_links = [base_url.format(train_id) for train_id in training_ids]

for link in download_links:
    print(link)
```
# **Dataset Structure & Download Guide**

## **Overview**
This dataset consists of **256x256 pixel image tiles** that follow the **Mercator tiling scheme**. Each tile is associated with:
- **Imagery ("chips/")**
- **Vector labels ("labels/")**
- **Binary masks ("binarymasks/") (optional)**

The filenames follow this **naming convention**:

**OAM-{mercantile_tile_x}-{mercantile_tile_y}-{zoom_level}.ext**

Where:
- **OAM**: Prefix indicating OpenAerialMap (or similar sources).
- **mercantile_tile_x / mercantile_tile_y**: Tile coordinates in the Mercator grid.
- **zoom_level**: The zoom level of the tile.
- **ext**: `.tif` (imagery), `.geojson` (labels), `.mask.tif` (binary masks).

---

## **Folder Structure**


### **1. Chips (`chips/`)**
- **Contains satellite/aerial imagery tiles**.
- Each `.tif` file corresponds to a **specific Mercator grid tile**.
- Example: `OAM-1251460-1026614-21.tif`.

### **2. Labels (`labels/`)**
- **Contains vector annotations (GeoJSON)**.
- Each file is clipped to the **exact boundary** of the corresponding image tile.
- Example: `OAM-1251450-1026604-21.geojson` matches `OAM-1251450-1026604-21.tif`.

### **3. Binary Masks (`binarymasks/`)**
- **Rasterized (burned) version of the labels**.
- Binary format (**0/1**) indicating building footprints.
- **Not required** if users prefer to generate masks from `chips/` and `labels/`.
- Example: `OAM-1251456-1026606-21.mask.tif`.

