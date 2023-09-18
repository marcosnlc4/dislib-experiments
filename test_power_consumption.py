import pyRAPL
import numpy as np

pyRAPL.setup()
measure = pyRAPL.Measurement('bar')
measure.begin()

# ...
# Instructions to be evaluated.
# ...
a = np.dot(np.random.rand(1000, 1000),np.random.rand(1000, 1000).T)

measure.end()

print((measure.result.pkg[0])/measure.result.duration)