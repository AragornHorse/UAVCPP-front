import numpy as np


def get_matrix_coordinates(xyz0, x_num, y_num, dx):
    """
        square matrix with z = 0
    """
    xs = np.linspace(
        xyz0[0],
        xyz0[0] + (x_num - 1) * dx,
        num=x_num
    )
    ys = np.linspace(
        xyz0[1],
        xyz0[1] + (y_num - 1) * dx,
        num=y_num
    )
    x, y = np.meshgrid(xs, ys)
    x = x.reshape([-1])
    y = y.reshape([-1])
    sites = np.stack([x, y, np.full_like(x, fill_value=xyz0[2])], axis=-1)
    return sites


def get_final_coordinates(total_uav, xyz0, dx, outer_uav_rate=0.6, hdw=1.5, inner_hdw=0.6, dot_dh=0.7):
    """
        y = y0
    """
    half_out_num = (total_uav * outer_uav_rate + 1.) // 2
    inner_num = total_uav - 2 * half_out_num
    out_w_num = half_out_num // (hdw + 1.)
    out_h_num = half_out_num - out_w_num

    inner_w_num = inner_num / (inner_hdw + 1.) // 3
    inner_hs_num = inner_num - inner_w_num * 3
    inner_h_num = (inner_hs_num + 2.) // (2. + dot_dh)
    inner_dot_num = inner_hs_num - 2 * inner_h_num

    half_out_num = int(half_out_num)
    out_w_num = int(out_w_num)
    out_h_num = int(out_h_num)
    inner_dot_num = int(inner_dot_num)
    inner_h_num = int(inner_h_num)
    inner_w_num = int(inner_w_num)

    sites = np.zeros([total_uav, 3])
    out_w_xs = np.linspace(xyz0[0], xyz0[0] + (out_w_num - 1) * dx, out_w_num)
    out_h_zs = np.linspace(xyz0[2], xyz0[2] + (out_h_num - 1) * dx, out_h_num)
    sites[:, 1] = xyz0[1]

    # ----
    # ----
    sites[:out_w_num, 0] = out_w_xs
    sites[:out_w_num, 2] = xyz0[2]
    sites[out_w_num: out_w_num * 2, 0] = out_w_xs
    sites[out_w_num: out_w_num * 2, 2] = xyz0[2] + xyz0[2] + out_h_num * dx

    #  |   |
    #  |   |
    sites[out_w_num * 2: out_w_num * 2 + out_h_num, 2] = out_h_zs
    sites[out_w_num * 2: out_w_num * 2 + out_h_num, 0] = xyz0[0]
    sites[out_w_num * 2 + out_h_num: half_out_num * 2, 2] = out_h_zs
    sites[out_w_num * 2 + out_h_num: half_out_num * 2, 0] = xyz0[0] + out_w_num * dx

    #  --
    #  --
    #  --
    out_num = half_out_num * 2
    h = inner_h_num * dx
    x0 = xyz0[0] + out_w_num * dx / 2 - inner_w_num * dx / 2
    xs = np.linspace(x0, x0 + (inner_w_num - 1) * dx, inner_w_num)
    sites[out_num: out_num + inner_w_num, 0] = xs
    sites[out_num + inner_w_num: out_num + 2 * inner_w_num, 0] = xs
    sites[out_num + 2 * inner_w_num: out_num + 3 * inner_w_num, 0] = xs
    mid_z = xyz0[2] + out_h_num / 2 * dx
    sites[out_num: out_num + inner_w_num, 2] = mid_z - h
    sites[out_num + inner_w_num: out_num + 2 * inner_w_num, 2] = mid_z
    sites[out_num + 2 * inner_w_num: out_num + 3 * inner_w_num, 2] = mid_z + h

    # |
    # |
    x0 = xyz0[0] + out_w_num * dx / 2
    z0 = mid_z - h
    idx = out_num + 3 * inner_w_num
    sites[idx: idx + inner_h_num * 2, 2] = np.linspace(
        z0, z0 + (inner_h_num * 2 - 1) * dx, inner_h_num * 2
    )
    sites[idx: idx + inner_h_num * 2, 0] = x0

    # .
    idx = idx + inner_h_num * 2
    x = x0 + inner_w_num * dx / 4
    sites[idx:, 2] = np.linspace(z0, z0 + (inner_dot_num - 1) * dx, inner_dot_num)
    sites[idx:, 0] = x

    return sites


def get_platforms(N, xyz0, xyze):
    """
        get N platforms
    """
    xyz0 = np.mean(xyz0, axis=0)
    xyze = np.mean(xyze, axis=0)
    xyz = np.zeros([N, 3])
    vecs = np.zeros([N, 3])
    vecs[:, 1] = np.linspace(1 / N, 1 - 1 / N, N)
    vecs[:, 2] = np.linspace(1 - 1 / N, 1 / N, N)
    vecs = vecs / np.sum(vecs ** 2, axis=1, keepdims=True) ** 0.5
    xyz[:, :] = np.array([0., xyze[1], xyz0[2]])[None, :]
    return xyz, vecs


