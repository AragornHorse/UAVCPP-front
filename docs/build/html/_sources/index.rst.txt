.. UAVCPP-front documentation master file, created by
   sphinx-quickstart on Mon Dec 23 17:48:40 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

UAVCPP-front documentation
==========================

APIs
-----------

test
___________

**path** : ``/test``

**method**: GET

**parameters**:none

**response**: ``"hi"``


create project
___________

**path** : ``/create_project``

**method**: POST

**parameters**:

- ``uav``
   - ``dx`` (float): The diameter of an UAV
- ``xyz0`` : the UAVs square array at the initial moment
   - ``xnum`` (int): The number of UAVs in the x-axis direction
   - ``ynum`` (int): The number of UAVs in the y-axis direction
   - ``dx`` (float): The distance between UAVs
   - ``xyz0`` ([float, float, float]): The minimum xyz coordinate
- ``xyze`` : the final pattern plane
   - ``vec`` ([float, float, float]): The normal vector of
   - ``dx`` (float): The distance between UAVs
   - ``xyz0`` ([float, float, float]): The minimum xyz coordinate
   - ``file`` : null
- ``image`` (string): Base64 encoding of the final pattern image

**response**:

- ``status`` : "succeed"
- ``pid`` : project identify (pid)



load project
___________

**path** : ``/load_project``

**method**: POST

**parameters**:

- (string): pid

**response**:

- ``status`` : "succeed"
- ``pid`` : project identify (pid)
- ``uav``
   - ``dx`` (float): The diameter of an UAV
- ``xyz0`` : the UAVs square array at the initial moment
   - ``xnum`` (int): The number of UAVs in the x-axis direction
   - ``ynum`` (int): The number of UAVs in the y-axis direction
   - ``dx`` (float): The distance between UAVs
   - ``xyz0`` ([float, float, float]): The minimum xyz coordinate
- ``xyze`` : the final pattern plane
   - ``vec`` ([float, float, float]): The normal vector of
   - ``dx`` (float): The distance between UAVs
   - ``xyz0`` ([float, float, float]): The minimum xyz coordinate
   - ``file`` : null



list project
___________

**path** : ``/list_projects``

**method**: POST

**parameters**: none

**response**:

- pid
   - ``time`` (string): create time
   - ``seg_num`` (string): segment number
   - ``N`` (int): key point number per UAV
   - ``n`` (int): UAV number
   - ``running`` (bool): solver status


delete project
___________

**path** : ``/delete_project``

**method**: POST

**parameters**:

- pid

**response**:

- pid
   - ``time`` (string): create time
   - ``seg_num`` (string): segment number
   - ``N`` (int): key point number per UAV
   - ``n`` (int): UAV number
   - ``running`` (bool): solver status



insert transfer plane
___________

**path** : ``/start_insert``

**method**: POST

**parameters**:

- ``wh`` (float): weight of the transfer plane
- ``vec`` ([float, float, float]): Normal vector
- ``xyz0`` ([float, float, float]): Midpoint coordinate
- ``seg_idx`` (int): segment id to insert
- ``dis`` (float): threshold of point pair distance
- ``w_max`` (float): loss weight
- ``w_dis`` (float): regularization weight
- ``lr`` (float): learning rate
- ``iter_num`` (int): maximum iteration time
- ``mode`` (string): loss function mode, choose from add, div
- ``fea`` (bool): whether only feasible solution
- ``pid`` (string): pid

**response** (stream):

- ``status`` : "succeed"
- ``loss`` (float): loss
- ``danger_num`` : The number of distances less than the threshold
- ``avg_seg`` : average path length
- ``max_seg`` : maximum path length
- 哈哈啊哈


delete transfer plane
___________

**path** : ``/cancel_insert``

**method**: POST

**parameters**:

- ``seg_idx`` (int): segment id to delete
- ``pid`` (string): pid

**response** (stream):

- ``status`` : "succeed"
- ``pid`` (string): pid



stop running
___________

**path** : ``/stop_running``

**method**: POST

**parameters**:

- pid

**response**:

- ``status``: "succeed"



match
___________

**path** : ``/start_match``

**method**: POST

**parameters**:

- ``pid`` (string): pid
- ``iter_num`` (int): max number of iterations

**response**  (stream):

- ``status`` : 'succeed'
- ``loss`` :  current loss
- ``avg_len`` : current average path length
- ``max_len`` :  largest path length
- ``dis_num`` : The number of key point pairs on the path with a distance less than the threshold



optimize segment
___________

**path** : ``/start_path``

**method**: POST

**parameters**:

- ``pid`` (string): pid
- ``seg_idx`` (int): segment id to optimize, -1 for all segments
- ``init_mode`` (string): initialization method, choose from 'proj', 'inter' and 'rea'
- ``N`` (int): number of key points
- ``dis`` (float): threshold of key point pair distance
- ``seg_dis`` (float): threshold of segment pair distance
- ``cross_dis`` (float): threshold of key point segment pair distance
- ``cross_seg_dis`` (float): threshold of segment pair cross distance
- ``w_max`` (float): loss weight
- ``w_dis`` (float): regularization weight
- ``w_seg_dis`` (float): regularization weight
- ``w_cross_dis`` (float): regularization weight
- ``w_cross_seg_dis`` (float): regularization weight
- ``fea`` (bool): whether only feasible solution
- ``lr`` (float): learning rate
- ``mode`` (string): mode of loss function, choose from add, div
- ``proj_mode`` (string): Mode of gradient projection, choose from proj, rea, clip, inter, dyn
- ``iter_num`` (int): max number of iterations


**response**  (stream):

- ``stage`` : 'solve'
- ``status`` : 'succeed'
- ``epoch`` : Current iteration progress
- ``loss`` :  current loss
- ``avg_len`` : current average path length
- ``max_len`` :  largest path length
- ``dis_num`` : The number of key point pairs on the path with a distance less than the threshold
- ``seg_num`` : The number of segment pairs on the path with a distance less than the threshold
- ``cross_num`` : The number of segment-point pairs on the path with a distance less than the threshold
- ``cross_seg_num`` : The number of segment pairs on the path with a cross distance less than the threshold




output
___________

**path** : ``/start_output``

**method**: POST

**parameters**:

- ``pid`` (string): pid
- ``dis`` (int): diameter of UAV
- ``mode`` (string): algorithm to generate frames, choose from linear, nocol
- 'nframe' (int): number of frame

**response**:

- ``status`` : 'succeed'
- ``col_num`` (int): Number of collisions
- ``col_rate`` (float): rate of collisions
- ``rst`` (bool): status of algorithm
- ``result`` : json result



Visualization
___________

**path** : ``/view_projects``

**method**: POST

**parameters**:

- pid

**response**:

- ``status`` : 'succeed'
- ``image`` : base64 encode of image



split
___________

**path** : ``/split_all``

**method**: POST

**parameters**:

- pid

**response**:

- ``status`` : 'succeed'
