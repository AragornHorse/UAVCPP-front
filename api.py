from flask import Flask, request, render_template, Response, stream_with_context, make_response, send_file
import json
from datetime import datetime
import solver as S
import random
import utils
import numpy as np
import cv2
import allocation

app = Flask(__name__)


# {'id': [time, Solver(), setting]}
projects = {}
max_project_num = 10


def generate_pid():

    def get_pid():
        pid = ''
        for i in range(10):
            pid += random.choice('qwertyuiopasdfghjklzxcvbnm1234567890QWERTYUIOPASDFGHJKLZXCVBNM')
        return pid

    pid = get_pid()
    while pid in projects.keys():
        pid = get_pid()

    return pid


@app.route('/list_projects', methods=['POST'])
def list_projects():
    resp = {}
    for pid, project in projects.items():
        start_time, solver, _ = project
        resp[pid] = solver.get_description()
        resp[pid]['time'] = start_time
    return json.dumps(resp)


@app.route('/test', methods=['GET'])
def connect():
    return 'hi'


@app.route('/create_project', methods=['POST'])
def create_project():
    data = request.get_data()
    data = json.loads(data)

    if len(projects) > max_project_num:
        return "max project number"

    pid = generate_pid()
    time = str(datetime.now())

    xyz0 = utils.get_matrix_coordinates(
        [float(num) for num in data['xyz0']['xyz0']],
        int(data['xyz0']['xnum']),
        int(data['xyz0']['ynum']),
        float(data['xyz0']['dx'])
    )
    n = int(data['xyz0']['xnum']) * int(data['xyz0']['ynum'])

    image = data['image']

    if image is None:
        xyze = utils.get_final_coordinates(
            n, [float(num) for num in data['xyze']['xyz0']], float(data['xyze']['dx'])
        )
    else:
        import base64
        image = base64.b64decode(image)
        image = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
        image = np.array(image)
        uv = allocation.image_to_points(image, n, float(data['xyze']['dx']))
        vec = [float(num) for num in data['xyze']['vec']]
        if vec[2] != 0.:
            v1 = np.cross(vec, np.array([vec[0], vec[1], 0.]))
        else:
            v1 = np.cross(vec, np.array([vec[0], vec[1], 1.]))
        v2 = np.cross(v1, vec)
        if v2[2] < 0:
            v2 = -v2
        w = np.stack([v1, v2], axis=0)    # 2, 3
        xyze = uv @ w + np.array([[float(num) for num in data['xyze']['xyz0']]])

    projects[pid] = [time, S.Solver(
        xyz0, xyze
    ), data]
    return json.dumps({
        'status': 'Succeed',
        'pid': pid
    })


@app.route('/load_project', methods=['POST'])
def load_project():
    pid = request.get_data().decode()
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]
    return json.dumps({
        'status': "succeed",
        'pid': pid,
        'setting': setting
    })


@app.route('/start_match', methods=['POST'])
def start_match():
    data = request.get_data()
    data = json.loads(data)
    pid = data['pid']
    iter_num = int(data['iter_num'])
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]

    def match():
        for resp in solver.match(iter_num):
            if resp is None:
                return json.dumps([])
            else:
                yield '\n' + json.dumps(list(resp))

    return Response(stream_with_context(match()), content_type='application/json; charset=utf-8')


@app.route('/delete_project', methods=['POST'])
def delete_project():
    pid = request.get_data().decode()
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    if projects[pid][1].running:
        return json.dumps({
            'status': f'pid {pid} is running'
        })
    projects.pop(pid)
    return json.dumps(({
        'status': 'succeed',
        'pid': pid
    }))


@app.route('/stop_running', methods=['POST'])
def stop_running():
    pid = request.get_data().decode()
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    projects[pid][1].stop()
    return json.dumps({
            'status': "succeed",
            'pid': pid
        })


@app.route('/')
def index():
    return render_template(r"index.html")


@app.route('/client.js')
def js():
    return render_template(r"client.js")


@app.route('/about.html')
def about():
    return render_template(r"about.html")


