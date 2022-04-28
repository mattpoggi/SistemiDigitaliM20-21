import numpy as np
from PIL import Image
from PIL.JpegImagePlugin import convert_dict_qtables
from scipy.interpolate import interp1d


def log(*args, **kwargs):
    print("[SD]", *args, **kwargs)


def jpeg_quality_of(image, tnum=0, force_baseline=None):
    assert tnum == 0 or tnum == 1, 'Table number must be 0 or 1'

    if force_baseline is None:
        th_high = 32767
    elif force_baseline == 0:
        th_high = 32767
    else:
        th_high = 255

    h = np.asarray(convert_dict_qtables(image.quantization)[tnum]).reshape((8, 8))

    if tnum == 0:
        # This is table 0 (the luminance table):
        t = np.array(
            [[16, 11, 10, 16, 24, 40, 51, 61],
             [12, 12, 14, 19, 26, 58, 60, 55],
             [14, 13, 16, 24, 40, 57, 69, 56],
             [14, 17, 22, 29, 51, 87, 80, 62],
             [18, 22, 37, 56, 68, 109, 103, 77],
             [24, 35, 55, 64, 81, 104, 113, 92],
             [49, 64, 78, 87, 103, 121, 120, 101],
             [72, 92, 95, 98, 112, 100, 103, 99]])

    elif tnum == 1:
        # This is table 1 (the chrominance table):
        t = np.array(
            [[17, 18, 24, 47, 99, 99, 99, 99],
             [18, 21, 26, 66, 99, 99, 99, 99],
             [24, 26, 56, 99, 99, 99, 99, 99],
             [47, 66, 99, 99, 99, 99, 99, 99],
             [99, 99, 99, 99, 99, 99, 99, 99],
             [99, 99, 99, 99, 99, 99, 99, 99],
             [99, 99, 99, 99, 99, 99, 99, 99],
             [99, 99, 99, 99, 99, 99, 99, 99]])

    else:
        raise ValueError(tnum, 'Table number must be 0 or 1')

    h_down = np.divide((2 * h - 1), (2 * t))
    h_up = np.divide((2 * h + 1), (2 * t))
    if np.all(h == 1): return 100
    x_down = (h_down[h > 1]).max()
    x_up = (h_up[h < th_high]).min() if (h < th_high).any() else None
    if x_up is None:
        s = 1
    elif x_down > 1 and x_up > 1:
        s = np.ceil(50 / x_up)
    elif x_up < 1:
        s = np.ceil(50 * (2 - x_up))
    else:
        s = 50
    return s


def jpeg_qtableinv(stream, tnum=0, force_baseline=None):
    return jpeg_quality_of(Image.open(stream), tnum=tnum, force_baseline=force_baseline)

def noiseprint2pnd(dat):
    mapp = dat['map']
    valid = dat['valid']
    range0 = dat['range0'].flatten()
    range1 = dat['range1'].flatten()
    imgsize = dat['imgsize'].flatten()

    return genMappUint8(mapp,valid,range0,range1,imgsize)

def genMappUint8(mapp, valid, range0, range1, imgsize, vmax=None, vmin=None):
    mapp_s = np.copy(mapp)
    mapp_s[valid == 0] = np.min(mapp_s[valid > 0])

    if vmax is None:
        vmax = np.nanmax(mapp_s)
    if vmin is None:
        vmin = np.nanmin(mapp_s)

    mapUint8 = (255 * (mapp_s.clip(vmin, vmax) - vmin) / (vmax - vmin)).clip(0, 255).astype(np.uint8)
    mapUint8 = 255 - resizeMapWithPadding(mapUint8, range0, range1, imgsize)

    return mapUint8

def resizeMapWithPadding(x, range0, range1, shapeOut):
    range0 = range0.flatten()
    range1 = range1.flatten()
    xv = np.arange(shapeOut[1])
    yv = np.arange(shapeOut[0])
    y = interp1d(range1, x    , axis=1, kind='nearest', fill_value='extrapolate', assume_sorted=True, bounds_error=False)
    y = interp1d(range0, y(xv), axis=0, kind='nearest', fill_value='extrapolate', assume_sorted=True, bounds_error=False)
    return y(yv).astype(x.dtype)