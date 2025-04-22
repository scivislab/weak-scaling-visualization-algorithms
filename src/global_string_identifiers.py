# list of all constant strings for writing csv files etc.
# this is to keep data_properties.csv files consistent with the setup dictionaries for experiments

# 0 DATA PROPERTIES FILENAME
DATA_PROPERTIES_FILENAME = "data_properties_v1.csv"

# 1 DATA
DATA_FILENAME = "filename"
DATA_FIELDNAME = "fieldname"
DATA_EXTENT = "extent"
DATA_RANGE = "range"
DATA_NUM_POINTS = "num_points"
DATA_NUM_CELLS = "num_cells"
DATA_MEM_SIZE = "mem_size"

# 1.0 all properties defined above under 1 and 1.x 
DATA_PROPERTIES = [DATA_FILENAME,
                   DATA_FIELDNAME,
                   DATA_EXTENT,
                   DATA_RANGE,
                   DATA_NUM_POINTS,
                   DATA_NUM_POINTS,
                   DATA_NUM_CELLS,
                   DATA_MEM_SIZE
                   ]

# 2 BENCHMARK
BM_NAME = "exp_name"
BM_RANKS = "ranks"
BM_CORES = "cores"
BM_NUM_REP = "num_rep"
BM_OUTPUT_FILENAME = "output_filename"
BM_AVG_TIME = "Avg_Time"
BM_STD_DEV_TIME = "Std_Dev"
BM_ALGO = 'algo'

# 2.1 Contour
IC_NUM_ISO = "num_iso"
IC_RANGE = "ic_range"
IC_ALGORITHM = "ic_algorithm"
IC_VALUES = "ic_values"

# 2.3 Volume Rendering
VR_ERT = "early_ray_term"
VR_IMAGE_SIZE = "resolution"
VR_OPACITY = "opacity"
VR_RANGE = "vr_range"

# 2.4 Contour Tree 
CT_ALGORITHM = "ct_algorithm" 

# 2.5 Streamlines
SL_MODE = "seed_mode"

# 3 Output data
OUT_NUM_POINTS = "out_num_points"
OUT_NUM_CELLS = "out_num_cells"
OUT_MEM_SIZE = "out_mem_size"
OUT_DATA_PREFIX = "out_data_prefix"

# 4 DATA SCALING VIA SEARCH
SEARCH_MAX_IT = "search_max_it"
SEARCH_USED_IT = "search_used_it"
SEARCH_EPSILON = "search_epsilon"
SEARCH_NUM_REP_SCALED = "search_num_rep_scaled"
SEARCH_NUM_REP_ORIG = "search_num_rep_orig"
SEARCH_DESTINATION_FACTOR = "search_destination_factor"
SEARCH_SCALING_FACTOR = "search_scaling_factor"
SEARCH_SCALING_METHOD = "search_scaling_method"
SEARCH_ERROR = "search_error"
SEARCH_ERROR_LAST = "search_error_last"
SEARCH_DATA_OUT = "data_path"
SEARCH_TIME_ORIGINAL = "Time_Orig"
SEARCH_TIME_SCALED = "Time_Scaled"
SEARCH_TIME_SEARCHED = "Time_Searched"
SEARCH_TIME_CUMULATED = "Time_Cumulated"
SEARCH_TIME_TOTAL = "Total_Time"
SEARCH_DATA_ORIGINAL_DIM = "original_dimension"
SEARCH_RFT = 'reason_for_termination'
SEARCH_REPLICATION_SCALING_MODE = "search_rsm"
SEARCH_CURRENT_ITERATION = "search_current_it"

# 5 WEAK SCALING EXPERIMENT
WEAK_TIME= "ptime"
WEAK_MODE = "mode"