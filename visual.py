import numpy as np
import matplotlib.pyplot as plt
import base64
import io


def scatter_3d(x, y, z, plot=True, ax=None, b64=False):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x, y, z, c='r', marker='o', s=10.)

    if b64:
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f'data:image/png;base64,{img_base64}'

    if plot:
        plt.show()
    return ax


def plot_platform(x0y0z0, normal_vector, h=5., plot=True, ax=None):

    b = x0y0z0[0] * normal_vector[0] + x0y0z0[1] * normal_vector[1] + x0y0z0[2] * normal_vector[2]

    if normal_vector[2] > 0.1:
        x = np.linspace(x0y0z0[0] - h, x0y0z0[0] + h, 50)
        y = np.linspace(x0y0z0[1] - h, x0y0z0[1] + h, 50)
        x, y = np.meshgrid(x, y)
        z = (b - normal_vector[0] * x - normal_vector[1] * y) / normal_vector[2]
    elif normal_vector[1] > 0.1:
        x = np.linspace(x0y0z0[0] - h, x0y0z0[0] + h, 50)
        z = np.linspace(x0y0z0[2] - h, x0y0z0[2] + h, 50)
        x, z = np.meshgrid(x, z)
        y = (b - normal_vector[0] * x - normal_vector[2] * z) / normal_vector[1]
    else:
        z = np.linspace(x0y0z0[2] - h, x0y0z0[2] + h, 50)
        y = np.linspace(x0y0z0[1] - h, x0y0z0[1] + h, 50)
        z, y = np.meshgrid(z, y)
        x = (b - normal_vector[2] * z - normal_vector[1] * y) / normal_vector[0]

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(x, y, z, cmap='viridis')
    # fig.colorbar(surf)
    if plot:
        plt.show()
    return ax


def plot_3d(x, y, z, plot=True, ax=None):
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

    ax.plot(x, y, z, label='3D Curve')

    if plot:
        plt.show()
    return ax


if __name__ == '__main__':
    plot_platform([0., 0., 0.], [0., 1., 1.], 5.)
