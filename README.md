# 使用 Flask 构建地理位置数据与机器学习模型结合的 Python 应用
这个 Python 应用利用了 Flask、GDAL 和 pickle 库。它通过 Web 界面接收用户上传的地理位置数据文件和机器学习模型文件，然后使用 GDAL 库读取位置数据，并将其转换成模型可以识别的格式。随后，应用会使用 pickle 序列化库读取机器学习模型文件，并使用该模型进行预测，将预测结果保存为 GeoTiff 格式的文件。最后，应用将预测结果发送回用户，以供后续分析和使用。
## 构建 Docker 镜像
要构建 Docker 镜像，请确保已经安装 Docker，并在本地目录下创建一个名为 `Dockerfile` 的文件，并将以下代码复制到其中：
```
FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN apt-get update && \
    apt-get install -y gdal-bin python3-gdal
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "app.py"]
```
接着，在终端中进入该目录并运行以下命令来构建 Docker 镜像：
```
docker build -t docker_test_water .
```
该命令将使用 `Dockerfile` 中定义的指令来构建一个名为 `docker_test_water` 的 Docker 镜像。
## 启动 Docker 容器
要启动 Docker 容器，请使用以下命令：
```
docker run -p -d 5000:5000 -v /path/to/data:/app/data docker_test_water
```
其中，`/path/to/data` 为数据文件所在的目录。以上命令将在 Docker 容器内部启动该应用，同时将容器内部的 5000 端口映射到主机的 5000 端口。此外，还将主机的数据目录挂载到 Docker 容器的 `/app/data` 目录下，以便应用可以读取和保存文件。
## 访问 Web 界面
启动容器后，可在浏览器中输入 `http://localhost:5000` 来访问应用的 Web 界面，并上传地理位置数据和机器学习模型文件。完成上传后，应用将使用 pickle 序列化库读取模型文件并使用 GDAL 库读取位置数据。随后，它会使用该模型进行预测，并将预测结果保存为 GeoTiff 文件。在完成所有处理后，应用会将生成的文件提供给用户下载。
