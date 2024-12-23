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



start match
___________

**path** : ``/start_match``

**method**: POST

**parameters**:

- ``pid`` (string): pid
- ``iter_num`` (int): max number of iterations

**response**:  (stream)

-




