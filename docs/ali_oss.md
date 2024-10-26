# 在阿里云创建 bucket

以下假设已经有了阿里云账户

### 价格

阿里云的[收费方式](https://www.aliyun.com/price/product?spm=5176.8466032.bucket-overview.5.6c061450yTTVek#/oss/detail/oss)比较复杂，但对于日常使用可以总结如下

免费的部分是
- api访问低于500 万次,免费
- 数据上传到oss
- 图片处理每月 0 - 10 TB （应该包含压缩）
收费的部分是
- 少量数据的存储并不贵
- 下行流量比较贵，忙时0.5元/GB，闲时0.25元/GB(08:00 - 24:00)


### 设置 bucket

首先[新建一个bucket](https://oss.console.aliyun.com/bucket)。关键设置为
- Bucket ACL 公共读
Alioss Tools 在同一个bucket中通过不同文件夹分类不同类型的文件，请手动在bucket中添加这两个文件夹
- project_tar ： 存储开源项目的压缩包
- images: 存储开源项目

### 设置oss

在ram访问控制中[添加用户](https://ram.console.aliyun.com/users)