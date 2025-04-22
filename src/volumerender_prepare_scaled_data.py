from global_string_identifiers import *
import weak_scaling_benchmark as wsb
import os
import sys
import volumerender_config

exp_dict = volumerender_config.get(sys.argv, mode='scaling_data')

wsb.prepare_scaled_data(exp_dict)