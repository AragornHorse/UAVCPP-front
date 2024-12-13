import numpy as np
import visual
import copy
import heapq
import matplotlib.pyplot as plt

test = True


def get_score(pth_len):
    """
        [max_len, avg_len, std_len]
    """
    rst = [np.max(pth_len), np.mean(pth_len), np.std(pth_len)]
    return rst


def is_in_domain(ori_to_final, domains):
    """
    :param ori_to_final:    [0, 1, 3, 2]
    :param domains:         [[1, 2], [1, 2], [3, 2]]
    :return:
    """
    for ori, final in enumerate(ori_to_final):
        if final not in domains[ori]:
            return False
    else:
        return True


def get_reverse_domain(num, domain):
    reverse_domain = [[] for _ in range(num)]
    for ori, finals in enumerate(domain):
        for final in finals:
            reverse_domain[final].append(ori)
    return reverse_domain


def clear_domain(domain, reverse_domain):
    """
        [[0, 1], [1]] -> [[0], [1]]
    """
    for i in reverse_domain:
        if len(i) == 0:
            return None, None
    one_final = set()
    one_ori = set()
    for ori, finals in enumerate(domain):
        if len(finals) == 1:
            one_final.add(ori)
    for final, oris in enumerate(reverse_domain):
        if len(oris) == 1:
            one_ori.add(final)
    if len(one_final) == 0 and len(one_ori) == 0:
        return domain, reverse_domain
    while len(one_final) > 0 or len(one_ori) > 0:
        if len(one_final) > 0:
            ori = one_final.pop()
            final = domain[ori][0]
            for o in reverse_domain[final]:
                if o != ori:
                    domain[o].remove(final)
                    if len(domain[o]) == 1:
                        one_final.add(o)
            reverse_domain[final] = [ori]
        else:
            final = one_ori.pop()
            if len(reverse_domain[final]) == 0:
                return None, None
            ori = reverse_domain[final][0]
            for f in domain[ori]:
                if f != final:
                    reverse_domain[f].remove(ori)
                    if len(reverse_domain[f]) == 1:
                        one_ori.add(f)
            domain[ori] = [final]
    return domain, reverse_domain


class Node:
    def __init__(self, dis, domain, solve=None, upper=None):
        self.dis = dis
        self.domain = domain   # [[1, 2, 3], [1, 2], [1], ...]
        self.reverse_domain = None
        self.domain, self.reverse_domain = clear_domain(self.domain, self.get_reverse_domain())
        self._lower = None
        self._upper = upper
        self._solve = solve
        self._min_dis = None
        self._max_dis = None
        self._reverse_min_dis = None

    def get_reverse_domain(self):
        if self.reverse_domain is not None:
            return self.reverse_domain
        else:
            self.reverse_domain = get_reverse_domain(self.dis.shape[0], self.domain)
            return self.reverse_domain

    def get_min_dis(self, reverse=False):
        if not reverse:
            if self._min_dis is not None:
                return self._min_dis
            else:
                dis = self.dis

                return np.array([np.min(dis[ori][finals]) for ori, finals in enumerate(self.domain)])
        else:
            if self._reverse_min_dis is not None:
                return self._reverse_min_dis
            else:
                reverse_domain = self.get_reverse_domain()
                return np.array([np.min(self.dis[oris, final]) for final, oris in enumerate(reverse_domain)])

    def get_max_dis(self):
        if self._max_dis is not None:
            return self._max_dis
        else:
            dis = self.dis
            return np.array([np.max(dis[ori][finals]) for ori, finals in enumerate(self.domain)])

    def get_lower(self):
        if self._lower is not None:
            return self._lower
        min_dis = self.get_min_dis(False)
        reverse_min_dis = self.get_min_dis(True)
        self._lower = [
            max([np.max(min_dis), np.max(reverse_min_dis)]),
            max([np.mean(min_dis), np.mean(reverse_min_dis)])
        ]
        return self._lower

    def split(self, split=True):
        """
            split: return node, and update self to (self - node)
            else: don't update self
        """

        for finals in self.domain:
            if len(finals) > 1:
                break
        else:
            return None

        min_dis = self.get_min_dis(False)
        max_dis = self.get_max_dis()
        scores = max_dis - min_dis
        total_num = self.dis.shape[0]

        cant_split = [i for i in range(self.dis.shape[0]) if len(self.domain[i]) == 1]
        scores[cant_split] = -1

        ori = np.argmax(scores)
        dis = np.full([total_num], self.get_max_dis()[ori] + 1.)
        dis[self.domain[ori]] = self.dis[ori, self.domain[ori]]
        final = np.argmin(dis)

        new_domain = copy.deepcopy(self.domain)
        for finals in new_domain:
            if final in finals:
                finals.remove(final)
        new_domain[ori] = [final]

        if split:
            self.domain[ori].remove(final)
            self.reverse_domain[final].remove(ori)
            self.domain, self.reverse_domain = clear_domain(self.domain, self.reverse_domain)
            self._lower = None
            self._min_dis = None
            self._max_dis = None
            self._reverse_min_dis = None

            solve = None
            upper = None

            if self._upper is not None:
                if is_in_domain(self._solve, new_domain):
                    solve = self._solve
                    upper = self._upper
                    self._solve = None
                    self._upper = None
                else:
                    solve = None
                    upper = None

            return Node(self.dis, new_domain, solve, upper)

        else:
            return Node(self.dis, new_domain)

    def get_upper(self):

        if self._upper is not None:
            return self._upper

        n = self.dis.shape[0]

        domain = copy.deepcopy(self.domain)
        reverse_domain = copy.deepcopy(self.get_reverse_domain())

        for _ in range(n):
            oris = [i for i in range(n) if len(domain[i]) > 1]
            if len(oris) == 0:
                break
            scores = np.full([n], fill_value=-1)
            for ori in oris:
                finals = domain[ori]
                scores[ori] = np.max(self.dis[ori, finals]) - np.min(self.dis[ori, finals])

            ori = np.argmax(scores)
            final = domain[ori][np.argmin(self.dis[ori, domain[ori]])]

            for f in domain[ori]:
                if f != final:
                    reverse_domain[f].remove(ori)
            domain[ori] = [final]
            domain, reverse_domain = clear_domain(domain, reverse_domain)

        self._solve = [i[0] for i in domain]
        pths = self.dis[range(self.dis.shape[0]), self._solve]
        self._upper = get_score(pths)
        return self._upper

    def get_solve(self):
        if self._solve is None:
            self.get_upper()
        return self._solve

    def __eq__(self, other):
        return self.get_lower() == other.get_lower()

    def __lt__(self, other):
        return self.get_lower() < other.get_lower()

    def __le__(self, other):
        return self.get_lower() <= other.get_lower()

    def __gt__(self, other):
        return self.get_lower() > other.get_lower()

    def __ge__(self, other):
        return self.get_lower() >= other.get_lower()