def project(xyzs, vecs, xyz0s):
    """
        project xyzs to platforms
    """
    N = xyzs.shape[0]
    xyz = np.copy(xyzs)
    bs = (xyz0s[:, None, :] @ vecs[:, :, None])[:, 0, 0]
    for i in range(N):
        vec = vecs[i]
        b = bs[i]
        xyz[i, :, :] = xyz[i, :, :] - \
                       (xyz[i, :, :] @ vec[:, None] - b)[:, :] / (vec[None, :] @ vec[:, None])[0, :] * vec[None, :]
    return xyz


def intersect(xyzs, vecs, xyz0s):
    n = xyzs.shape[1]
    N = vecs.shape[0]
    dis = np.sum(vecs[None, :, None, :] * (xyzs[:, None, :, :] - xyz0s[None, :, None, :]), axis=-1) > 0.   # N+2, N, n
    xyz = np.zeros([N, n, 3])
    idx = np.argmax(dis, axis=0)   # N, n
    for plat in range(N):
        x1 = xyzs[idx[plat] - 1, range(n), :]    # n, 3
        x2 = xyzs[idx[plat], range(n), :]        # n, 3
        x0 = xyz0s[plat, :]              # 3
        vec = vecs[plat, :]              # 3
        t = (x2 - x0[None, :]) @ vec[:, None] / ((x2 - x1) @ vec[:, None] + 1e-100)   # n, 1
        xyz[plat, :, :] = x1 * t + (1 - t) * x2
    return xyz


def dynamic_projection(xyzs):
    N = xyzs.shape[0]
    xyz_mean = np.mean(xyzs, axis=1, keepdims=True)    # N, 1, 3
    xyz_cen = xyzs - xyz_mean     # N, n, 3
    cov = xyz_cen.transpose([0, 2, 1]) @ xyz_cen    # N, 3, 3
    eig, vec = np.linalg.eig(cov)           # N, 3      N, 3, 3
    eig[eig == 0] = 1e30
    vec_idx = np.argmin(eig, axis=1)        # N
    vecs = vec[range(N), :, vec_idx]         # N, 3
    return project(xyzs, vecs, xyz_mean[:, 0, :])


def reallocate(xyzs):
    N = xyzs.shape[0] - 2
    n = xyzs.shape[1]
    dis = np.sum((xyzs[1:] - xyzs[:-1]) ** 2, axis=-1) ** 0.5   # N+1, n
    avg_dis = np.mean(dis, axis=0)     # n
    rate = dis / avg_dis[None, :]        # N+1, n
    rate[-1] -= 1e-3
    new_xyz = np.zeros([N, n, 3])
    for uav in range(n):
        k = 0
        t = 1.
        for i in range(N+1):
            rat = rate[i, uav]
            while t < rat and k < N:
                rat -= t
                new_xyz[k, uav, :] = (rat * xyzs[i, uav, :] + (rate[i, uav] - rat) * xyzs[i+1, uav, :]) / rate[i, uav]
                k += 1
                t = 1.
            t -= rat
    return new_xyz


def clip_reallocate(xyzs, max_dis=None):
    N, n, _ = xyzs.shape
    N -= 2
    dx = xyzs[1:] - xyzs[:-1]  # N+1, n, 3
    dis2 = np.sum(dx * dx, axis=-1)  # N+1, n

    # default max_dis: proportional to the average length of the longest path
    if max_dis is None:
        dis = dis2 ** 0.5
        dis = np.sum(dis, axis=0)       # n
        max_dis = np.max(dis) / (N + 2) * 1.5

    too_far = dis2 > max_dis ** 2      # N+1, n
    if not np.any(too_far):
        return xyzs[1:-1]
    else:
        new_xyz = np.copy(xyzs[1:-1])    # N, n, 3
        need_rea = np.nonzero(np.any(too_far, axis=0))[0]
        for uav in need_rea:
            uav_dis = dis2[:, uav] ** 0.5    # N+1
            dis0 = np.copy(uav_dis)
            uav_full = too_far[:, uav]       # N+1
            rest_dis = np.sum(uav_dis[uav_full] - max_dis)
            can_add = max_dis - uav_dis[~uav_full]    # n_
            to_add = can_add / np.sum(can_add) * rest_dis   # n_
            uav_dis[uav_full] = max_dis
            uav_dis[~uav_full] += to_add
            xyz0 = xyzs[:, uav, :]               # N+2, 3
            xn = np.zeros([N+2, 3])
            xn[0] = xyz0[0]
            xn[-1] = xyz0[-1]
            u = 1
            k = 0
            rst_d = dis0[0]
            for i in range(N):
                d = uav_dis[i]
                while d > rst_d:
                    d -= rst_d
                    k += 1
                    rst_d = dis0[k]
                x0 = xyz0[k]
                x1 = xyz0[k+1]
                t = d / dis0[k]
                rst_d -= d
                x = x0 * (1 - t) + x1 * t
                xn[u] = x
                u += 1
            new_xyz[:, uav, :] = xn[1:-1]
        return new_xyz


