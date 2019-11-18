import numpy as np
from scipy.interpolate import interp1d


def mdwave(wave):
    """ median delta wavelength """
    return np.median(np.diff(wave))


def wave_log10(wave, dwave=None):
    """ generate log10 wavelength array given wave array

    Parameters
    ----------
    wave:
        old wavelength array
    dwave:
        delta wavelength. if not specified, use median(dwave).

    Example
    -------
    >>> wave_new = wave_log10(wave)

    """
    if dwave is None:
        dwave = mdwave(wave)
    npix = np.int(np.ptp(wave) / dwave) + 1
    return np.logspace(np.log10(np.min(wave)), np.log10(np.max(wave)), npix,
                       base=10.0)


def center2edge(x):
    x = np.asarray(x)
    dx = np.diff(x)
    return np.hstack((x[0] - .5 * dx[0], x[:-1] + .5 * dx, x[-1] + .5 * dx[-1]))


def rebin(wave, flux=None, flux_err=None, mask=None, wave_new=None):
    """ Rebin spectrum to a new wavelength grid

    Parameters
    ----------
    wave: array
        old wavelength
    flux: array
        old flux
    flux_err: array (optional)
        old flux error
    mask: array (optional)
        old mask
    wave_new:
        new wavelength. if None, use log10 wavelength.

    Return
    ------
    re-binned (flux, [flux_err], [mask])
    """
    wave = np.asarray(wave)
    if wave_new is None:
        wave_new = wave_log10(wave, dwave=None)
    else:
        wave_new = np.asarray(wave_new)

    wave_edge = center2edge(wave)
    wave_new_edge = center2edge(wave_new)

    I = interp1d(wave_edge[:-1], np.arange(len(wave)), kind="linear",
                 bounds_error=False)
    wave_new_edge_pos = I(wave_new_edge)  # accurate position projected to old
    wave_new_edge_pos2 = np.array(
        [wave_new_edge_pos[:-1], wave_new_edge_pos[1:]]).T  # slipt to lo & hi

    wave_new_ipix = np.floor(wave_new_edge_pos2).astype(int)  # integer part
    wave_new_frac = wave_new_edge_pos2 - wave_new_ipix  # fraction part
    flags = np.any(np.isnan(wave_new_edge_pos2), axis=1)

    result = []

    # rebin flux
    if flux is not None:
        flux = np.asarray(flux)
        assert flux.shape == wave.shape
        flux_new = np.zeros_like(wave_new, dtype=float)
        for ipix, this_flag in enumerate(flags):
            if not this_flag:
                flux_new[ipix] = np.sum(
                    flux[wave_new_ipix[ipix, 0]:wave_new_ipix[ipix, 1]]) \
                    - flux[wave_new_ipix[ipix, 0]] * wave_new_frac[ipix, 0] \
                    + flux[wave_new_ipix[ipix, 1]] * wave_new_frac[ipix, 1]
            else:
                flux_new[ipix] = np.nan
        result.append(flux_new)

    # rebin flux_err
    if flux_err is not None:
        flux_err2 = np.square(np.asarray(flux_err, dtype=float))
        assert flux_err2.shape == wave.shape
        flux_err2_new = np.zeros_like(wave_new, dtype=float)
        for ipix, this_flag in enumerate(flags):
            if not this_flag:
                flux_err2_new[ipix] = np.sum(
                    flux_err2[wave_new_ipix[ipix, 0]:wave_new_ipix[ipix, 1]]) \
                    - flux_err2[wave_new_ipix[ipix, 0]] * wave_new_frac[ipix, 0] \
                    + flux_err2[wave_new_ipix[ipix, 1]] * wave_new_frac[ipix, 1]
            else:
                flux_err2_new[ipix] = np.nan
        result.append(np.sqrt(flux_err2_new))

    # rebin mask
    if mask is not None:
        mask = np.asarray(mask)
        assert mask.shape == wave.shape
        mask_new = np.zeros_like(wave_new, dtype=bool)
        for ipix, this_flag in enumerate(flags):
            if not this_flag:
                mask_new[ipix] = np.any(
                    mask[wave_new_ipix[ipix, 0]:wave_new_ipix[ipix, 1] + 1])
        result.append(mask_new)

    return result


def _test():
    wave, flux, wave_new = np.arange(10), np.ones(10), np.arange(0, 10, 2) + 0.5
    print(wave, flux)
    print(wave_new, rebin(wave, flux, wave_new=wave_new))
    # figure()
    # plot(wave, flux, 'x-')
    # plot(wave_new, rebin(wave, flux, wave_new), 's-')
    return


if __name__ == "__main__":
    _test()
