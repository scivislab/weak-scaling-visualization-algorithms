from global_string_identifiers import *
import scaling_algos as sc
import pv_io as pvio
import algos as alg
import paraview.simple as pvs
import sys
import numpy as np
import math
import time
import scipy.optimize as opt

def prepare_scaled_data(exp_dict):
    total_start = time.time()
    #read data
    data = pvio.read_vti(exp_dict)
    prefix = exp_dict[BM_ALGO]

    rft= 0

    # execute algorithm on workload for one core
    data = pvio.read_vti(exp_dict)
    scaled_data = data
    if exp_dict[SEARCH_SCALING_METHOD] == 'extent':
        scaled_data = sc.scale_by_extent(data, 1.0, original_dim=exp_dict[SEARCH_DATA_ORIGINAL_DIM])

    # log execution time
    o_time = execute(scaled_data, exp_dict, repetitions=exp_dict[SEARCH_NUM_REP_ORIG])
    exp_dict[SEARCH_TIME_ORIGINAL] = o_time

    # if the destination factor just one, add necessary log fields to be consistent with the other runs
    if exp_dict[SEARCH_DESTINATION_FACTOR] == 1:
        output_filename = exp_dict[OUT_DATA_PREFIX] + '_' + str(exp_dict[SEARCH_DESTINATION_FACTOR])+"_input_scaled.pvti" 
        pvs.SaveData(output_filename, scaled_data)
        output_filename = exp_dict[OUT_DATA_PREFIX] + '_' + str(exp_dict[SEARCH_DESTINATION_FACTOR])+"_work_scaled.pvti" 
        pvs.SaveData(output_filename, scaled_data)
        # filling result fields
        exp_dict[SEARCH_TIME_SCALED] = o_time
        exp_dict[SEARCH_RFT] = 0
        exp_dict[SEARCH_TIME_SEARCHED] = o_time
        exp_dict[SEARCH_ERROR] = 0.0
        exp_dict[SEARCH_SCALING_FACTOR] = float(exp_dict[SEARCH_DESTINATION_FACTOR])
        exp_dict[SEARCH_DATA_OUT] = output_filename
        exp_dict[SEARCH_USED_IT] = 1
        exp_dict[SEARCH_TIME_TOTAL] = time.time() - total_start
    # for other destination factors, search for correct scaling factor
    else:
        # scale data and get the scaled exec time
        last_scaling_factor = 1.0
        scaling_factor = exp_dict[SEARCH_DESTINATION_FACTOR]
        scaled_data = scale(data, exp_dict, scaling_factor)

        # log first scaled exec time and write first scaled data 
        traditional_scaled_time = execute(scaled_data, exp_dict, repetitions=exp_dict[SEARCH_NUM_REP_SCALED])
        n_time = traditional_scaled_time
        output_filename = exp_dict[OUT_DATA_PREFIX] + '_' + str(exp_dict[SEARCH_DESTINATION_FACTOR])+"_input_scaled.pvti" 
        pvs.SaveData(output_filename, scaled_data, ChooseArraysToWrite=1, PointDataArrays=[exp_dict[DATA_FIELDNAME]], CellDataArrays=[])
        
        
        # setup function to search for zeroes
        f = n_time/o_time - exp_dict[SEARCH_DESTINATION_FACTOR]
        f_last = 1.0 - exp_dict[SEARCH_DESTINATION_FACTOR] # o_time/o_time - destination factor
        delta_f = 1.00

        closest_lower= 1.0
        closest_upper= math.inf

        if f > 0.0:
            # if the function is positive, we need to find a lower scaling factor
            # and the last scaling factor is the closest upper bound
            closest_upper = scaling_factor
        else:
            # if the function is negative, we need to find a upper scaling factor
            # and the last scaling factor is the closest lower bound
            closest_lower = scaling_factor

        # while loop continues if:
        # error is not small enough AND
        # maximum iteration is not reached AND
        # the extent of the data is still changing between iterations
        current_it = 0
        extent_changing = True
        while abs(f) > exp_dict[SEARCH_EPSILON] and current_it < exp_dict[SEARCH_MAX_IT] and extent_changing:
            # update extent from last iteration
            last_extent = scaled_data.GetDataInformation().GetExtent()

            # delete old scaled data
            pvs.Delete(scaled_data)

            # approx. derivative
            delta_f = (f - f_last) / (scaling_factor - last_scaling_factor)

            if math.isnan(delta_f) or delta_f == 0.0:
                rft += 8
                break

            if f / delta_f < 0.0 and scaling_factor > 2.0*exp_dict[SEARCH_DESTINATION_FACTOR]:
                # if the scaling factor is already larger than twice the destination factor
                # and would be increased even more, break
                rft += 16
                break

            if scaling_factor > 10.0*exp_dict[SEARCH_DESTINATION_FACTOR]:
                # iteration diverged too much
                rft += 256
                break

            if closest_upper == closest_lower:
                rft += 64
                break

            if scaling_factor <= closest_lower and f / delta_f > 0.0:
                rft += 32
                break
            if scaling_factor >= closest_upper and f / delta_f < 0.0:
                rft += 32
                break

            # update scaling factor
            last_scaling_factor = scaling_factor

            # damp if it iteration wants to go out of already computed bounds
            damping = 1.0
            while scaling_factor - damping*f / delta_f <= closest_lower or scaling_factor - damping*f / delta_f >= closest_upper:
                # damping factor is too large, decrease it
                damping *= 0.5
            while closest_upper == math.inf and scaling_factor - damping*f / delta_f >= 3.0*exp_dict[SEARCH_DESTINATION_FACTOR]:
                # damping factor is too large, decrease it
                damping *= 0.5
            scaling_factor -= damping * f / delta_f

            # scale data and execute
            scaled_data = scale(data, exp_dict, scaling_factor)
            n_time = execute(scaled_data, exp_dict, repetitions=exp_dict[SEARCH_NUM_REP_SCALED])
            f_last = f
            f = n_time/o_time - exp_dict[SEARCH_DESTINATION_FACTOR]

            if f > 0.0:
                # if the function is positive, we need to find a lower scaling factor
                # and the last scaling factor is the closest upper bound
                closest_upper = scaling_factor
            else:
                # if the function is negative, we need to find an upper scaling factor
                # and the last scaling factor is the closest lower bound
                closest_lower = scaling_factor

            if exp_dict[SEARCH_SCALING_METHOD] == 'extent':
                if sc.check_scale_by_extent(data, scaling_factor, exp_dict[SEARCH_DATA_ORIGINAL_DIM]):
                    # exceeded extent in extent scaling method
                    current_it += 1
                    rft += 128
                    break

            # update the current iteration and check whether the extent still changes
            extent_changing = not np.array_equal(last_extent,scaled_data.GetDataInformation().GetExtent())
            current_it += 1

        output_filename = exp_dict[OUT_DATA_PREFIX] + '_' + str(exp_dict[SEARCH_DESTINATION_FACTOR])+"_work_scaled.pvti" 
        pvs.SaveData(output_filename, scaled_data, ChooseArraysToWrite=1, PointDataArrays=[exp_dict[DATA_FIELDNAME]], CellDataArrays=[])

        # filling result fields
        exp_dict[SEARCH_TIME_SCALED] = traditional_scaled_time
        exp_dict[SEARCH_RFT] = (abs(f) <= exp_dict[SEARCH_EPSILON]) 
        exp_dict[SEARCH_RFT] += 2 * (current_it >= exp_dict[SEARCH_MAX_IT]) 
        exp_dict[SEARCH_RFT] += 4 * (1-extent_changing)
        exp_dict[SEARCH_RFT] += rft
        exp_dict[SEARCH_TIME_SEARCHED] = n_time
        exp_dict[SEARCH_ERROR] = f
        exp_dict[SEARCH_SCALING_FACTOR] = scaling_factor 
        exp_dict[SEARCH_DATA_OUT] = output_filename
        exp_dict[SEARCH_USED_IT] = current_it
        exp_dict[SEARCH_TIME_TOTAL] = time.time() - total_start

    pvio.write_dict_to_csv(exp_dict)


