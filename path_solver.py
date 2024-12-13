import numpy as np
import utils
import visual
import matplotlib.pyplot as plt


class PathSolver:
    def __init__(self, init_mode, xyz0, xyze, N, *args, **kwargs):
        # key point number
        self.N = N

        # initial position
        self.xyz0 = xyz0

        # final position
        self.xyze = xyze

        # key points
        self.xyz = None

        # normal vectors of platforms
        self.vecs = None

        # a position on platform
        self.xyz0s = None

        assert init_mode in ['rea', 'inter', 'proj']
        self.init_mode = init_mode

    def initial_xyz(self):
        if self.init_mode in ['inter', 'proj']:
            if self.vecs is None:
                self.xyz0s, self.vecs = utils.get_platforms(self.N, self.xyz0, self.xyze)
        if self.init_mode == 'inter':
            self.xyz = utils.intersect_init(self.vecs, self.xyz0s, self.xyz0, self.xyze)
        elif self.init_mode == 'proj':
            self.xyz = utils.project_init(self.vecs, self.xyz0s, self.xyz0, self.xyze)
        else:
            self.xyz = utils.reallocate_init(self.N, self.xyz0, self.xyze)

    def collision_detection(self, dis):
        col_num, col_rate, min_dis = utils.collision_detection(self.get_complete_xyz(), dis)
        print(f"col_num: {col_num}, col_rate: {col_rate}, min_dis: {min_dis}")

    def solve(self, *args, **kwargs):
        pass

    def get_complete_xyz(self):
        if self.xyz is None:
            self.initial_xyz()
        return np.concatenate([self.xyz0[None, :, :], self.xyz, self.xyze[None, :, :]], axis=0)

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

    def save(self, pth):
        import os
        if not os.path.exists(pth):
            os.mkdir(pth)
        np.save(rf"{pth}\N.npy", self.N)
        np.save(rf"{pth}\xyz0.npy", self.xyz0)
        np.save(rf"{pth}\xyze.npy", self.xyze)
        np.save(rf"{pth}\xyz.npy", self.xyz)
        np.save(rf"{pth}\vecs.npy", self.vecs)
        np.save(rf"{pth}\xyz0s.npy", self.xyz0s)
        np.save(rf"{pth}\init_mode.npy", self.init_mode)

    def load(self, pth):
        self.N = np.load(rf"{pth}\N.npy")
        self.xyz0 = np.load(rf"{pth}\xyz0.npy")
        self.xyze = np.load(rf"{pth}\xyze.npy")
        self.xyz = np.load(rf"{pth}\xyz.npy")
        self.vecs = np.load(rf"{pth}\vecs.npy", allow_pickle=True)
        self.xyz0s = np.load(rf"{pth}\xyz0s.npy", allow_pickle=True)
        self.init_mode = np.load(rf"{pth}\init_mode.npy", allow_pickle=True)


