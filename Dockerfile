FROM tensorflow/tensorflow:2.9.2-gpu-jupyter

RUN apt-get update && apt-get install -y python3-opencv
RUN add-apt-repository ppa:ubuntugis/ppa && apt-get update
RUN apt-get update
RUN apt-get install -y gdal-bin 
RUN apt-get install wget
RUN apt-get install -y libgdal-dev
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

#install numpy before gdal 
RUN pip install numpy==1.23.5

# pip install dependencies.
RUN pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`

COPY docker/ramp/docker-requirements.txt docker-requirements.txt
RUN pip install -r docker-requirements.txt

# Install ultralytics for YOLO, FastSAM, etc. together with pytorch and other dependencies
# For exact pytorch+cuda versions, see https://pytorch.org/get-started/previous-versions/
# RUN pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
#  RUN pip install torch==2.0.0 torchvision==0.15.1 torchaudio==2.0.1
# cuda 12.1 --- https://pytorch.org/get-started/previous-versions/
# RUN pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1
# RUN pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121
#RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# RUN pip install ultralytics==8.1.6
RUN pip install ultralytics==8.3.162
#  RUN pip install ultralytics

# pip install solaris -- try with tmp-free build
# COPY docker/ramp/solaris /tmp/solaris
COPY docker/solaris/solaris  /tmp/solaris/solaris
COPY docker/solaris/requirements.txt  /tmp/solaris/requirements.txt
COPY docker/solaris/setup.py /tmp/solaris/setup.py

RUN pip install /tmp/solaris --use-feature=in-tree-build

RUN pip install scikit-fmm --use-feature=in-tree-build

RUN pip install setuptools --upgrade 

ENV RAMP_HOME=/tf

# Install the package in development mode
COPY setup.py ./setup.py 
COPY hot_fair_utilities ./hot_fair_utilities
RUN pip install -e .

# install ramp-fair
RUN pip install ramp-fair mercantile pandas==1.5.3

## Copy Sample data
COPY ramp-data ./ramp-data

# Prepare ramp-code
RUN git clone --depth 1 https://github.com/kshitijrajsharma/ramp-code-fAIr.git ramp-code

# install gdown
RUN pip install gdown

# Download Basemodel
RUN gdown --fuzzy https://drive.google.com/file/d/1YQsY61S_rGfJ_f6kLQq4ouYE2l3iRe1k/view?usp=sharing

# Unzip and Move Basemodel
RUN unzip checkpoint.tf.zip -d ramp-code/ramp

RUN pip install 'git+https://github.com/facebookresearch/segment-anything.git'
RUN pip install -q roboflow supervision
RUN pip install imantics

#yolo obb models
# YOLO11n-obb	1024	78.4	117.6 ± 0.8	4.4 ± 0.0	2.7	17.2
# YOLO11s-obb	1024	79.5	219.4 ± 4.0	5.1 ± 0.0	9.7	57.5
# YOLO11m-obb	1024	80.9	562.8 ± 2.9	10.1 ± 0.4	20.9	183.5
# YOLO11l-obb	1024	81.0	712.5 ± 5.0	13.5 ± 0.6	26.2	232.0
# YOLO11x-obb	1024	81.3	1408.6 ± 7.7	28.6 ± 1.0	58.8	520.2
RUN wget -q 'https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n-obb.pt'


# moved to code (params in .env file)

#SAM_CHECKPOINT_URL = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
#SAM_CHECKPOINT_PATH = "/tf/sam_vit_b_01ec64.pth"
#SAM_MODEL_TYPE = "vit_b"

# RUN wget -q 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth'
# 2.4Gb
# RUN wget -q 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth'
# 1.2Gb
# RUN wget -q 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth'
# 358Mb
#RUN wget -q 'https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth'


# Copy test_app.py
#COPY test_app.py ./test_app.py
#COPY test_yolo.py ./test_yolo.py
COPY yolo11n-seg.pt ./yolo11n-seg.pt
COPY yolo11n.pt ./yolo11n.pt
COPY yolo_v11_obb.pt ./yolo_v11_obb.pt
COPY test_ramp.py ./test_ramp.py
COPY test_yolo_v1.py ./test_yolo_v1.py
COPY test_yolo_v2.py ./test_yolo_v2.py
COPY test_yolo_v11.py ./test_yolo_v11.py
COPY check_cuda.ipynb ./check_cuda.ipynb
COPY Package_Test.ipynb ./Package_Test.ipynb
COPY test_yolo_v11.ipynb ./test_yolo_v11.ipynb
COPY test_yolo_v11_sam.ipynb ./test_yolo_v11_sam.ipynb
COPY yolo_sam.ipynb ./yolo_sam.ipynb