def benchmark(exp_dict):

    # mode = reagular scaling
    filename_prefix = exp_dict[OUT_DATA_PREFIX] + "_" + str(exp_dict[SEARCH_DESTINATION_FACTOR])
    filename = filename_prefix + "_input_scaled.pvti"
    exp_dict[DATA_FILENAME] = filename
    exp_dict[WEAK_MODE] = 'input scaling'

    # read data
    data = pvio.read_pvti(exp_dict)

    reps = exp_dict[BM_NUM_REP]
    for r in range(reps):
        time = execute(data, exp_dict)
        exp_dict[WEAK_TIME] = time

        pvio.write_dict_to_csv(exp_dict)

        # reset session to free memory
        pvs.ResetSession()

    # mode = corrected scaling
    filename_prefix =  exp_dict[OUT_DATA_PREFIX] + "_" + str(exp_dict[SEARCH_DESTINATION_FACTOR])
    filename = filename_prefix + "_work_scaled.pvti"
    exp_dict[DATA_FILENAME] = filename
    exp_dict[WEAK_MODE] = 'work scaling'

    data = pvio.read_pvti(exp_dict)

    for r in range(reps):
        time = execute(data, exp_dict)
        exp_dict[WEAK_TIME] = time

        pvio.write_dict_to_csv(exp_dict)

        # reset session to free memory
        pvs.ResetSession()


def scale(data, exp_dict, scaling_factor):
    if exp_dict[SEARCH_SCALING_METHOD] == 'resampling':
        return sc.resample_image(data, scaling_factor)
    elif exp_dict[SEARCH_SCALING_METHOD] == 'extent':
        return  sc.scale_by_extent(data, scaling_factor, original_dim=exp_dict[SEARCH_DATA_ORIGINAL_DIM]) # scaled data with the first estimate
    elif exp_dict[SEARCH_SCALING_METHOD] == 'replication':
        if exp_dict[BM_ALGO] == 'streamline':
            sc.replicate_vector(data, scaling_factor)
        if SEARCH_REPLICATION_SCALING_MODE in exp_dict.keys():
            return sc.replicate(data, scaling_factor, mode=exp_dict[SEARCH_REPLICATION_SCALING_MODE])
        return sc.replicate(data, scaling_factor)

    print("Scaling method not found - aborting", file=sys.stderr)
    return data


def execute(scaled_data, exp_dict, repetitions=1):
    if exp_dict[BM_ALGO] == 'contour':
        return alg.contour_execute(scaled_data, reps=repetitions, exp_dict=exp_dict)
    elif exp_dict[BM_ALGO] == 'volumerender':
        # return alg.volumerender_execute(scaled_data, reps=exp_dict[SEARCH_NUM_REP_SCALED], exp_dict=exp_dict)
        return alg.volumerender_distributed_execute(scaled_data, reps=repetitions, exp_dict=exp_dict)
    elif exp_dict[BM_ALGO] == 'contourtree':
        return alg.contourtree_execute(scaled_data, reps=repetitions, exp_dict=exp_dict)
    elif exp_dict[BM_ALGO] == 'streamline':
        return alg.streamlines_execute(scaled_data, reps=repetitions, exp_dict=exp_dict)

    print("algorithm not found - aborting", file=sys.stderr)
    return time