class GradientPathSolver(PathSolver):

    def solve(self,
              danger_dx, danger_seg_dx, cross_danger_dis, danger_cross_seg_dis,
              w_max, w_dis, w_seg_dis, w_cross_dis, w_cross_seg_dis,
              max_iter=100, lr=0.5, mode='add', proj_mode='proj', feasible_solution=False,
              *args, **kwargs):

        assert mode in ['add', 'div']
        assert proj_mode in ['proj', 'inter', 'rea', 'dyn', 'clip']

        if self.xyz is None:
            self.initial_xyz()

        yield {
            'stage': 'initial',
            'status': 'succeed'
        }

        xyz = self.get_complete_xyz()    # N+2, n, 3
        N = xyz.shape[0] - 2
        n = xyz.shape[1]

        fea_xyz = np.copy(xyz)

        for i in range(max_iter):
            # x_{i+1}^{k} - x_{i}^{k}
            dxyz = xyz[1:, ...] - xyz[:-1, ...]   # N+1, n, 3
            ddxyz = dxyz[1:] - dxyz[:-1]          # N, n, 3

            # average and max segment length
            seg_len_2 = np.sum(dxyz ** 2, axis=-1)
            seg_len = seg_len_2 ** 0.5  # N+1, n
            pth_len = np.sum(seg_len, axis=0)  # n
            avg_len = np.mean(pth_len)
            max_idx = np.argmax(pth_len)
            max_len = pth_len[max_idx]

            # x_{i}^{m} - x_{i}^{n}
            dx_all = xyz[:, :, None, :] - xyz[:, None, :, :]   # N+2, n, n, 3
            dx = dx_all[1:-1, ...]            # N, n, n, 3

            # average distance on the same platform
            dis = np.sum(dx ** 2, axis=-1)  # N, n, n
            is_danger = dis < danger_dx ** 2           # N, n, n
            is_danger[:, range(n), range(n)] = False
            if mode == 'add':
                dis_sqrt = dis[is_danger] ** 0.5
                danger_num = np.sum(is_danger.astype(float))
                if danger_num > 0:
                    danger_avg_dis = np.mean(dis_sqrt)
                else:
                    danger_avg_dis = danger_dx
            else:
                dis_sqrt = dis[is_danger] ** 0.5
                inv_dis_sqrt = 1. / (dis_sqrt + 1e-10)
                danger_num = np.sum(is_danger.astype(float))
                if danger_num > 0:
                    danger_avg_dis = - danger_dx * np.mean(inv_dis_sqrt)
                else:
                    danger_avg_dis = -1.

            # parallel distance between two segments
            dx_cross_dot = np.sum(dx_all[:-1] * dx_all[1:], axis=-1)  # N+1, n, n
            cross = dx_all[1:] - dx_all[:-1]
            dx_cross_len = np.sum(cross ** 2, axis=-1)  # N+1, n, n
            seg_dx = dx_cross_dot + 1 / 3 * dx_cross_len  # N+1, n, n
            danger_seg_idx = seg_dx < danger_seg_dx ** 2
            danger_seg_idx[:, range(n), range(n)] = False
            danger_seg_num = np.sum(danger_seg_idx.astype(float))
            if mode == 'add':
                seg_dx[danger_seg_idx] **= 0.5        # N+1, n, n
                if danger_seg_num > 0:
                    danger_avg_seg_dis = np.mean(seg_dx[danger_seg_idx])
                else:
                    danger_avg_seg_dis = danger_seg_dx
            else:
                seg_dx_sqrt = seg_dx[danger_seg_idx] ** 0.5
                inv_seg_dx_sqrt = 1. / (seg_dx_sqrt + 1e-10)
                if danger_seg_num > 0:
                    danger_avg_seg_dis = - danger_seg_dx * np.mean(inv_seg_dx_sqrt)
                else:
                    danger_avg_seg_dis = - 1.

            # distance between point and segments
            cross_dis = - np.sum(ddxyz[:, None, :, :] * dx, axis=-1)   # N, n, n
            cross_dis += 2 * dis
            cross_dis += 1 / 3 * (seg_len[:-1] ** 2 + seg_len[1:] ** 2)[:, None, :]
            cross_dis /= 2
            danger_cross = cross_dis < cross_danger_dis ** 2
            cross_sqrt = cross_dis[danger_cross] ** 0.5            # N, n, n
            danger_cross_num = np.sum(danger_cross.astype(float))
            if mode == 'add':
                if danger_cross_num > 0.:
                    cross_loss = np.mean(cross_sqrt)
                else:
                    cross_loss = cross_danger_dis
            else:
                if danger_cross_num > 0.:
                    cross_loss = - np.mean(cross_danger_dis / cross_sqrt)
                else:
                    cross_loss = - 1.

            # cross distance between two segments
            cross_d2 = np.sum((dxyz[:, :, None] - dxyz[:, None, :]) ** 2, axis=-1)        # N+1, n, n
            cross_seg_dis = 1 / 12 * ((seg_len_2[1:] + seg_len[:-1])[:, :, None] + \
                            (seg_len_2[1:] + seg_len[:-1])[:, None, :]) + \
                            dx_cross_dot[1:] + dx_cross_dot[:-1] + \
                            1 / 4 * (cross_d2[1:] + cross_d2[:-1])
            cross_seg_dis /= 2
            danger_cross_seg = cross_seg_dis < danger_cross_seg_dis ** 2
            danger_cross_seg_num = np.sum(danger_cross_seg.astype(float))
            danger_cross_seg_sqrt = cross_seg_dis[danger_cross_seg] ** 0.5
            if mode == 'add':
                if danger_cross_seg_num > 0.:
                    loss_cross_seg = np.mean(danger_cross_seg_sqrt)
                else:
                    loss_cross_seg = danger_cross_seg_dis
            else:
                if danger_cross_seg_num > 0.:
                    loss_cross_seg = - danger_cross_seg_dis * np.mean(1. / (danger_cross_seg_sqrt + 1e-10))
                else:
                    loss_cross_seg = - 1.

            if feasible_solution:
                if danger_num == 0:
                    fea_xyz = np.copy(xyz)

            loss = avg_len + w_max * max_len\
                   - w_dis * danger_avg_dis - w_seg_dis * danger_avg_seg_dis\
                   - w_cross_dis * cross_loss - w_cross_seg_dis * loss_cross_seg

            yield {
                'stage': 'solve',
                'status': 'succeed',
                'epoch': i,
                'loss': loss,
                'avg_len': avg_len,
                'max_len': max_len,
                'dis_num': danger_num,
                'seg_num': danger_seg_num,
                'cross_num': danger_cross_num,
                'cross_seg_num': danger_cross_seg_num
            }

            # segment length gradient
            grad_avg_len = dxyz / seg_len[..., None]
            grad_avg_len = 0.5 * (grad_avg_len[:-1] - grad_avg_len[1:])   # N, n, 3
            grad_max_len = np.zeros([N, n, 3])
            grad_max_len[:, max_idx, :] = grad_avg_len[:, max_idx, :]    # N, n, 3

            # repulsion between two points
            if mode == 'add':
                if danger_num > 0:
                    grad_danger_dis = np.zeros([N, n, n, 3])   # N, n, n, 3
                    grad_danger_dis[is_danger, :] = dx[is_danger, :] / (dis_sqrt[:, None] + 1e-100)
                    grad_danger_dis = 0.5 * np.sum(grad_danger_dis, axis=2)   # N, n, 3
                else:
                    grad_danger_dis = 0.
            else:
                if danger_num > 0:
                    grad_danger_dis = np.zeros([N, n, n, 3])  # N, n, n, 3
                    grad_danger_dis[is_danger, :] = dx[is_danger, :] * (inv_dis_sqrt ** 3)[:, None]
                    grad_danger_dis = 0.5 * danger_dx * np.sum(grad_danger_dis, axis=2)  # N, n, 3
                else:
                    grad_danger_dis = 0.

            # parallel repulsion between two segments
            if mode == 'add':
                if danger_seg_num > 0:
                    grad_seg_dx = np.zeros([N+1, n, n, 3])
                    w = np.zeros([N + 1, n, n])
                    w[danger_seg_idx] = 1. / (seg_dx[danger_seg_idx] + 1e-100)
                    grad_seg_dx[danger_seg_idx] = cross[danger_seg_idx] * w[danger_seg_idx, None]  # N+1, n, n, 3
                    grad_seg_dx = 1 / 3 * (grad_seg_dx[1:] - grad_seg_dx[:-1])  # N, n, n, 3
                    grad_seg_dx += dx * (w[1:] + w[:-1])[..., None]
                    grad_seg_dx = np.sum(grad_seg_dx, axis=2) * 0.5
                else:
                    grad_seg_dx = 0.
            else:
                if danger_seg_num > 0:
                    grad_seg_dx = np.zeros([N + 1, n, n, 3])
                    w = np.zeros([N + 1, n, n])
                    w[danger_seg_idx] = inv_seg_dx_sqrt ** 3
                    grad_seg_dx[danger_seg_idx] = cross[danger_seg_idx] * w[danger_seg_idx, None]  # N+1, n, n, 3
                    grad_seg_dx = 1 / 3 * (grad_seg_dx[1:] - grad_seg_dx[:-1])  # N, n, n, 3
                    grad_seg_dx += dx * (w[1:] + w[:-1])[..., None]
                    grad_seg_dx = np.sum(grad_seg_dx, axis=2) * danger_seg_dx
                else:
                    grad_seg_dx = 0.

            # repulsion from segment to point
            if mode == 'add':
                if danger_cross_num > 0.:
                    grad_cross = np.zeros([N, n, n, 3])
                    grad_cross[danger_cross, :] = 2 * dx[danger_cross, :] + (xyz[1:-1, :, None, :] - xyz[:-2, None, :, :]
                                                  + xyz[1:-1, :, None, :] - xyz[2:, None, :, :])[danger_cross, :]
                    grad_cross[danger_cross, :] /= (cross_sqrt[:, None] + 1e-30)
                    grad_cross = np.sum(grad_cross, axis=2) * 0.5
                else:
                    grad_cross = 0.
            else:
                if danger_cross_num > 0.:
                    grad_cross = np.zeros([N, n, n, 3])
                    grad_cross[danger_cross, :] = 2 * dx[danger_cross, :] + (xyz[1:-1, :, None, :] - xyz[:-2, None, :, :]
                                                    + xyz[1:-1, :, None, :] - xyz[2:, None, :, :])[danger_cross, :]
                    grad_cross[danger_cross, :] /= (cross_sqrt[:, None] ** 3 + 1e-30)
                    grad_cross = np.sum(grad_cross, axis=2) * cross_danger_dis
                else:
                    grad_cross = 0.

            # cross repulsion between two segments
            if mode == 'add':
                if danger_cross_seg_num > 0.:
                    grad_cross_seg = np.zeros([N, n, n, 3])
                    grad_cross_seg[danger_cross_seg] = (2 / 3 * (-ddxyz)[:, :, None, :] +
                                                        dx_all[2:] + dx_all[:-2] + 0.5 *
                                     ddxyz[:, None, :, :])[danger_cross_seg]      # N, n, n, 3
                    grad_cross_seg[danger_cross_seg] /= (danger_cross_seg_sqrt + 1e-30)[:, None]
                    grad_cross_seg = np.sum(grad_cross_seg, axis=2) * 0.25
                else:
                    grad_cross_seg = 0.
            else:
                if danger_cross_seg_num > 0.:
                    grad_cross_seg = np.zeros([N, n, n, 3])
                    grad_cross_seg[danger_cross_seg] = (2 / 3 * (-ddxyz)[:, :, None, :] +
                                                        dx_all[2:] + dx_all[:-2] + 0.5 *
                                                ddxyz[:, None, :, :])[danger_cross_seg]  # N, n, n, 3
                    grad_cross_seg[danger_cross_seg] /= (danger_cross_seg_sqrt ** 3 + 1e-30)[:, None]
                    grad_cross_seg = np.sum(grad_cross_seg, axis=2) * (danger_cross_seg_dis / 2)
                else:
                    grad_cross_seg = 0.

            grad = 1 / N * grad_avg_len +\
                       w_max * grad_avg_len -\
                       1 / (danger_num + 1e-30) * w_dis * grad_danger_dis - \
                       1 / (danger_seg_num + 1e-30) * w_seg_dis * grad_seg_dx - \
                       1 / (danger_cross_num + 1e-30) * w_cross_dis * grad_cross -\
                       1 / (danger_cross_seg_num + 1e-30) * w_cross_seg_dis * grad_cross_seg

            grad = np.clip(grad, -4., 4.)
            xyz[1:-1, ...] -= grad * lr
            if proj_mode == 'proj':
                xyz[1:-1, ...] = utils.project(xyz[1:-1, ...], self.vecs, self.xyz0s)
            elif proj_mode == 'inter':
                xyz[1:-1, ...] = utils.intersect(xyz, self.vecs, self.xyz0s)
            elif proj_mode == 'dyn':
                xyz[1:-1, ...] = utils.dynamic_projection(xyz[1:-1, ...])
            elif proj_mode == 'clip':
                xyz[1:-1, ...] = utils.clip_reallocate(xyz, None)
            else:
                xyz[1:-1, ...] = utils.reallocate(xyz)

            # print(
            #     f"iter: {i} >>> loss: {loss:.2f}, avg_len: {avg_len:.2f}, max_len: {max_len:.2f},"
            #     f" avg_dis_num: {danger_avg_dis:.2f}, {int(danger_num)}, "
            #     f"seg_avg_num: {danger_avg_seg_dis:.2f}, {int(danger_seg_num)}, "
            #     f"cross_avg_num: {cross_loss: .2f}, {int(danger_cross_num)}, "
            #     f"cross_seg_num: {loss_cross_seg: .2f}, {int(danger_cross_seg_num)}"
            # )

        if feasible_solution:
            xyz = fea_xyz

        self.xyz = xyz[1:-1, ...]


if __name__ == '__main__':
    N = 10
    xyz0 = utils.get_matrix_coordinates([0., 0., 0.], 10, 10, 2.)
    xyze = utils.get_final_coordinates(100, [0., 100., 20.], 2.)

    solver = GradientPathSolver(init_mode='proj', xyz0=xyz0, xyze=xyze, N=N)

    solver.solve(
        2., 2., 3., 3., 10., 100., 100., 100., 100., max_iter=100, mode='div', proj_mode='clip'
    )

    solver.plot()
    solver.plot_example()
