import numpy as np
from osgeo import gdal
import pickle
import os
from flask import Flask, request, send_file, render_template

gdal.UseExceptions()

app = Flask(__name__)

@app.route('/')
def upload_file():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    # 上传地理位置数据和训练好的模型
    geotif = request.files['geotif']
    pkl = request.files['pkl']
    if geotif and pkl:
        # 将上传的tif格式的位置数据和pkl格式的模型数据存下来
        geotif_path = './data/' + geotif.filename
        geotif.save(geotif_path)
        model_path = './data/' + pkl.filename
        pkl.save(model_path)

        # 使用pickle读取模型
        with open(model_path, 'rb') as file:
            model = pickle.load(file)

        # 使用gdal库读取tif格式的数据
        Tif_data, Tif_info = read_large_tif(geotif_path)
        Tif_width = Tif_data.shape[2]  # 栅格矩阵的列数
        Tif_height = Tif_data.shape[1]  # 栅格矩阵的行数
        Tif_geotrans = Tif_info['geo_trans']  # 获取仿射矩阵信息
        Tif_proj = Tif_info['proj']  # 获取投影信息

        data = np.zeros((Tif_data.shape[0], Tif_height * Tif_width))
        for i in range(Tif_data.shape[0]):
            data[i] = Tif_data[i].flatten()
        data = data.swapaxes(0, 1)

        # 使用模型进行预测
        pred = model.predict(data)
        # 将预测结果重塑为原本的矩阵形式并转换为整数类型
        pred = pred.reshape(Tif_height, Tif_width)
        pred = pred.astype(np.uint8)

        output_path = './output/out_pred.tif'  # 将结果保存到指定的路径
        writeTiff(pred, Tif_geotrans, Tif_proj, output_path)

        return send_file(output_path, as_attachment=True)

    return 'Upload failed'

def read_large_tif(file_path, block_size=512):
    """
    Read large geo-tif by blocks
    :param file_path: file path
    :param block_size: block size, default 512
    :return: [array, raster_info]
    """
    ds = gdal.Open(file_path)
    block_cols = np.ceil(ds.RasterXSize / block_size).astype(int)
    block_rows = np.ceil(ds.RasterYSize / block_size).astype(int)
    band = ds.GetRasterBand(1)
    raster_info = {
        "cols": ds.RasterXSize,
        "rows": ds.RasterYSize,
        "geo_trans": ds.GetGeoTransform(),
        "proj": ds.GetProjection()
    }
    data = None
    for i in range(block_rows):
        rows = block_size if (i + 1) * block_size < ds.RasterYSize else ds.RasterYSize - i * block_size
        for j in range(block_cols):
            cols = block_size if (j + 1) * block_size < ds.RasterXSize else ds.RasterXSize - j * block_size
            # 读取数据块并进行类型转换
            data_block = band.ReadAsArray(j * block_size, i * block_size, cols, rows).astype(np.int16)
            if data is None:
                data = np.zeros((ds.RasterCount, ds.RasterYSize, ds.RasterXSize), dtype=np.int16)
            data[:, i * block_size:i * block_size + rows, j * block_size:j * block_size + cols] = data_block
    return data, raster_info

def writeTiff(im_data, im_geotrans, im_proj, path):
    if 'int8' in im_data.dtype.name:
        datatype = gdal.GDT_Byte
    elif 'int16' in im_data.dtype.name:
        datatype = gdal.GDT_UInt16
    else:
        datatype = gdal.GDT_Float32
    if len(im_data.shape) == 2:
        im_data = np.array([im_data])
    im_bands, im_height, im_width = im_data.shape
    # 创建 GeoTiff 文件并设置其相关信息
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(path, int(im_width), int(im_height), int(im_bands), datatype)
    if dataset != None:
        dataset.SetGeoTransform(im_geotrans)
        dataset.SetProjection(im_proj)
    # 将 numpy 数组写入 GeoTiff
    for i in range(im_bands):
        dataset.GetRasterBand(i + 1).WriteArray(im_data[i])
    del dataset


if __name__ == '__main__':
    app.run()
