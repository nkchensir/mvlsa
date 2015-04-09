"""
Functions for calculating the statistical significant differences between two dependent or independent correlation  coefficients.
The Fisher and Steiger method is adopted from the R package http://personality-project.org/r/html/paired.r.html
and is described in detail in the book 'Statistical Methods for Psychology'
Steiger's method is from the paper "Tests for comparing elements of a correlation matrix" http://www.psychmike.com/Steiger.pdf
The Zou method is adopted from http://seriousstats.wordpress.com/2012/02/05/comparing-correlations/
Credit goes to the authors of above mentioned packages!
Author: Philipp Singer (www.philippsinger.info)
Modified by: Pushpendre Rastogi.
"""

from __future__ import division

__author__ = 'psinger'
__modifier__ = 'pushpendre' # Google for Phillip Singer's original code to see the diff
import numpy as np
from scipy.stats import t, norm
from math import atanh, pow, tanh


def rz_ci(r, n, conf_level = 0.95):
    zr_se = pow(1/(n - 3), .5)
    moe = norm.ppf(1 - (1 - conf_level)/float(2)) * zr_se
    zu = atanh(r) + moe
    zl = atanh(r) - moe
    return tanh((zl, zu))

def rho_rxy_rxz(rxy, rxz, ryz):
    num = (ryz-1/2.*rxy*rxz)*(1-pow(rxy,2)-pow(rxz,2)-pow(ryz,2))+pow(ryz,3)
    den = (1 - pow(rxy,2)) * (1 - pow(rxz,2))
    return num/float(den)

def dependent_corr(xy, xz, yz, n, twotailed=False, conf_level=None, method='steiger'):
    """
    Calculates the statistic significance between two dependent correlation coefficients
    @param xy: correlation coefficient between x and y
    @param xz: correlation coefficient between x and z
    @param yz: correlation coefficient between y and z
    @param n: number of elements in x, y and z
    @param twotailed: whether to calculate a one or two tailed test, only works for 'steiger' method
    @param conf_level: confidence level, only works for 'zou' method
    @param method: defines the method uses, 'steiger' or 'zou'
    @return: t and p-val
    """
    if method == 'steiger':
        d = xy - xz
        determin = 1 - xy ** 2 - xz ** 2 - yz ** 2 + 2 * xy * xz * yz
        av = (xy + xz)/2
        cube = (1 - yz) * (1 - yz) * (1 - yz)
        e = (n - 1) * (1 + yz)/(((2 * (n - 1)/(n - 3)) * determin + (av ** 2) * cube))
        if e < 0:
            return np.nan, np.nan
        t2 = d * np.sqrt(e)
        p = 1 - t.cdf(abs(t2), n - 2)

        if twotailed:
            p *= 2
        " p is the probability of the null hypothesis"
        return t2, p
    elif method == 'zou':
        if conf_level==None:
            conf_level=0.95
        L1 = rz_ci(xy, n, conf_level=conf_level)[0]
        U1 = rz_ci(xy, n, conf_level=conf_level)[1]
        L2 = rz_ci(xz, n, conf_level=conf_level)[0]
        U2 = rz_ci(xz, n, conf_level=conf_level)[1]
        rho_r12_r13 = rho_rxy_rxz(xy, xz, yz)
        lower = xy - xz - pow((pow((xy - L1), 2) + pow((U2 - xz), 2) - 2 * rho_r12_r13 * (xy - L1) * (U2 - xz)), 0.5)
        upper = xy - xz + pow((pow((U1 - xy), 2) + pow((xz - L2), 2) - 2 * rho_r12_r13 * (U1 - xy) * (xz - L2)), 0.5)
        return lower, upper
    else:
        raise Exception('Wrong method!')

def independent_corr(xy, ab, n, n2 = None, twotailed=True, conf_level=0.95, method='fisher'):
    """
    Calculates the statistic significance between two independent correlation coefficients
    @param xy: correlation coefficient between x and y
    @param xz: correlation coefficient between a and b
    @param n: number of elements in xy
    @param n2: number of elements in ab (if distinct from n)
    @param twotailed: whether to calculate a one or two tailed test, only works for 'fisher' method
    @param conf_level: confidence level, only works for 'zou' method
    @param method: defines the method uses, 'fisher' or 'zou'
    @return: z and p-val
    """

    if method == 'fisher':
        xy_z = 0.5 * np.log((1 + xy)/(1 - xy))
        xz_z = 0.5 * np.log((1 + ab)/(1 - ab))
        if n2 is None:
            n2 = n

        se_diff_r = np.sqrt(1/(n - 3) + 1/(n2 - 3))
        diff = xy_z - xz_z
        z = abs(diff / se_diff_r)
        p = (1 - norm.cdf(z))
        if twotailed:
            p *= 2

        return z, p
    elif method == 'zou':
        L1 = rz_ci(xy, n, conf_level=conf_level)[0]
        U1 = rz_ci(xy, n, conf_level=conf_level)[1]
        L2 = rz_ci(ab, n2, conf_level=conf_level)[0]
        U2 = rz_ci(ab, n2, conf_level=conf_level)[1]
        lower = xy - ab - pow((pow((xy - L1), 2) + pow((U2 - ab), 2)), 0.5)
        upper = xy - ab + pow((pow((U1 - xy), 2) + pow((ab - L2), 2)), 0.5)
        return lower, upper
    else:
        raise Exception('Wrong method!')

#print dependent_corr(.396, .179, .088, 3000, method='steiger')
#print dependent_corr(.396, .179, .088, 3000, method='zou')

# print independent_corr(.560, .588, 100, 353, method='fisher')
# print independent_corr(.560, .588, 100, 353, method='zou')
if __name__ == "__main__":
    import sys, argparse
    parser = argparse.ArgumentParser(description="This code can reproduce the top section of Table~2 \nfrom the paper, Multiview LSA: Representation Learning via Generalized CCA. \nWith its default settings it reproduces the last column and 'MC' row\n")
    parser.add_argument('n', type=int, default=30, nargs='?',
                        help="the number of data points in dataset")
    parser.add_argument('lc_max', default=0.2, nargs='?', type=float,
                        help="the maximum LC from start")
    parser.add_argument('midval', default=0.9, nargs='?', type=float,
                        help="Assumed maximum third correlation")
    parser.add_argument('confidence_thresh', default=0.05, nargs='?', type=float,
                        help="the required confidence level.")

    args = parser.parse_args()
    lc_max = args.lc_max
    n = args.n
    midval = args.midval
    confidence_thresh = args.confidence_thresh
    #print dependent_corr(r1, r2, r3, r4)
    done = False
    for lc in np.arange(lc_max, 0.000, -0.001):
        for i in np.arange(0, 1-lc, 0.01):
            _,p=dependent_corr(i, i + lc, midval, n)
            #print p
            if p > confidence_thresh:
                done = True
                break
        if done:
            break
    print "%0.3f"%lc
