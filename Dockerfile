FROM debian
WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install -y wget python3 python3-pip 
RUN wget https://udomain.dl.sourceforge.net/project/gdal-wheels-for-linux/GDAL-3.4.1-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.whl && \
python3 -m pip install GDAL-3.4.1-cp39-cp39-manylinux_2_5_x86_64.manylinux1_x86_64.whl 
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
