import sys
from global_string_identifiers import *
import weak_scaling_benchmark as wsb
import contourtree_config

exp_dict = contourtree_config.get(sys.argv, mode='scaling_data')

wsb.prepare_scaled_data(exp_dict)