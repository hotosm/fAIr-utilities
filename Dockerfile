FROM tensorflow/tensorflow:2.9.2-gpu-jupyter

RUN apt-get update && apt-get install -y python3-opencv
RUN add-apt-repository ppa:ubuntugis/ppa && apt-get update
RUN apt-get update
RUN apt-get install -y gdal-bin
RUN apt-get install -y libgdal-dev
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

#install numpy before gdal 
RUN pip install numpy==1.23.5

# pip install dependencies.
RUN pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`

COPY docker/ramp/docker-requirements.txt docker-requirements.txt
RUN pip install -r docker-requirements.txt

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