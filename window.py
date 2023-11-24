import scipy.io
from scipy.fft import fft,fftfreq
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal.windows import blackman,general_cosine,hamming,hann,nuttall,parzen,triang
from scipy.interpolate import interp1d

from argparse import ArgumentParser

N = 10
step = 0.025
w = np.zeros(int(N * 1/step))
interpolate = 8

def fourier(data):
    # yf = 2/(N/step) * fft(data)[1:int(N/step//2)]
    yf = np.squeeze(np.real(fft(data)))
    xf = fftfreq(int(N/step)-2, step)
    return xf, yf

def window(data, w):
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
    args = parser.parse_args()
    PLOT_WINDOW = True
    if args.w and args.w.lower() == 'f':
        PLOT_WINDOW = False

    data = np.array(scipy.io.loadmat("sin5.mat")['f0'])
    print("=====original data=====")
    print(data[0:int(N/step//2)])
    data = data[1:int(N/step/2)]
    data = np.append(data, data)
    xf, yf = fourier(data)
    print(xf.shape, yf.shape)
    yf_ = smooth(xf, yf)

    print("======apply blackman=====")
    w = blackman(int(N/step)-2)
    re_blackman = window(data, w)
    re_blackman_ = smooth(xf, re_blackman)

    print("=====apply general_cosine=====")
    a = np.array([10e-1]*int(N/step)) # modify later
    w = general_cosine(int(N/step)-2, a)
    re_geCos = window(data, w)
    re_geCos_ = smooth(xf, re_geCos)
    
    print("=====apply hamming=====")
    w = hamming(int(N/step)-2)
    re_hamming = window(data, w)
    re_hamming_ = smooth(xf, re_hamming)

    print("=====apply hann=====")
    w = hann(int(N/step)-2)
    re_hann = window(data, w)
    re_hann_ = smooth(xf, re_hann)

    # print("=====apply lanczos=====")
    # w = lanczos(int(N/step)).reshape(-1,1)
    # re_lanczos = window(data, w)

    print("=====apply nuttall=====")
    w = nuttall(int(N/step)-2)
    re_nuttall = window(data, w)
    re_nuttall_ = smooth(xf, re_nuttall)

    print("=====apply parzen=====")
    w = parzen(int(N/step)-2)
    re_parzen = window(data, w)
    re_parzen_ = smooth(xf, re_parzen)

    print("=====apply triang=====")
    w = triang(int(N/step)-2)
    re_triang = window(data, w)
    re_triang_ = smooth(xf, re_triang)

    print("=====plot=====")
    xf_ = np.linspace(xf.min(), xf.max(), N*interpolate)
    plt.plot(xf_, yf_, '-r')
    if PLOT_WINDOW == False:
        plt.legend(['FFT'])
    else:
        plt.plot(xf_, re_blackman_, '-g')
        plt.plot(xf_, re_geCos_, '-b')
        plt.plot(xf_, re_hamming_, '-y')
        plt.plot(xf_, re_hann_, '-c')
        plt.plot(xf_, re_nuttall_, '-k')
        plt.plot(xf_, re_parzen_, color='tab:orange')
        plt.plot(xf_, re_triang_, color='tab:purple')
        plt.legend(['FFT', 
                    'blackman', 
                    'general_cosine', 
                    'hamming', 
                    'hann', 
                    'nuttall',
                    'parzen', 
                    'triang'
                    ])
    plt.grid()
    plt.show()

main()

