.. UAVCPP-front documentation master file, created by
   sphinx-quickstart on Mon Dec 23 17:48:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


**UAVCPP-front 文档**
==========================


**API**
-----------

**测试连接**
___________

**path** : ``/test``

**method**: GET

**parameters**: none

**response**: ``"hi"``

**example**

.. code-block:: python

   import requests
   url = r"http://121.89.192.173:5000/"
   print(requests.get(f"{url}test").text)
   >>> hi


**创建项目**
_____________________

**path** : ``/create_project``

**method**: POST

**parameters**:

- ``uav``
   - ``dx`` (float): 无人机直径
- ``xyz0`` : 机群初始方阵位置
   - ``xnum`` (int): x轴方向方阵无人机数量
   - ``ynum`` (int): y轴方向方阵无人机数量
   - ``dx`` (float): 无人机间隔
   - ``xyz0`` ([float, float, float]): 方阵最小[xyz]坐标
- ``xyze`` : 机群最终位置
   - ``vec`` ([float, float, float]): 图案平面法向量
   - ``dx`` (float): 无人机间隔
   - ``xyz0`` ([float, float, float]): 图案平面最小[xyz]坐标
   - ``file`` : null
- ``image`` (string): 图案图片的base64编码

**response**:

- ``status`` : "succeed"
- ``pid`` : 项目的pid



**加载项目**
__________________

**path** : ``/load_project``

**method**: POST

**parameters**:

- (string): pid

**response**:

- ``status`` : "succeed"
- ``pid`` : 项目id
- ``uav``
   - ``dx`` (float): 无人机直径
- ``xyz0`` : 机群初始方阵位置
   - ``xnum`` (int): x轴方向方阵无人机数量
   - ``ynum`` (int): y轴方向方阵无人机数量
   - ``dx`` (float): 无人机间隔
   - ``xyz0`` ([float, float, float]): 方阵最小[xyz]坐标
- ``xyze`` : 机群最终位置
   - ``vec`` ([float, float, float]): 图案平面法向量
   - ``dx`` (float): 无人机间隔
   - ``xyz0`` ([float, float, float]): 图案平面最小[xyz]坐标
   - ``file`` : null
- ``image`` (string): 图案图片的base64编码

**example**

.. code-block:: python

   import requests
   url = r"http://121.89.192.173:5000/"
   print(requests.post(f"{url}load_project", data='OPPtHnujhg').text)
   >>>{"status": "succeed", "pid": "OPPtHnujhg", "setting": {"uav": {"dx": "1.5"}, "xyz0": {"xnum": "10", "ynum": "25", "dx": "2", "xyz0": ["0", "0", "0"]}, "xyze": {"vec": ["0", "1", "0"], "dx": "2", "xyz0": ["0", "500", "50"], "file": "C:\\fakepath\\icon.png"}, "image": "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"}}




**列出所有现有项目**
_____________________

**path** : ``/list_projects``

**method**: POST

**parameters**: none

**response**:

- pid
   - ``time`` (string): 创建时间
   - ``seg_num`` (string): 路段数量
   - ``N`` (int): 路径关键点数量
   - ``n`` (int): 无人机数量
   - ``running`` (bool): 状态

**example**

.. code-block:: python

   import requests
   url = r"http://121.89.192.173:5000/"
   print(requests.post(f"{url}list_projects", data=None).text)
   >>>{"cwOGPIBhAW": {"seg_num": 1, "N": 12, "n": 375, "running": false, "time": "2024-12-17 13:54:39.780525"}, "wUu1rDCCJp": {"seg_num": 3, "N": 34, "n": 450, "running": false, "time": "2024-12-17 13:56:46.270063"}, "xzIzcAzrsZ": {"seg_num": 1, "N": 12, "n": 500, "running": false, "time": "2024-12-17 14:02:29.368565"}, "0lTLydoQeQ": {"seg_num": 1, "N": 12, "n": 450, "running": false, "time": "2024-12-17 14:04:06.650212"}, "aytyekv1my": {"seg_num": 1, "N": 12, "n": 250, "running": false, "time": "2024-12-18 17:19:25.420759"}, "OPPtHnujhg": {"seg_num": 1, "N": 12, "n": 250, "running": false, "time": "2024-12-18 17:20:40.194130"}, "JMW2rW89nN": {"seg_num": 1, "N": 12, "n": 250, "running": false, "time": "2024-12-19 09:58:19.705704"}, "uHAEZRvzW8": {"seg_num": 1, "N": 12, "n": 250, "running": false, "time": "2024-12-20 11:05:02.159516"}, "wbELAN92sH": {"seg_num": 1, "N": 12, "n": 250, "running": false, "time": "2024-12-20 11:06:16.534606"}, "JKEservAPC": {"seg_num": 21, "N": 100, "n": 250, "running": false, "time": "2024-12-20 14:01:27.666317"}, "RLb0Q5oMTf": {"seg_num": 1, "N": 12, "n": 250, "running": false, "time": "2024-12-20 23:32:36.882104"}}



**删除项目**
__________________

**path** : ``/delete_project``

**method**: POST

**parameters**:

- (string): pid

**response**:

- ``status`` : "succeed"
- ``pid`` : pid



**插入中转平面**
________________________

**path** : ``/start_insert``

**method**: POST

**parameters**:

- ``wh`` (float): 平面宽度
- ``vec`` ([float, float, float]): 平面法向量
- ``xyz0`` ([float, float, float]): 平面中点坐标
- ``seg_idx`` (int): 在第几个路段上插入
- ``dis`` (float): 平面上无人机最小间隔
- ``w_max`` (float): 目标函数的参数
- ``w_dis`` (float): 惩罚性系数
- ``lr`` (float): 学习率
- ``iter_num`` (int): 最大迭代次数
- ``mode`` (string): 损失函数模式，从['add' , `div`]中选
- ``fea`` (bool): 是否只保留可行解
- ``pid`` (string): pid

**response** (流式响应):

- ``status`` : "succeed"
- ``loss`` (float): 当前损失值
- ``danger_num`` : 距离过近无人机对数
- ``avg_seg`` : 平均路长
- ``max_seg`` : 最大路长
- ``duv`` : 描述无人机平均间隔的量，越大越好

**example**

.. code-block:: python

   import requests
   import json
   url = r"http://121.89.192.173:5000/"
   for resp in requests.post(f"{url}start_insert", data=json.dumps({
       'pid': 'OPPtHnujhg',
       'wh': 200,
       'vec': [1., 1., 1.],
       'xyz0': [100., 100., 100.],
       'seg_idx': 0,
       'dis': 3.,
       'w_max': 10.,
       'w_dis': 100.,
       'lr': 0.01,
       'iter_num': 2,
       'mode': 'add',
       'fea': False,
   }), stream=True):
       print(resp.decode())
   >>>{"status": "succeed", "epoch": 0, "loss": 1760.1331183496823, "avg_seg": 154.59027921853757, "max_seg": 174.06800202576008, "duv": -1.3513718112645599, "danger_num": 1822.0}
   >>>{"status": "succeed", "epoch": 1, "loss": 1759.3927153494533, "avg_seg": 154.58892602678816, "max_seg": 173.99942516902198, "duv": -1.3519046236755456, "danger_num": 1822.0}


**删除中转平面**
_________________________

**path** : ``/cancel_insert``

**method**: POST

**parameters**:

- ``seg_idx`` (int): 中转平面编号（等于插入时的段编号）
- ``pid`` (string): pid

**response** (stream):

- ``status`` : "succeed"
- ``pid`` (string): pid



**停止运行（包括所有迭代操作）**
______________

**path** : ``/stop_running``

**method**: POST

**parameters**:

- (string): pid

**response**:

- ``status``: "succeed"



**开始匹配**
___________

**path** : ``/start_match``

**method**: POST

**parameters**:

- ``pid`` (string): pid
- ``iter_num`` (int): 最大迭代次数

**response**  (stream):

- ``status`` : 'succeed'
- ``loss`` :  当前损失值
- ``avg_len`` : 无人机平均路长
- ``max_len`` :  最大无人机路长


**优化路段**
________________________

**path** : ``/start_path``

**method**: POST

**parameters**:

- ``pid`` (string): pid
- ``seg_idx`` (int): 待优化的路段编号，-1代表所有路段
- ``init_mode`` (string): 初始化方法，从['proj', 'inter' and 'rea']中选
- ``N`` (int): 路径关键点数
- ``dis`` (float): 关键点距离阈值
- ``seg_dis`` (float): 路径距离阈值
- ``cross_dis`` (float): 点线路径阈值
- ``cross_seg_dis`` (float): 线线交叉距离阈值
- ``w_max`` (float): 损失函数参数
- ``w_dis`` (float): 惩罚项系数
- ``w_seg_dis`` (float): 惩罚项系数
- ``w_cross_dis`` (float): 惩罚项系数
- ``w_cross_seg_dis`` (float): 惩罚项系数
- ``fea`` (bool): 是否只保留可行解
- ``lr`` (float): 学习率
- ``mode`` (string): 损失函数模式，从['add', 'div']中选
- ``proj_mode`` (string): 投影模式, 从['proj', 'rea', 'clip', 'inter', 'dyn']中选
- ``iter_num`` (int): 最大迭代次数


**response**  (流式响应):

- ``stage`` : 'solve'
- ``status`` : 'succeed'
- ``epoch`` : 迭代进度
- ``loss`` :  损失值
- ``avg_len`` : 平均路长
- ``max_len`` :  最大路长
- ``dis_num`` : 小于阈值的关键点对数
- ``seg_num`` : 小于阈值的路径对数
- ``cross_num`` : 小于阈值的点线对数
- ``cross_seg_num`` : 小于阈值的线线交叉距离对数


**输出**
___________

**path** : ``/start_output``

**method**: POST

**parameters**:

- ``pid`` (string): pid
- ``dis`` (int): 无人机直径
- ``mode`` (string): 插帧算法，从['linear', 'nocol']中选
- 'nframe' (int): 帧数

**response**:

- ``status`` : 'succeed'
- ``col_num`` (int): 碰撞次数
- ``col_rate`` (float): 碰撞概率
- ``rst`` (bool): 算法状态
- ``result`` : 运行结果



**可视化**
______________

**path** : ``/view_projects``

**method**: POST

**parameters**:

- pid

**response**:

- ``status`` : 'succeed'
- ``image`` : 可视化图像的base64编码



**细化路段**
_______________

**path** : ``/split_all``

**method**: POST

**parameters**:

- pid

**response**:

- ``status`` : 'succeed'