def match(ori_xyz, final_xyz, only_one_solve=False, max_iter=None):
    """
        which ori to which final
    :param ori_xyz:       n, 3
    :param final_xyz:     n, 3
    :param only_one_solve:     only return one solve
    :param max_iter:           max iter number
    :return:      best_loss, [solve1, solve2, ...], log(searched_space / total_space)
    """
    dis = np.sum((ori_xyz[:, None, :] - final_xyz[None, :, :]) ** 2, axis=-1) ** 0.5
    domain = [list(range(dis.shape[0])) for _ in range(dis.shape[0])]

    nodes = [Node(dis, domain)]
    rst = []

    # print(1)
    upper = nodes[0].get_upper()
    # print(2)
    i = 0

    r = nodes[0].get_solve()

    while len(nodes) > 0 and not (only_one_solve and len(rst) > 0) and not (max_iter is not None and i >= max_iter):
        i += 1
        # if i % 2 == 0:
        #     print(f"{i} iters")
        node = heapq.heappop(nodes)
        if node.domain is None:
            continue
        if node.get_lower() > upper:
            continue
        up = node.get_upper()
        if up < upper:
            upper = up
            r = node.get_solve()
        sub = node.split(True)
        if sub is None or sub.domain is None:
            rst.append(node)
        else:
            nodes.append(node)
            nodes.append(sub)
        yield upper, None, None

    if max_iter is None:
        yield upper, [r.get_solve() for r in rst], np.log(i) - dis.shape[0] * np.log(dis.shape[0])
    else:
        if not only_one_solve:
            yield upper, [r.get_solve() for r in nodes], None
        else:
            yield upper, [r], None


if __name__ == '__main__':

    ori = np.random.random([100, 3])
    final = np.random.random([100, 3])

    ori[:, -1] = 0.

    final[:, 0] = 5.
    final[:, -1] += 2.

    ax = visual.scatter_3d(ori[:, 0], ori[:, 1], ori[:, 2], False, None)
    visual.scatter_3d(final[:, 0], final[:, 1], final[:, 2], False, ax)

    upper, solves, log_rate = match(ori, final, only_one_solve=False, max_iter=10000)

    print(f"upper: {upper}")
    print(f"log_rate: {log_rate}")
    print(f"rst_num: {len(solves)}")

    for oi, fi in enumerate(solves[0]):
        o = ori[oi]
        f = final[fi]
        visual.plot_3d([o[0], f[0]], [o[1], f[1]], [o[2], f[2]], False, ax)

    plt.show()






