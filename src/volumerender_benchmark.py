import sys
from global_string_identifiers import *
import weak_scaling_benchmark as wsb
import volumerender_config

exp_dict = volumerender_config.get(sys.argv, mode='benchmark')

wsb.benchmark(exp_dict)