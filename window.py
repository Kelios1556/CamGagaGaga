import scipy.io
from scipy.fft import fft,fftfreq
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal.windows import blackman,general_cosine,hamming,hann,nuttall,parzen,triang
from scipy.interpolate import interp1d

from argparse import ArgumentParser

N = 20
step = 0.025
w = np.zeros(int(N * 1/step))
interpolate = 8

def fourier(data):
    # yf = 2/(N/step) * fft(data)[1:int(N/step//2)]
    yf = np.squeeze(np.real(fft(data)))
    xf = fftfreq(data.shape[0], step)
    return xf, yf

def window(data, w):
    if w.shape[0] < data.shape[0]:
        while data.shape[0] - w.shape[0] >= w.shape[0]:
            w = np.append(w, w)
    d = np.squeeze(data)
    yfw = np.squeeze(np.real(fft(d*w)))
    return yfw

def smooth(datax, datay):
    smooth_ = interp1d(datax, datay, kind="cubic")
    datax_ = np.linspace(datax.min(), datax.max(), N*interpolate)
    datay_ = smooth_(datax_)
    return datay_

def main():
    parser = ArgumentParser()
    parser.add_argument('-w', type=str) # determine plot window or not
    parser.add_argument('-o', type=str) # determine plot un-connected data or not
    args = parser.parse_args()
    PLOT_WINDOW = True
    PLOT_ORIGINAL = False
    plottedWin = [False]*7 # blackman, general_cosine, hamming, hann, nuttall, parzen, triang
    if args.w:
        PLOT_WINDOW = False
        '''
        if args.w.lower() == 'none':
            PLOT_WINDOW = False
        '''
        if args.w.lower() == 'all':
            PLOT_WINDOW = True
        if 'blackman' in args.w:
            plottedWin[0] = True
        if 'general_cosine' in args.w:
            plottedWin[1] = True
        if 'hamming' in args.w:
            plottedWin[2] = True
        if 'hann' in args.w:
            plottedWin[3] = True
        if 'nuttall' in args.w:
            plottedWin[4] = True
        if 'parzen' in args.w:
            plottedWin[5] = True
        if 'triang' in args.w:
            plottedWin[6] = True
    if args.o and args.o.lower() == 't':
        PLOT_WINDOW = False
        PLOT_ORIGINAL = True

    data = np.array(scipy.io.loadmat("sin5.mat")['f0'])
    print("=====original data=====")
    print(data[0:int(N/step//2)])
    orig_data = data[1:int(N/step/2)]
    data = np.append(orig_data, orig_data)
    xf, yf = fourier(data)
    orig_xf, orig_yf = fourier(orig_data)
    yf_ = smooth(xf, yf)
    orig_yf_ = smooth(orig_xf, orig_yf)

    labels = []
    xf_ = np.linspace(xf.min(), xf.max(), N*interpolate)
    orig_xf_ = np.linspace(orig_xf.min(), orig_xf.max(), N*interpolate)
    if PLOT_ORIGINAL == False:
        plt.plot(xf_, yf_, '-r')
        labels.append('FFT')
    else:
        plt.plot(orig_xf_, orig_yf_, 'tab:cyan')
        labels.append(['orig_FFT'])

    if plottedWin[0] or PLOT_WINDOW:
        print("======apply blackman=====")
        w = blackman(data.shape[0]//2)
        re_blackman = window(data, w)
        re_blackman_ = smooth(xf, re_blackman)
        plt.plot(xf_, re_blackman_, '-g')
        labels.append('blackman')

    if plottedWin[1] or PLOT_WINDOW:
        print("=====apply general_cosine=====")
        a = np.array([10e-3]*(data.shape[0]//2)) # modify later
        w = general_cosine(data.shape[0]//2, a)
        re_geCos = window(data, w)
        re_geCos_ = smooth(xf, re_geCos)
        plt.plot(xf_, re_geCos_, 'b')
    
    if plottedWin[2] or PLOT_WINDOW:
        print("=====apply hamming=====")
        w = hamming(data.shape[0]//2)
        re_hamming = window(data, w)
        re_hamming_ = smooth(xf, re_hamming)
        plt.plot(xf_, re_hamming_, '-y')
        labels.append('hamming')

    if plottedWin[3] or PLOT_WINDOW:
        print("=====apply hann=====")
        w = hann(data.shape[0]//2)
        re_hann = window(data, w)
        re_hann_ = smooth(xf, re_hann)
        plt.plot(xf_, re_hann_, '-c')
        labels.append('hann')

    # print("=====apply lanczos=====")
    # w = lanczos(int(N/step)).reshape(-1,1)
    # re_lanczos = window(data, w)

    if plottedWin[4] or PLOT_WINDOW:
        print("=====apply nuttall=====")
        w = nuttall(data.shape[0]//2)
        re_nuttall = window(data, w)
        re_nuttall_ = smooth(xf, re_nuttall)
        plt.plot(xf_, re_nuttall_, '-k')
        labels.append('nuttall')

    if plottedWin[5] or PLOT_WINDOW:
        print("=====apply parzen=====")
        w = parzen(data.shape[0]//2)
        re_parzen = window(data, w)
        re_parzen_ = smooth(xf, re_parzen)
        plt.plot(xf_, re_parzen_, color='tab:orange')
        labels.append('parzen')

    if plottedWin[6] or PLOT_WINDOW:
        print("=====apply triang=====")
        w = triang(data.shape[0]//2)
        re_triang = window(data, w)
        re_triang_ = smooth(xf, re_triang)
        plt.plot(xf_, re_triang_, color='tab:purple')
        labels.append('triang')

    print("=====plot=====")
    plt.legend(labels)
    plt.grid()
    plt.show()

main()

