import base64
import json
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image


def pre_img(img):
    avg = sum(sum(e) for e in img) / (24 * 22)
    bits = [[1 if val > avg else 0 for val in row] for row in img]
    return bits


def saturation(d):
    saturate = np.round(
        ((np.max(d, axis=1) - np.min(d, axis=1)) * 255) / np.max(d, axis=1)
    )
    img = saturate.reshape((40, 200))
    bls = [
        img[
            7 + 5 * (i % 2) + 1 : 35 - 5 * ((i + 1) % 2),
            (i + 1) * 25 + 2 : (i + 2) * 25 + 1,
        ]
        for i in range(6)
    ]
    return bls


def flatten(arr):
    return [val for sublist in arr for val in sublist]


def mat_mul(a, b):
    x, z, y = len(a), len(a[0]), len(b[0])
    product = [[0] * y for _ in range(x)]

    for i in range(x):
        for j in range(y):
            for k in range(z):
                product[i][j] += a[i][k] * b[k][j]

    return product


def mat_add(a, b):
    return [a[i] + b[i] for i in range(len(a))]


def max_soft(a):
    n = list(a)
    s = sum(np.exp(f) for f in n)
    n = [np.exp(f) / s for f in n]
    return n


HEIGHT = 40
WIDTH = 200


def solve(img):
    weights = None
    biases = None
    label_txt = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

    weights_path = Path(__file__).parent.parent / "constants" / "weights.json"
    with open(weights_path, "r") as f:
        data = json.load(f)
        weights = data["weights"]
        biases = data["biases"]

    img_data = img.convert("RGB").getdata()
    img_array = np.array(list(img_data))

    bls = saturation(img_array)
    out = ""

    for i in range(6):
        bls[i] = pre_img(bls[i])
        bls[i] = [flatten(bls[i])]
        bls[i] = mat_mul(bls[i], weights)
        bls[i] = mat_add(*bls[i], biases)
        bls[i] = max_soft(bls[i])
        index = bls[i].index(max(bls[i]))
        out += label_txt[index]

    return out


def solve_base64(img_base64: str) -> str:
    return solve(Image.open(BytesIO(base64.b64decode(img_base64))))