def collision_detection(xyzs, dis):
    N, n, _ = xyzs.shape
    dxx = np.sum((xyzs[:, :, None, :] - xyzs[:, None, :, :]) ** 2, axis=-1)
    col = dxx < dis ** 2
    col[:, range(n), range(n)] = False
    col_num = np.sum(col.astype(float))
    col_rate = col_num / (N * n * n)
    if col_num > 0.:
        min_dis = np.min(dxx[col])
    else:
        min_dis = None
    return col_num, col_rate, min_dis


def linear_insert(xyz0, xyze, N):
    n = xyz0.shape[0]
    xyz = np.zeros([N, n, 3])
    for i in range(n):
        xyz[:, i, 0] = np.linspace(
            xyz0[i, 0] * 0.9 + 0.1 * xyze[i, 0], xyz0[i, 0] * 0.1 + 0.9 * xyze[i, 0], N
        )
        xyz[:, i, 1] = np.linspace(
            xyz0[i, 1] * 0.9 + 0.1 * xyze[i, 1], xyz0[i, 1] * 0.1 + 0.9 * xyze[i, 1], N
        )
        xyz[:, i, 2] = np.linspace(
            xyz0[i, 2] * 0.9 + 0.1 * xyze[i, 2], xyz0[i, 2] * 0.1 + 0.9 * xyze[i, 2], N
        )
    return xyz


def project_init(vecs, xyz0s, xyz0, xyze):
    N = vecs.shape[0]
    xyz = linear_insert(xyz0, xyze, N)
    xyz = project(xyz, vecs, xyz0s)
    return xyz


def intersect_init(vecs, xyz0s, xyz0, xyze):
    N = vecs.shape[0]
    xyz = linear_insert(xyz0, xyze, N)
    xyz = intersect(np.concatenate([xyz0[None, ...], xyz, xyze[None, ...]]), vecs, xyz0s)
    return xyz


def reallocate_init(N, xyz0, xyze):
    xyz = linear_insert(xyz0, xyze, N)
    xyz = reallocate(np.concatenate([xyz0[None, ...], xyz, xyze[None, ...]]))
    return xyz


def get_vecs_from_norm_vec(vec):
    if not (vec[0] == vec[1] and vec[1] == vec[2]):
        x1 = np.cross(vec, np.ones([3]))
    else:
        x1 = np.cross(vec, np.array([0., 1., 1.]))
    x2 = np.cross(vec, x1)
    x1 = x1 / np.sum(x1 * x1) ** 0.5
    x2 = x2 / np.sum(x2 * x2) ** 0.5
    return np.stack([x1, x2], axis=0)      # 2, 3


def inter_proj_init(xyz, vecs, x0, wh):
    dx = xyz - x0[None, :]         # n, 3
    vecs = vecs / np.sum(vecs ** 2, axis=-1, keepdims=True) ** 0.5   # 2, 3
    uv = dx @ vecs.T        # n, 2
    max_uv = np.max(uv, axis=0, keepdims=True)
    min_uv = np.min(uv, axis=1, keepdims=True)
    uv = (uv - 0.5 * (min_uv + max_uv))
    if np.any(max_uv - min_uv > wh):
        uv = uv / (max_uv - min_uv + 1e-10) * wh
    return uv


if __name__ == '__main__':
    import visual
    import matplotlib.pyplot as plt

    x0 = get_matrix_coordinates([0., 0., 0.], 10, 10, 1.)
    xe = get_final_coordinates(100, [0., 10., 10.], 1.)

    xyzs, vecs = get_platforms(
        5,
        x0,
        xe
    )

    xyz = project_init(vecs, xyzs, x0, xe)

    xyz = clip_reallocate(xyz)

    xyz = np.concatenate([x0[None, :], xyz, xe[None, :]], 0)
    ax = None

    for i in range(0, xyz.shape[1], 10):
        ax = visual.plot_3d(xyz[:, i, 0], xyz[:, i, 1], xyz[:, i, 2], False, ax)

    plt.show()

    visual.scatter_3d(xyz[:, ::50, 0], xyz[:, ::50, 1], xyz[:, ::50, 2], True)
