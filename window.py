import scipy.io
from scipy.fft import fft,fftfreq
import numpy as np
import matplotlib.pyplot as plt

from scipy.signal.windows import blackman,general_cosine,hamming,hann,nuttall,parzen,triang

N = 10
step = 0.01
w = np.zeros(int(N * 1/step))

def fourier(data):
    yf = 2/(N/step) * np.abs(fft(data)[1:int(N/step//2)])
    xf = fftfreq(int(N/step), step)[1:int(N/step//2)]
    return xf, yf

def window(data, w):
    d = data[0:int(N/step)]
    yfw = 2/(N/step) * np.abs(fft(d*w)[1:int(N/step//2)])
    return yfw

def main():
    data = np.array(scipy.io.loadmat("sin5.mat")['f0'])
    print("=====original data=====")
    print(data[0:int(N/step//2)])
    xf, yf = fourier(data)

    print("======apply blackman=====")
    w = blackman(int(N/step)).reshape(-1,1)
    re_blackman = window(data, w)

    print("=====apply general_cosine=====")
    a = np.array([10e7]*int(N/step)) # modify later
    w = general_cosine(int(N/step), a).reshape(-1,1)
    re_geCos = window(data, w)
    
    print("=====apply hamming=====")
    w = hamming(int(N/step)).reshape(-1,1)
    re_hamming = window(data, w)

    print("=====apply hann=====")
    w = hann(int(N/step)).reshape(-1,1)
    re_hann = window(data, w)

    # print("=====apply lanczos=====")
    # w = lanczos(int(N/step)).reshape(-1,1)
    # re_lanczos = window(data, w)

    print("=====apply nuttall=====")
    w = nuttall(int(N/step)).reshape(-1,1)
    re_nuttall = window(data, w)

    print("=====apply parzen=====")
    w = parzen(int(N/step)).reshape(-1,1)
    re_parzen = window(data, w)

    print("=====apply triang=====")
    w = triang(int(N/step)).reshape(-1,1)
    re_triang = window(data, w)

    print("=====plot=====")
    plt.semilogy(xf, yf, '-r')
    plt.semilogy(xf, re_blackman, '-g')
    plt.semilogy(xf, re_geCos, '-b')
    plt.semilogy(xf, re_hamming, '-y')
    plt.semilogy(xf, re_hann, '-c')
    # plt.semilogy(xf, re_lanczos, '-m')
    plt.semilogy(xf, re_nuttall, '-k')
    plt.semilogy(xf, re_parzen, color='tab:orange')
    plt.semilogy(xf, re_triang, color='tab:purple')
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

