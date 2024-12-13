import numpy as np
import utils
import visual
import matplotlib.pyplot as plt


class IntermediateSolver:
    def __init__(self, xyz0, xyze, wh, vecs, x0, *args, **kwargs):

        # start position
        self.xyz0 = xyz0

        # end position
        self.xyze = xyze

        # position vector, not normal vector
        self.vecs = vecs / np.sum(vecs ** 2, axis=-1, keepdims=True) ** 0.5     # 2, 3

        # base position
        self.x0 = x0

        # random initialization
        # self.uv = (np.random.random([xyz0.shape[0], 2]) - 0.5) * wh
        self.uv = utils.inter_proj_init(xyz0, vecs, x0, wh)

        # uv bound
        self.max_uv = wh * 0.5 * np.ones([2])
        self.min_uv = -wh * 0.5 * np.ones([2])

    def save(self, pth):
        import os
        if not os.path.exists(pth):
            os.mkdir(pth)
        np.save(fr"{pth}/xyz0.npy", self.xyz0)
        np.save(fr"{pth}/xyze.npy", self.xyze)
        np.save(fr"{pth}/uv.npy", self.uv)
        np.save(fr"{pth}/vecs.npy", self.vecs)
        np.save(fr"{pth}/x0.npy", self.x0)
        np.save(fr"{pth}/max_uv.npy", self.max_uv)
        np.save(fr"{pth}/min_uv.npy", self.min_uv)

    def load(self, pth):
        self.xyz0 = np.load(fr"{pth}/xyz0.npy")
        self.xyze = np.load(fr"{pth}/xyze.npy")
        self.uv = np.load(fr"{pth}/uv.npy")
        self.vecs = np.load(fr"{pth}/vecs.npy")
        self.x0 = np.load(fr"{pth}/x0.npy")
        self.max_uv = np.load(fr"{pth}/max_uv.npy")
        self.min_uv = np.load(fr"{pth}/min_uv.npy")

    def solve(self, *args, **kwargs):
        pass

    def get_xyz(self, *args, **kwargs):
        return self.x0[None, :] + self.uv @ self.vecs

    def get_complete_xyz(self, *args, **kwargs):
        xyz = self.get_xyz()
        return np.stack([self.xyz0, xyz, self.xyze], axis=0)    # 3, n, 3

    def plot(self, *args, **kwargs):
        ax = None
        xyz = self.get_complete_xyz()

        for i in range(self.xyze.shape[0]):
            ax = visual.plot_3d(xyz[:, i, 0], xyz[:, i, 1], xyz[:, i, 2], False, ax)
        visual.scatter_3d(xyz[0, :, 0], xyz[0, :, 1], xyz[0, :, 2], False, ax)
        visual.scatter_3d(xyz[-1, :, 0], xyz[-1, :, 1], xyz[-1, :, 2], False, ax)

        plt.show()

    def plot_example(self):
        xyz = self.get_complete_xyz()
        visual.scatter_3d(xyz[:, ::200, 0], xyz[:, ::200, 1], xyz[:, ::200, 2])


class GradientIntermediateSolver(IntermediateSolver):

    def solve(self,
              danger_duv, w_max, w_dis,
              lr=0.2, max_iter=100, mode='add', feasible_solution=True,
              *args, **kwargs):

        assert mode in ['add', 'div']

        uv = self.uv        # n, 2
        w = self.vecs       # 2, 3
        b = self.x0         # 3
        xyz0 = self.xyz0    # n, 3
        xyze = self.xyze    # n, 3
        n, _ = uv.shape

        best_uv = np.copy(uv)
        best_rst = None

        for epoch in range(max_iter):
            x = uv @ w + b[None, :]      # n, 3
            dxyz0 = x - xyz0      # n, 3
            dxyze = x - xyze      # n, 3
            seg_xyz0 = np.sum(dxyz0 ** 2, axis=1) ** 0.5   # n
            seg_xyze = np.sum(dxyze ** 2, axis=1) ** 0.5   # n
            seg = seg_xyz0 + seg_xyze      # n
            avg_seg = np.mean(seg)
            max_idx = np.argmax(seg)
            max_seg = seg[max_idx]

            duv = uv[:, None, :] - uv[None, :, :]      # n, n, 2
            duv2 = np.sum(duv ** 2, axis=-1)    # n, n
            danger_idx = duv2 < danger_duv
            danger_idx[range(n), range(n)] = False    # n, n
            danger_num = np.sum(danger_idx.astype(float))
            danger_duv_sqrt = 0.

            if mode == 'add':
                if danger_num > 0:
                    danger_duv_sqrt = duv2[danger_idx] ** 0.5
                    duv_loss = -np.mean(danger_duv_sqrt)
                else:
                    duv_loss = -danger_duv
            else:
                if danger_num > 0:
                    danger_duv_sqrt = duv2[danger_idx] ** 0.5
                    duv_loss = np.mean(1. / (danger_duv_sqrt + 1e-30)) * danger_duv
                else:
                    duv_loss = 1.

            if feasible_solution:
                if best_rst is None:
                    best_rst = [avg_seg, max_seg]
                else:
                    if danger_num == 0 and [avg_seg, max_seg] < best_rst:
                        best_rst = [avg_seg, max_seg]
                        best_uv = np.copy(uv)

            loss = avg_seg + w_max * max_seg + w_dis * duv_loss
            # print(f"epoch: {epoch}, loss: {loss:.2f}, avg_seg: {avg_seg:.2f}, "
            #       f"max_seg: {max_seg:.2f}, duv: {duv_loss:.2f}, duv_num: {int(danger_num)}")
            yield {
                'status': 'succeed',
                'epoch': epoch,
                'loss': loss,
                'avg_seg': avg_seg,
                'max_seg': max_seg,
                'duv': duv_loss,
                'danger_num': danger_num
            }

            grad_avg = dxyz0 @ w.T / (seg_xyz0[:, None] + 1e-10) + dxyze @ w.T / (seg_xyze[:, None] + 1e-10)  # n, 2
            grad_avg *= 1. / n
            grad_avg[max_idx] += w_max * grad_avg[max_idx] * n

            if danger_num > 0:
                grad_duv = np.zeros([n, n, 2])
                grad_duv[danger_idx, :] = -duv[danger_idx, :]
                if mode == 'add':
                    grad_duv[danger_idx, :] /= (danger_duv_sqrt[:, None] + 1e-30)
                else:
                    grad_duv[danger_idx, :] /= 2 * (danger_duv_sqrt[:, None] ** 3 + 1e-30)
                grad_duv = np.sum(grad_duv, axis=1) * danger_duv  # n, 2
            else:
                grad_duv = 0.

            grad = grad_avg + w_dis / (danger_num + 1e-30) * grad_duv

            grad = np.clip(grad, -5, 5)
            uv -= lr * grad
            uv[:, 0] = np.clip(uv[:, 0], self.min_uv[0], self.max_uv[0])
            uv[:, 1] = np.clip(uv[:, 1], self.min_uv[1], self.max_uv[1])

        if feasible_solution:
            self.uv = best_uv
        else:
            self.uv = uv


if __name__ == '__main__':
    xyz0 = utils.get_matrix_coordinates([0., 0., 0.], 10, 10, 2.)
    xyze = utils.get_final_coordinates(100, [0., 100., 20.], 2.)

    solver = GradientIntermediateSolver(xyz0, xyze, 100., np.array([[1., 0., 0.], [0., -1., 1.]]), np.array([10., 50., 40.]))

    solver.solve(2., 10., 10., max_iter=100, mode='div')

    solver.plot()
    solver.plot_example()



