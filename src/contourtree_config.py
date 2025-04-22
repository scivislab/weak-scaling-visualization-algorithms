from global_string_identifiers import *
import os
import sys

def get(argv, mode='scaling_data'):

    if len(argv) < 2:
        print("no thread count given as arg", file=sys.stderr)
    threads = int(argv[1])

    if len(argv) < 3:
        print("no scaling method selected", file=sys.stderr)
    scaling_method = argv[2] # valid entries: 'resampling', 'extent' , 'replication'

    if len(argv) < 4:
        print("no data as arg", file=sys.stderr)
    data_path = argv[3]
    if data_path[-4:] != '.vti':
        print("wrong data format - data has to be .vti", file=sys.stderr)
    path, file = os.path.split(data_path)
    name = file[:-4]
    name = name.removesuffix('_copy')
    name = name.removesuffix('Large')

    fieldname = 'ImageFile'
    if len(argv) > 4:
        fieldname = argv[4]

    algorithm = 'vtkm'
    if len(argv) > 5:
        algorithm = argv[5]

    exp_dict = dict()
    exp_dict[DATA_FILENAME] = data_path
    exp_dict[DATA_FIELDNAME] = fieldname

    if mode == 'scaling_data':
        exp_dict[BM_OUTPUT_FILENAME] = 'output/contourtree_' + algorithm + '/contourtree_data_' + name + '.csv'
    if mode == 'benchmark':
        exp_dict[BM_OUTPUT_FILENAME] = 'output/contourtree_' + algorithm + '/contourtree_weak_' + name + '.csv'
    exp_dict[BM_ALGO] = 'contourtree'
    exp_dict[BM_NUM_REP] = 10
    exp_dict[OUT_DATA_PREFIX] = path + '/' + exp_dict[BM_ALGO] + '_' + file[:-4] + '_' + algorithm

    exp_dict[SEARCH_SCALING_METHOD] = scaling_method
    exp_dict[SEARCH_DESTINATION_FACTOR] = threads
    exp_dict[SEARCH_MAX_IT] = 10
    exp_dict[SEARCH_EPSILON] = 0.01
    exp_dict[SEARCH_NUM_REP_ORIG] = 7
    exp_dict[SEARCH_NUM_REP_SCALED] = 5
    exp_dict[SEARCH_DATA_ORIGINAL_DIM] = [128]*3

    exp_dict[CT_ALGORITHM] = algorithm

    return exp_dict
