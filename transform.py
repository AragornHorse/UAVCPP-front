import utils
import numpy as np


def xyz_to_dict(xyz):
    """
    :param xyz:   N, n, 3
    :return:      [[{}, ...], ...]
    """
    N, n, _ = xyz.shape
    rst = [
        [
            {
                'id': uid,
                'latitude': xyz[fid, uid, 0],
                'longitude': xyz[fid, uid, 1],
                'altitude': xyz[fid, uid, 2],
                'color': '#e6d3d0'
            }
            for uid in range(n)
        ]
        for fid in range(N)
    ]
    return rst


def insert_frame(xyz, n_frame):
    N, n, _ = xyz.shape
    if n_frame <= N:
        return xyz
    new_frame_num = np.full([N-1], (n_frame - N) // (N - 1))

    rest = (n_frame - N) % (N - 1)
    if rest > 0:
        head = rest // 2
        end = rest - head
        new_frame_num[:head] += 1
        new_frame_num[-end:] += 1

    new_xyz = np.zeros([n_frame, n, 3])
    new_xyz[-1, :, :] = xyz[-1, :, :]
    new_xyz_idx = 0

    for seg_idx in range(N-1):
        new_xyz[new_xyz_idx] = xyz[seg_idx]
        new_xyz_idx += 1
        new_num = new_frame_num[seg_idx]
        rate = 1. / (new_num + 1.)
        new_xyz[new_xyz_idx: new_xyz_idx + new_num, :, 0] = np.linspace(
            (1 - rate) * xyz[seg_idx, :, 0] + rate * xyz[seg_idx + 1, :, 0],
            rate * xyz[seg_idx, :, 0] + (1 - rate) * xyz[seg_idx + 1, :, 0],
            new_num
        )
        new_xyz[new_xyz_idx: new_xyz_idx + new_num, :, 1] = np.linspace(
            (1 - rate) * xyz[seg_idx, :, 1] + rate * xyz[seg_idx + 1, :, 1],
            rate * xyz[seg_idx, :, 1] + (1 - rate) * xyz[seg_idx + 1, :, 1],
            new_num
        )
        new_xyz[new_xyz_idx: new_xyz_idx + new_num, :, 2] = np.linspace(
            (1 - rate) * xyz[seg_idx, :, 2] + rate * xyz[seg_idx + 1, :, 2],
            rate * xyz[seg_idx, :, 2] + (1 - rate) * xyz[seg_idx + 1, :, 2],
            new_num
        )
        new_xyz_idx += new_num
    return new_xyz


def prevent_collision_insert_frame_ignore_time(xyz, n_frame, dis, alpha=0.2):
    N, n, _ = xyz.shape
    new_xyz = np.zeros([n_frame, n, 3])
    new_xyz[0, :, :] = xyz[0, :, :]
    tgt = np.ones([n], dtype=int)          # n
    dx = np.abs(xyz[1:, :, :] - xyz[:-1, :, :]).reshape([-1, 3])
    v = (alpha * np.max(dx, axis=0) + (1 - alpha) * np.mean(dx, axis=0)) * N / n_frame       # 3
    t = np.zeros([n])              # n
    dt = np.min(v[None, :] / np.abs(xyz[1, :, :] - xyz[0, :, :] + 1e-30), axis=1)  # n
    for fid in range(1, n_frame):
        sum_t = tgt + t
        order = np.argsort(sum_t)
        x = np.copy(new_xyz[fid - 1, :, :])  # n, 3
        for uav in order:
            arrived = False
            x0 = xyz[tgt[uav]-1, uav, :]        # 3
            x1 = xyz[np.clip(tgt[uav], 0, N-1), uav, :]
            tn = t[uav] + dt[uav]
            if tn >= 1:
                arrived = True
                tn = 1.
            xn = (1 - tn) * x0 + tn * x1        # 3
            dis = np.sum((x - xn[None, :]) ** 2, axis=-1)    # n
            col = dis < dis ** 2
            col[uav] = False
            if not np.any(col):
                x[uav, :] = xn
                if arrived:
                    t[uav] = 0.
                    tgt[uav] = np.clip(tgt[uav] + 1, 0, N)
                    if tgt[uav] < N:
                        dt[uav] = np.min(v / np.abs(xyz[tgt[uav], uav, :] - xyz[tgt[uav]-1, uav, :] + 1e-30))
                else:
                    t[uav] = tn
            else:
                continue
        new_xyz[fid] = x

    if not np.all(tgt == N) and alpha < 2.:
        return prevent_collision_insert_frame_ignore_time(xyz, n_frame, dis, alpha * 1.5)

    return new_xyz, not (alpha >= 2.)


if __name__ == '__main__':
    pass

