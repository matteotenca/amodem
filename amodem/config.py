"""Configuration class."""
import pprint

import numpy as np


class Configuration:
    # sampling_frequency = 32000.0  # sampling frequency [Hz]
    symbol_duration = 0.001  # symbol duration [seconds]
    # n_points = 64
    # frequencies = [0.5e3, 11.5e3]  # use 1..8 kHz carriers

    # audio config
    bits_per_sample = 16
    latency = 0.1

    # sender config
    silence_start = 0.5
    silence_stop = 0.5

    # receiver config
    skip_start = 0.1
    timeout = 30.0

    def __init__(self, sampling_frequency: float = 32000, n_points=64, frequencies=None):
        # self.__dict__.update(**kwargs)
        self.sampling_frequency = sampling_frequency
        self.Npoints = n_points
        if frequencies is not None:
            self.frequencies = frequencies
        else:
            self.frequencies = []

        self.sample_size = self.bits_per_sample // 8
        assert self.sample_size * 8 == self.bits_per_sample

        self.Ts = 1.0 / self.sampling_frequency
        self.Fsym = 1 / self.symbol_duration
        self.Nsym = int(self.symbol_duration / self.Ts)
        self.baud = int(1.0 / self.symbol_duration)
        assert self.baud * self.symbol_duration == 1

        if len(self.frequencies) > 1:
            first, last = self.frequencies
            # self.frequencies = np.arange(first, last + self.baud, self.baud)
            self.frequencies = np.arange(first, last + self.baud, self.baud)
        pprint.pprint(self.frequencies)
        self.Nfreq = len(self.frequencies)
        self.carrier_index = 0
        self.Fc = self.frequencies[self.carrier_index]

        bits_per_symbol = int(np.log2(self.Npoints))
        assert 2 ** bits_per_symbol == self.Npoints
        self.bits_per_baud = bits_per_symbol * self.Nfreq
        self.modem_bps = self.baud * self.bits_per_baud

        carriers = np.array([
            np.exp(2j * np.pi * f * np.arange(0, self.Nsym) * self.Ts)
            for f in self.frequencies
        ])
        self.carriers = np.ndarray.copy(carriers)

        carriers2 = np.array([
            np.exp(2j * np.pi * f * np.arange(0, self.Nsym) * self.Ts)
            for f in [2.4e3]
        ])
        self.carriers2 = np.ndarray.copy(carriers2)

        # QAM constellation
        Nx = 2 ** int(np.ceil(bits_per_symbol // 2))
        Ny = self.Npoints // Nx
        symbols = [complex(x, y) for x in range(Nx) for y in range(Ny)]
        symbols = np.array(symbols)
        symbols = symbols - symbols[-1]/2
        self.symbols = symbols / np.max(np.abs(symbols))


# MODEM configurations for various bitrates [kbps]
# bitrates = {
#     0: Configuration(sampling_frequency=8e3, n_points=2, frequencies=[0.5e3, 1.5e3]),
#     1: Configuration(sampling_frequency=8e3, n_points=2, frequencies=[2e3]),
#     2: Configuration(sampling_frequency=8e3, n_points=4, frequencies=[2e3]),
#     4: Configuration(sampling_frequency=8e3, n_points=16, frequencies=[2e3]),
#     8: Configuration(sampling_frequency=8e3, n_points=16, frequencies=[1e3, 2e3]),
#     12: Configuration(sampling_frequency=16e3, n_points=16, frequencies=[3e3, 5e3]),
#     16: Configuration(sampling_frequency=16e3, n_points=16, frequencies=[2e3, 5e3]),
#     20: Configuration(sampling_frequency=16e3, n_points=16, frequencies=[2e3, 6e3]),
#     24: Configuration(sampling_frequency=16e3, n_points=16, frequencies=[1e3, 6e3]),
#     28: Configuration(sampling_frequency=32e3, n_points=16, frequencies=[3e3, 9e3]),
#     32: Configuration(sampling_frequency=32e3, n_points=16, frequencies=[2e3, 9e3]),
#     36: Configuration(sampling_frequency=32e3, n_points=64, frequencies=[4e3, 9e3]),
#     42: Configuration(sampling_frequency=32e3, n_points=64, frequencies=[4e3, 10e3]),
#     48: Configuration(sampling_frequency=32e3, n_points=64, frequencies=[3e3, 10e3]),
#     54: Configuration(sampling_frequency=32e3, n_points=64, frequencies=[2e3, 10e3]),
#     60: Configuration(sampling_frequency=32e3, n_points=64, frequencies=[2e3, 11e3]),
#     64: Configuration(sampling_frequency=32e3, n_points=256, frequencies=[3e3, 10e3]),
#     72: Configuration(sampling_frequency=32e3, n_points=256, frequencies=[2e3, 10e3]),
#     80: Configuration(sampling_frequency=32e3, n_points=256, frequencies=[2e3, 11e3]),
# }

mbitrates = {
    0: {"sampling_frequency": 8e3, "n_points": 16, "frequencies": [2e3]},
    1: {"sampling_frequency": 8e3, "n_points": 2, "frequencies": [2e3]},
    2: {"sampling_frequency": 8e3, "n_points": 4, "frequencies": [2e3]},
    4: {"sampling_frequency": 8e3, "n_points": 16, "frequencies": [2e3]},
    8: {"sampling_frequency": 8e3, "n_points": 16, "frequencies": [1e3, 2e3]},
    12: {"sampling_frequency": 16e3, "n_points": 16, "frequencies": [3e3, 5e3]},
    16: {"sampling_frequency": 16e3, "n_points": 16, "frequencies": [2e3, 5e3]},
    20: {"sampling_frequency": 16e3, "n_points": 16, "frequencies": [2e3, 6e3]},
    24: {"sampling_frequency": 16e3, "n_points": 16, "frequencies": [1e3, 6e3]},
    28: {"sampling_frequency": 32e3, "n_points": 16, "frequencies": [3e3, 9e3]},
    32: {"sampling_frequency": 32e3, "n_points": 16, "frequencies": [2e3, 9e3]},
    36: {"sampling_frequency": 32e3, "n_points": 64, "frequencies": [4e3, 9e3]},
    42: {"sampling_frequency": 32e3, "n_points": 64, "frequencies": [4e3, 10e3]},
    48: {"sampling_frequency": 32e3, "n_points": 64, "frequencies": [3e3, 10e3]},
    54: {"sampling_frequency": 32e3, "n_points": 64, "frequencies": [2e3, 10e3]},
    60: {"sampling_frequency": 32e3, "n_points": 64, "frequencies": [2e3, 11e3]},
    64: {"sampling_frequency": 32e3, "n_points": 256, "frequencies": [3e3, 10e3]},
    72: {"sampling_frequency": 32e3, "n_points": 256, "frequencies": [2e3, 10e3]},
    80: {"sampling_frequency": 32e3, "n_points": 256, "frequencies": [2e3, 11e3]},
}

def fastest():
    return mbitrates[max(mbitrates)]


def slowest():
    return mbitrates[min(mbitrates)]
