"""Constants used by the SI-only first-pass model."""

AVOGADRO = 6.022_140_76e23  # mol^-1, exact
ATOMIC_MASS = 1.660_539_066_60e-27  # kg
BOLTZMANN = 1.380_649e-23  # J K^-1, exact
KEV_TO_KELVIN = 1.160_451_812e7
KEV_TO_JOULE = 1.602_176_634e-16
MEV_TO_JOULE = 1.602_176_634e-13
SPEED_OF_LIGHT = 299_792_458.0  # m s^-1, exact

# Atomic mass numbers and fully stripped nuclear charges for the current model.
NUCLIDES = {
    "n": (1.0, 0),
    "h1": (1.0, 1),
    "d": (2.0, 1),
    "t": (3.0, 1),
    "he3": (3.0, 2),
    "he4": (4.0, 2),
    "c12": (12.0, 6),
    "c13": (13.0, 6),
    "n13": (13.0, 7),
    "o14": (14.0, 8),
    "n14": (14.0, 7),
    "o15": (15.0, 8),
    "n15": (15.0, 7),
    "o16": (16.0, 8),
    "f17": (17.0, 9),
    "o17": (17.0, 8),
    "f18": (18.0, 9),
}
