import sys
from global_string_identifiers import *
import weak_scaling_benchmark as wsb
import contour_config

exp_dict = contour_config.get(sys.argv, mode='benchmark')

wsb.benchmark(exp_dict)