@app.route('/start_insert', methods=['POST'])
def start_insert():
    data = request.get_data()
    data = json.loads(data)
    pid = data['pid']
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]

    seg_idx = int(data['seg_idx'])
    wh = float(data['wh'])
    vecs = utils.get_vecs_from_norm_vec(np.array(data['vec']))
    x0 = np.array(data['xyz0'])
    danger_duv = float(data['dis'])
    w_max = float(data['w_max'])
    w_dis = float(data['w_dis'])
    lr = float(data['lr'])
    max_iter = int(data['iter_num'])
    mode = data['mode']
    feasible_solution = bool(data['fea'])

    def insert():
        for resp in solver.insert_intermediate_position(
                seg_idx, wh, vecs, x0, danger_duv, w_max, w_dis, lr, max_iter, mode, feasible_solution
        ):
            if resp is None:
                return '\n' + json.dumps({
                    'status': 'interrupted'
                })
            else:
                yield '\n' + json.dumps(resp)

    return Response(stream_with_context(insert()), content_type='application/json; charset=utf-8')


@app.route('/cancel_insert', methods=['POST'])
def cancel_insert():
    data = request.get_data()
    data = json.loads(data)
    pid = data['pid']
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]
    seg_idx = int(data['seg_idx'])
    solver.combine_segments(seg_idx)
    return json.dumps({
        'status': 'succeed',
        'pid': pid,
        'seg_idx': seg_idx
    })


@app.route('/start_path', methods=['POST'])
def start_path():
    data = request.get_data()
    data = json.loads(data)
    pid = data['pid']
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]
    seg_idx = int(data['seg_idx'])
    init_mode = data['init_mode']
    N = int(data['N'])
    if N <= 0:
        N = None
    dis = float(data['dis'])
    seg_dis = float(data['seg_dis'])
    cross_dis = float(data['cross_dis'])
    cross_seg_dis = float(data['cross_seg_dis'])
    w_max = float(data['w_max'])
    w_dis = float(data['w_dis'])
    w_seg_dis = float(data['w_seg_dis'])
    w_cross_dis = float(data['w_cross_dis'])
    w_cross_seg_dis = float(data['w_cross_seg_dis'])
    fea = bool(data['fea'])
    iter_num = int(data['iter_num'])
    lr = float(data['lr'])
    mode = data['mode']
    proj_mode = data['proj_mode']

    def path():
        for resp in solver.solve_segment(seg_idx, dis, seg_dis, cross_dis, cross_seg_dis,
              w_max, w_dis, w_seg_dis, w_cross_dis, w_cross_seg_dis, feasible_solution=fea,
              max_iter=iter_num, lr=lr, mode=mode, proj_mode=proj_mode, N=N, init_mode=init_mode):
            yield '\n' + json.dumps(resp)

    return Response(stream_with_context(path()), content_type='application/json; charset=utf-8')


@app.route('/start_output', methods=['POST'])
def start_output():
    data = request.get_data()
    data = json.loads(data)
    pid = data['pid']
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]

    nframe = int(data['nframe'])
    mode = data['mode']
    dis = float(data['dis'])

    resp = solver.output_to_json(dis, n_frame=nframe, pth=None, insert_mode=mode)
    return json.dumps(resp)


@app.route('/view_projects', methods=['POST'])
def view_projects():
    pid = request.get_data().decode()
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]
    xyzs = [solver.segments[0].xyz0]
    for seg in solver.segments:
        xyzs.append(seg.xyze)
    xyzs = np.concatenate(xyzs, axis=0)    # nn, 3
    import visual
    img_b64 = visual.scatter_3d(xyzs[:, 0], xyzs[:, 1], xyzs[:, 2], plot=False, ax=None, b64=True)
    return json.dumps({
        'status': 'succeed',
        'image': img_b64
    })


@app.route('/split_all', methods=['POST'])
def split_all():
    data = request.get_data()
    data = json.loads(data)
    pid = data['pid']
    if pid not in projects.keys():
        return json.dumps({
            'status': "pid doesn't exist"
        })
    time, solver, setting = projects[pid]
    solver.split(data['nframe'])
    return json.dumps({
        'status': 'succeed'
    })


if __name__ == '__main__':
    app.run(debug=True)
