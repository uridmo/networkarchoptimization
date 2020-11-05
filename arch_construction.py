import numpy as np
from scipy.optimize import fsolve


def displacement(d, q, s, nx, ny, x, y, dx, l1, l2, fun_angle, fun_height_2):
    dy = d[0]
    dl1 = fsolve(lambda dl: fun_height_2(l1 + dl, y - dy) - (x + dx), 0)[0]
    dl2 = fsolve(lambda dl: fun_height_2(l2 - dl, y - dy) - (s - x - dx), 0)[0]

    a1 = fun_angle(l1 + dl1 / 2)
    b1 = fun_angle(-(l1 + dl1 / 2))
    a2 = fun_angle(l2 - dl2 / 2)
    b2 = fun_angle(-(l2 - dl2 / 2))

    f1 = q * dl1 / (np.sin(a1) + np.cos(a1) * np.tan(b1))
    f2 = q * dl2 / (np.sin(a2) + np.cos(a2) * np.tan(b2))

    nx2 = nx - f1 * np.cos(a1) + f2 * np.cos(a2)
    ny2 = ny + f1 * np.sin(a1) + f2 * np.sin(a2)

    x3 = (dx / 2 * (ny / nx + ny2 / nx2) - dy) * 100
    return x3, nx2, ny2, dl1, dl2


def displacement_opt(d, q, s, nx, ny, x, y, dx, l1, l2, fun_angle, fun_height_2):
    x, nx2, ny2, dl1, dl2 = displacement(d, q, s, nx, ny, x, y, dx, l1, l2, fun_angle, fun_height_2)
    return x


def arch(N, X, r, s, l0, q, fun_angle, fun_height_2):
    nx_arr = np.zeros(len(X))
    ny_arr = np.zeros(len(X))
    y = np.zeros(len(X))
    l1 = np.zeros(len(X))
    l2 = np.zeros(len(X))
    dx = np.diff(X)

    nx_arr[0] = N
    y[0] = r
    l1[0] = l0
    l2[0] = l0
    d = [0.1]

    for i in range(len(X) - 1):
        def displacement_d(d): return displacement_opt(d, q, s, nx_arr[i], ny_arr[i], X[i], y[i], dx[i], l1[i], l2[i],
                                                       fun_angle, fun_height_2)

        d = fsolve(displacement_d, d, factor=0.1)
        [a, nx, ny, dl1, dl2] = displacement(d, q, s, nx_arr[i], ny_arr[i], X[i], dx[i], y[i], l1[i], l2[i], fun_angle,
                                             fun_height_2)
        y[i + 1] = y[i] - d
        l1[i + 1] = l1[i] + dl1
        l2[i + 1] = l2[i] - dl2
        nx_arr[i + 1] = nx
        ny_arr[i + 1] = ny
    dy = y[-1]
    return dy, y, nx_arr, ny_arr, l1, l2


def arch_opt(n, x, r, s, l0, q, fun_angle, fun_height_2):
    [dy, y, nx_arr, ny_arr, l1, l2] = arch(n, x, r, s, l0, q, fun_angle, fun_height_2)
    return dy


def parabolic_arch():
    arc = 0
    return arc


def circular_arch():
    arc = 0
    return arc


def continuous_arch(s, r, q, n, hangers):
    a_x = hangers['Position']
    angles = hangers['Angles']
    normal_force = q * s ** 2 / 8 / r
    x = np.linspace(s / 2, s, n+1)

    def fun_angle(p): return np.interp(p, a_x, angles)
    def fun_height(p, angle, h): return p + h / np.tan(angle)
    def fun_height_2(p, h): return fun_height(p, fun_angle(p), h)

    # Find start positions
    l0 = fsolve(lambda l: (fun_height_2(l, r) - s / 2), 0)
    a = fun_height_2(l0, r) - s / 2

    normal_force = fsolve(lambda n_x: arch_opt(n_x, x, r, s, l0, q, fun_angle, fun_height_2), normal_force)
    [dy, y, nx, ny, l1, l2] = arch(normal_force, x, r, s, l0, q, fun_angle, fun_height_2)

    x = np.linspace(0, s, 2*n).tolist()
    y = y.tolist()
    y = y[-1:1:-1]+y
    return x, y


def discrete_arch():
    arc = 0
    return arc





if __name__ == '__main__':
    aaa = 1
