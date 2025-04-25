# emAlioss
emAlioss 是基于Pyside6的小工具，用于管理小规模的图片以及文件。
![home_page](https://emnavi-doc-img.oss-cn-beijing.aliyuncs.com/emalioss_assets/pyside_version/home_page.png)
支持平台
- win
- ubuntu

> 注意: 当前配置文件是独立的，请查看[config配置](#config配置)

## 快速开始
### win安装

推荐直接[下载安装包](https://github.com/hyaline-wang/emAlioss/releases)
> 默认安装位置为 C:\Users\XXX\AppData\Local\Programs\alioss_tool

手动构建可使用
```bash
git clone https://github.com/hyaline-wang/emAlioss.git
cd emAlioss
pip install cx_Freeze
pip install -r requirements.txt
python setup.py bdist_msi
```

### ubuntu 安装

安装依赖
```bash
sudo apt-get install --reinstall libxcb-xinerama0 libxcb1 libx11-xcb1 libxcb-util1 libxcb-cursor0
sudo apt-get install alien python3 python3-pip python3-venv
```
安装
```bash
# 视情况pip为更换清华源
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple


git clone https://github.com/hyln/emAlioss.git
cd emAlioss
## 请将conda 环境退出
conda deactivate

python3 -m venv ossenv 
source ossenv/bin/activate
pip install .
echo "alias emalioss=./emAlioss/ossenv/bin/emalioss" >> ~/.bashrc
```
使用
```bash
emalioss
```

### config配置

> 对于内部使用，请从飞书文档中**阿里云oss文件管理**直接复制`config.ini`配置
> 对于文档构建
> imageprefix->prefix 填写 `emnavi_assets`
> prjprefix->prefix  填写 `emnavi_video`

Alioss Img Tools 从`HOME`目录寻找配置文件`emalioss.ini`即
- win: C:\Users\xxxx\emalioss.ini
- ubuntu: /home/xxxx/emalioss.ini
若没有`emalioss.ini`可新建,配置文件标准格式为
```
[ossconfig]
alibaba_cloud_access_key_id = <ALIBABA_CLOUD_ACCESS_KEY_ID>
alibaba_cloud_access_key_secret = <ALIBABA_CLOUD_ACCESS_KEY_SECRET>
bucket = <YOUR_BUCKET_NAME>
endpoint = https://oss-cn-beijing.aliyuncs.com
region = cn-beijing
[imageprefix]
prefix = <your_image_root_folder>
[prjprefix]
prefix = oss_prj_test
````
配置完成后再次打开软件时生效

对于`<your_image_root_folder>`是一个自定义参数，是一个云端文件夹，起一个自己喜欢的名字即可
对于`prjprefix`，当前还未完成



### 图片上传

进入程序后使用首先选择目标**存储文件夹**，若没有请在`图片管理`中新建
![upload_image](https://emnavi-doc-img.oss-cn-beijing.aliyuncs.com/emalioss_assets/pyside_version/upload_image.png)
- 有三种图片上传方式
    - 托拽，
    - 从粘贴板粘贴
    - 点击上传文件
- 上传后点击 `复制当前图片链接` 即可复制缩略图显示的图片链接
- 托拽支持多张图同时上传

### 图片管理
> 当前程序bug较多，有事没事 refresh 一下
![](https://emnavi-doc-img.oss-cn-beijing.aliyuncs.com/emalioss_assets/pyside_version/pic_manage.png)

### 文件管理
> 当前程序bug较多，有事没事 refresh 一下

![](https://emnavi-doc-img.oss-cn-beijing.aliyuncs.com/emalioss_assets/pyside_version/big_image_manage.png)


## 如何配置

- [如何配置阿里云对象存储](./docs/ali_oss.md)

1. 网络问题可能导致无法连接至oss:，可以尝试以下更换网络，看是否能解决
2. 上传图片后不更新，`refresh`一下试试
