import numpy as np
import matplotlib.pyplot as plt
import intermediate_position
import matching
import path_solver
import visual
import utils
import transform


class Solver:
    def __init__(self, xyz0, xyze, init_mode='rea', N=10):
        self.segments = [path_solver.GradientPathSolver(init_mode, xyz0, xyze, N)]
        self.init_mode = init_mode
        self.running = False

    def match(self, max_iter=50):
        if len(self.segments) > 1:
            yield {'status': 'warning: more than 1 segments'}

        if self.running:
            return {'status': 'still running'}
        self.running = True

        seg = self.segments[-1]
        solves = None

        for upper, solves, log_rate in matching.match(
            seg.xyz0, seg.xyze, only_one_solve=True, max_iter=max_iter
        ):
            yield {'status': 'succeed', 'upper': upper}
            if not self.running:
                break

        if solves is not None:
            xyze = seg.xyze[solves[0], :]
        else:
            xyze = seg.xyze
        self.segments.pop(-1)
        self.segments.append(path_solver.GradientPathSolver(seg.init_mode, seg.xyz0, xyze, seg.N))
        self.running = False

    def combine_segments(self, seg1_idx, N=None):
        if len(self.segments) < 2:
            return {'status': "can't combine less than 2 segments"}
        seg2 = self.segments.pop(seg1_idx + 1)
        seg1 = self.segments.pop(seg1_idx)
        N_ = seg1.N + seg2.N + 1
        if N is not None and N != N_:
            seg = path_solver.GradientPathSolver(seg1.init_mode, seg1.xyz0, seg2.xyze, N)
        else:
            xyz = np.concatenate([
                seg1.get_complete_xyz()[1:], seg2.get_complete_xyz()[1:-1]
            ], axis=0)
            seg = path_solver.GradientPathSolver(seg1.init_mode, seg1.xyz0, seg2.xyze, xyz.shape[0])
            seg.xyz = xyz
        self.segments.insert(seg1_idx, seg)

    def insert_intermediate_position(self,
                                     seg_idx, wh, vecs, x0, danger_duv, w_max, w_dis, lr=0.2, max_iter=100, mode='div',
                                     feasible_solution=True
                                     ):
        if self.running:
            return {'status': 'running'}
        self.running = True
        seg = self.segments[seg_idx]
        init_mode = seg.init_mode
        N = seg.N
        xyz0 = seg.xyz0
        xyze = seg.xyze
        solver = intermediate_position.GradientIntermediateSolver(xyz0, xyze, wh, vecs, x0)

        for rst in solver.solve(danger_duv, w_max, w_dis, lr, max_iter, mode, feasible_solution):
            yield rst
            if not self.running:
                break

        xyz = solver.get_xyz()
        self.segments.pop(seg_idx)
        self.segments.insert(seg_idx, path_solver.GradientPathSolver(init_mode, xyz0, xyz, N))
        self.segments.insert(seg_idx+1, path_solver.GradientPathSolver(init_mode, xyz, xyze, N))
        self.running = False

    def solve_segment(self, seg_idx, danger_dx, danger_seg_dx, cross_danger_dis, danger_cross_seg_dis,
              w_max, w_dis, w_seg_dis, w_cross_dis, w_cross_seg_dis, feasible_solution=False,
              max_iter=100, lr=0.5, mode='add', proj_mode='proj', N=None, init_mode=None):

        if self.running:
            return {'status': 'still running'}
        self.running = True

        if seg_idx >= len(self.segments):
            self.running = False
            return {'status': 'seg_idx out of range'}

        if (N is not None and N != self.segments[seg_idx].N) or\
                (init_mode is not None and init_mode != self.segments[seg_idx].init_mode):
            if init_mode is None:
               init_mode = self.segments[seg_idx].init_mode
            if N is None:
                N = self.segments[seg_idx].N
            self.segments[seg_idx] = path_solver.GradientPathSolver(
                init_mode, self.segments[seg_idx].xyz0, self.segments[seg_idx].xyze, N
            )

        if seg_idx >= 0:
            for resp in self.segments[seg_idx].solve(
                danger_dx, danger_seg_dx, cross_danger_dis, danger_cross_seg_dis,
                  w_max, w_dis, w_seg_dis, w_cross_dis, w_cross_seg_dis,
                  max_iter, lr, mode, proj_mode, feasible_solution
            ):
                yield resp
                if not self.running:
                    break
        else:
            for sid, seg in enumerate(self.segments):
                yield {'status': f'start sid {sid}'}
                for resp in seg.solve(
                        danger_dx, danger_seg_dx, cross_danger_dis, danger_cross_seg_dis,
                        w_max, w_dis, w_seg_dis, w_cross_dis, w_cross_seg_dis,
                        max_iter, lr, mode, proj_mode, feasible_solution
                ):
                    yield resp
                    if not self.running:
                        break

        self.running = False

    def get_complete_xyz(self):
        lst = [self.segments[0].xyz0[None, :, :]]
        for seg in self.segments:
            lst.append(seg.get_complete_xyz()[1:-1, :, :])
        lst.append(self.segments[-1].xyze[None, :, :])
        xyzs = np.concatenate(lst, axis=0)
        return xyzs

    def plot(self):
        ax = None
        xyz = self.get_complete_xyz()
        for i in range(xyz.shape[1]):
            ax = visual.plot_3d(xyz[:, i, 0], xyz[:, i, 1], xyz[:, i, 2], False, ax)
        visual.scatter_3d(xyz[0, :, 0], xyz[0, :, 1], xyz[0, :, 2], False, ax)
        visual.scatter_3d(xyz[-1, :, 0], xyz[-1, :, 1], xyz[-1, :, 2], False, ax)
        plt.show()

    def plot_example(self):
        xyz = self.get_complete_xyz()
        visual.scatter_3d(xyz[:, ::200, 0], xyz[:, ::200, 1], xyz[:, ::200, 2])

    def collision_detection(self, dis):
        col_num, col_rate, min_dis = utils.collision_detection(self.get_complete_xyz(), dis)
        print(f"col_num: {col_num}, col_rate: {col_rate}, min_dis: {min_dis}")

    def output_to_json(self, dis, n_frame=None, pth=None, insert_mode='linear'):
        if self.running:
            return None
        self.running = True

        assert insert_mode in ['linear', 'nocol']

        xyz = self.get_complete_xyz()

        if not self.running:
            return {'status': 'interrupted'}

        if n_frame is None:
            n_frame = xyz.shape[0]

        if insert_mode == 'linear':
            xyz = transform.insert_frame(xyz, n_frame)
            rst = True
        else:
            xyz, rst = transform.prevent_collision_insert_frame_ignore_time(xyz, n_frame, dis=dis)

        if not self.running:
            return {'status': 'interrupted'}

        scores = utils.collision_detection(xyz, dis)
        if not self.running:
            return {'status': 'interrupted'}
        dic = transform.xyz_to_dict(xyz)

        if pth is not None:
            import json
            with open(pth, 'w', encoding='utf-8') as f:
                json.dump(dic, f)

        if not self.running:
            return {'status': 'interrupted'}
        self.running = False
        return {
            'status': 'succeed', 'stage': 'final',
            'result': dic, 'col_num': scores[0], 'col_rate': scores[1], 'min_dis': scores[2], 'rst': rst
        }

    def save(self, pth):
        import os
        if os.path.exists(pth):
            import shutil
            shutil.rmtree(pth)
        os.mkdir(pth)
        for i, seg in enumerate(self.segments):
            seg.save(fr"{pth}\seg{i}")

    def load(self, pth):
        import os
        self.segments = []
        for pt in os.listdir(pth):
            seg = path_solver.GradientPathSolver('rea', None, None, None)
            seg.load(fr"{pth}\{pt}")
            self.segments.append(seg)

    def stop(self):
        self.running = False

    def get_description(self):
        seg_num = len(self.segments)
        N = 0
        for seg in self.segments:
            if seg.N is not None:
                N += seg.N
        N += seg_num + 1
        if len(self.segments) > 0 and self.segments[0].xyz0 is not None:
            n = self.segments[0].xyz0.shape[0]
        else:
            n = None
        running = self.running
        return {
            'seg_num': int(seg_num),
            'N': int(N),
            'n': int(n),
            'running': running
        }

    def split(self, n_frame):
        xyz = self.get_complete_xyz()      # N, n, 3
        N, n, _ = xyz.shape
        new_frame_num = np.full([N - 1], (n_frame - N) // (N - 1))     # N-1
        rest = (n_frame - N) % (N - 1)
        if rest > 0:
            head = rest // 2
            end = rest - head
            new_frame_num[:head] += 1
            new_frame_num[-end:] += 1
        self.segments = [path_solver.GradientPathSolver(
            'rea', xyz[i, :, :], xyz[i+1, :, :], new_frame_num[i]
        ) for i in range(N-1)]


if __name__ == '__main__':
    xyz0 = utils.get_matrix_coordinates(xyz0=[0., 0., 0.], x_num=40, y_num=25, dx=2.)
    xyze = utils.get_final_coordinates(total_uav=1000, xyz0=[10., 500., 10.], dx=2.)

    solver = Solver(xyz0, xyze, init_mode='rea', N=10)

    # solver.match(max_iter=50)
    # solver.plot()
    # solver.save(r"./save/v3")

    solver.load(r"./save/v3")
    # solver.combine_segments(0, N=10)
    # solver.insert_intermediate_position(
    #     0, wh=300, vecs=np.array([[1., 0., 0.], [0., -1., 2.]]), x0=np.array([5., 100., 200.]),
    #     danger_duv=2., w_max=10., w_dis=100., lr=0.2, max_iter=1000, mode='div', feasible_solution=True
    # )

    # solver.plot()
    # solver.plot_example()
    # solver.save(r"./save/v3")

    # solver.solve_segment(
    #     seg_idx=1, danger_dx=2.5, danger_seg_dx=2.5, cross_danger_dis=3., danger_cross_seg_dis=3.,
    #     w_max=10., w_dis=10000., w_seg_dis=3000., w_cross_dis=1000., w_cross_seg_dis=1000., feasible_solution=False,
    #     max_iter=100, lr=0.1, mode='div', proj_mode='clip', N=20
    # )
    # solver.plot()
    # solver.save(r"./save/v3")

    _, score = solver.output_to_json(dis=1.5, n_frame=100, pth=r"./rst/v3.json", insert_mode='linear')
    print(score)


