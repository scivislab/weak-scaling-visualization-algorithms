''' Utility functions for scaling workload experiments
'''

# from paraview.simple import *
import paraview.simple as pvs
from global_string_identifiers import *
import numpy as np
import math
import pv_io as pvio

def resample_image(proxy_in, scaling_factor):
    """
    Resamples a vtkImageData to another resolution specified by the factor.

    Returns a proxy for paraview pipelines yielding the resampled image.
    This is done via the vtkResampleToImageFilter. The scaling factor describes the
    increase in the number of cells overall meaning its third root is used for
    mulitplication with the axis dimension

    Parameters
    ----------
    proxyIn : vtkPVProxy
        ParaView proxy from which input image is retrieved.
    scalingFactor : float
        scalingFactor with which the extent is multiplied.
    samplingDim : [float, float, float]
        List of size 3, containing the target dimensions for the sampling.
        Is used only if scalingFactor is not given as parameter.

    Returns
    -------
    proxy
        A ParaView proxy which can be used to write data or connect to other pipeline 
        modules with the new resampled image.

    """
    # sf = scaling_factor**(1/3)
    if float(scaling_factor) < 0.0:
        sf = -pow(abs(float(scaling_factor)), 1.0/3.0)
    else:
        sf = pow(float(scaling_factor), 1.0/3.0)

    resampleToImage1 = pvs.ResampleToImage(registrationName='ResampleToImage1', Input=proxy_in)
    extent_orig = proxy_in.GetDataInformation().GetExtent()
    sampling_dim_orig = [extent_orig[1]-extent_orig[0]+1, extent_orig[3]-extent_orig[2]+1, extent_orig[5]-extent_orig[4]+1]
    sampling_dim_low = [max(int(x*sf),2) for x in sampling_dim_orig]

    resampleToImage1.UseInputBounds = 0
    resampleToImage1.SamplingDimensions = sampling_dim_low
    pvs.UpdatePipeline(time=0.0, proxy=resampleToImage1)
    return resampleToImage1


def replicate(proxy_in, scaling_factor, mode='line'):
    '''
    This can be done by reading the data set multiple times and change its extent
        # 0. prime factorization of factor (only feasible if scaling factor is integer)
        1. read data multiple times
        2. change extent so that it lines up
        3. group data set 
        4. resample to image
        (5. support replication in box rather than line)
    '''
    if mode =='box':
        # box mode
        orig_extent = proxy_in.GetDataInformation().GetExtent()
        orig_bounds = proxy_in.GetDataInformation().GetBounds()
        whole_extent = list(orig_extent)
        x_increment = orig_extent[1]-orig_extent[0]
        y_increment = orig_extent[3]-orig_extent[2]
        z_increment = orig_extent[5]-orig_extent[4]
        origin_x_increment = orig_bounds[1]-orig_bounds[0]
        origin_y_increment = orig_bounds[3]-orig_bounds[2]
        origin_z_increment = orig_bounds[5]-orig_bounds[4]
        group_proxies=[proxy_in]

        # sf = scaling_factor**(1/3)
        if float(scaling_factor) < 0:
            sf = -pow(abs(float(scaling_factor)), 1.0/3.0)
        else:
            sf = pow(float(scaling_factor), 1.0/3.0)
        ceil_scaling_factor = int(max(math.ceil(sf),1))

        for i in range(ceil_scaling_factor):
            for j in range(ceil_scaling_factor):
                for k in range(ceil_scaling_factor):
                    if i==0 and j==0 and k==0:
                        continue
                    orig_extent_string = ','.join(map(str,orig_extent))
                    programmableFilter1 = pvs.ProgrammableFilter(registrationName='ProgrammableFilter' + str(i), Input=proxy_in)
                    programmableFilter1.OutputDataSetType = 'Same as Input'
                    programmableFilter1.Script = """input0 = inputs[0]
origin = list(input0.GetOrigin())
origin[0]+=""" + str(i*(origin_x_increment)) + """
origin[1]+=""" + str(j*(origin_y_increment)) + """
origin[2]+=""" + str(k*(origin_z_increment)) + """
output.SetOrigin(origin)"""
                    programmableFilter1.RequestInformationScript = """# RequestInformation !!! NEED TO ADJUST EXTENT FOR OWN DAtA
executive = self.GetExecutive() 
inInfo = executive.GetInputInformation(0, 0)
inInfo.Set(executive.WHOLE_EXTENT(), """ + orig_extent_string + """)"""
                    programmableFilter1.RequestUpdateExtentScript = """# RequestInformation !!! NEED TO ADJUST EXTENT FOR OWN DAtA
executive = self.GetExecutive() 
inInfo = executive.GetInputInformation(0, 0)
inInfo.Set(executive.UPDATE_EXTENT(), """ + orig_extent_string + """)"""
                    programmableFilter1.CopyArrays = 1
                    programmableFilter1.PythonPath = ''
                    group_proxies.append(programmableFilter1)
                    pvs.UpdatePipeline(time=0.0, proxy=group_proxies[-1])

        whole_extent[1] += (ceil_scaling_factor-1)*(x_increment + 1)
        whole_extent[3] += (ceil_scaling_factor-1)*(y_increment + 1)
        whole_extent[5] += (ceil_scaling_factor-1)*(z_increment + 1)
        
        groupDatasets1 = pvs.GroupDatasets(registrationName='GroupDatasets1', Input=group_proxies)

        x_sampling_dim = whole_extent[1]-whole_extent[0]+1
        y_sampling_dim = whole_extent[3]-whole_extent[2]+1
        z_sampling_dim = whole_extent[5]-whole_extent[4]+1
        corrected_x_sampling_dim = max(int(x_sampling_dim / float(ceil_scaling_factor) * sf),2)
        corrected_y_sampling_dim = max(int(y_sampling_dim / float(ceil_scaling_factor) * sf),2)
        corrected_z_sampling_dim = max(int(z_sampling_dim / float(ceil_scaling_factor) * sf),2)

        new_extent = whole_extent.copy()
        new_extent[1] = whole_extent[0] + corrected_x_sampling_dim -1
        new_extent[3] = whole_extent[2] + corrected_y_sampling_dim -1
        new_extent[5] = whole_extent[4] + corrected_z_sampling_dim -1
        bounds_factors = np.nan_to_num(np.divide(new_extent[1::2], orig_extent[1::2]))
        origin_increments = [origin_x_increment, origin_y_increment, origin_z_increment]
        scaled_increments = np.multiply(bounds_factors, origin_increments)
        new_bounds = list(orig_bounds).copy()
        new_bounds[1::2] = np.add(orig_bounds[::2], scaled_increments)

        resampleToImage1 = pvs.ResampleToImage(registrationName='ResampleToImage1', Input=groupDatasets1)
        resampleToImage1.UseInputBounds = 0
        resampleToImage1.SamplingDimensions = [corrected_x_sampling_dim, corrected_y_sampling_dim, corrected_z_sampling_dim]
        resampleToImage1.SamplingBounds = new_bounds

        pvs.UpdatePipeline(time=0.0, proxy=resampleToImage1)
        for p in group_proxies:
            pvs.Delete(p)
        pvs.Delete(groupDatasets1)
        return resampleToImage1

    if mode =='line':
        # line mode
        orig_extent = proxy_in.GetDataInformation().GetExtent()
        orig_bounds = proxy_in.GetDataInformation().GetBounds()
        whole_extent = list(orig_extent)
        increment = orig_extent[1]-orig_extent[0]
        origin_increment = orig_bounds[1]-orig_bounds[0]
        group_proxies=[proxy_in]
        ceil_scaling_factor = int(math.ceil(scaling_factor))
        for i in range(ceil_scaling_factor-1):
            # programmable filter origin translate
            orig_extent_string = ','.join(map(str,orig_extent))
            programmableFilter1 = pvs.ProgrammableFilter(registrationName='ProgrammableFilter' + str(i), Input=proxy_in)
            programmableFilter1.OutputDataSetType = 'Same as Input'
            programmableFilter1.Script = """input0 = inputs[0]
origin = list(input0.GetOrigin())
origin[0]+=""" + str((i+1)*(origin_increment)) + """
output.SetOrigin(origin)"""
            programmableFilter1.RequestInformationScript = """# RequestInformation !!! NEED TO ADJUST EXTENT FOR OWN DAtA
executive = self.GetExecutive() 
inInfo = executive.GetInputInformation(0, 0)
inInfo.Set(executive.WHOLE_EXTENT(), """ + orig_extent_string + """)"""
            programmableFilter1.RequestUpdateExtentScript = """# RequestInformation !!! NEED TO ADJUST EXTENT FOR OWN DAtA
executive = self.GetExecutive() 
inInfo = executive.GetInputInformation(0, 0)
inInfo.Set(executive.UPDATE_EXTENT(), """ + orig_extent_string + """)"""
            programmableFilter1.CopyArrays = 1
            programmableFilter1.PythonPath = ''

            pvs.UpdatePipeline(time=0.0, proxy=programmableFilter1)
            group_proxies.append(programmableFilter1)
            whole_extent[1] += increment+1
        
        groupDatasets1 = pvs.GroupDatasets(registrationName='GroupDatasets1', Input=group_proxies)

        x_sampling_dim = whole_extent[1]-whole_extent[0]+1
        corrected_x_sampling_dim = max(int(x_sampling_dim / float(ceil_scaling_factor) * scaling_factor),2)

        new_extent = whole_extent.copy()
        new_extent[1] = whole_extent[0] + corrected_x_sampling_dim -1
        bounds_factor = new_extent[1] / increment
        scaled_increment = bounds_factor * origin_increment
        new_bounds = list(orig_bounds).copy()
        new_bounds[1] = orig_bounds[0] + scaled_increment

        resampleToImage1 = pvs.ResampleToImage(registrationName='ResampleToImage1', Input=groupDatasets1)
        resampleToImage1.UseInputBounds = 0
        resampleToImage1.SamplingDimensions = [corrected_x_sampling_dim, orig_extent[3]-orig_extent[2]+1, orig_extent[5]-orig_extent[4]+1]
        resampleToImage1.SamplingBounds = new_bounds

        pvs.UpdatePipeline(time=0.0, proxy=resampleToImage1)
        for p in group_proxies:
            pvs.Delete(p)
        pvs.Delete(groupDatasets1)
        return resampleToImage1

        
def check_scale_by_extent(proxy_in, scaling_factor, original_dim=[100,100,100]):
    '''
    This function checks whether the scaling factor does not exceed the largest extent.
    '''
    if float(scaling_factor) < 0:
        sf = -pow(abs(float(scaling_factor)), 1.0/3.0)
    else:
        sf = pow(float(scaling_factor), 1.0/3.0)

    whole_extent = proxy_in.GetDataInformation().GetExtent()
    whole_dim = [whole_extent[1]-whole_extent[0]+1, whole_extent[3]-whole_extent[2]+1, whole_extent[5]-whole_extent[4]+1]
    new_dim = [max(int(x*sf),2) for x in original_dim]
    return any([w-n < 0 for w,n in zip(whole_dim, new_dim)])


def scale_by_extent(proxy_in, scaling_factor, original_dim=[100,100,100]):
    """
    scales data by extracting subvolumes. The proxy here has to be the largest data set (whole data set).
    The original data set is specified via its dimension.


    Parameters
    ----------
    proxy_in : vtkPVProxy
        ParaView proxy from which input image is retrieved.
    scalingFactor : float
        scalingFactor with which the extent is multiplied.
    original_dim : [int, int, int]
        List of size 3, containing the original dimensions for the sampling.

    Returns
    -------
    proxy
        A ParaView proxy which can be used to write data or connect to other pipeline 
        modules with the new resampled image.

    """
    if float(scaling_factor) < 0:
        sf = -pow(abs(float(scaling_factor)), 1.0/3.0)
    else:
        sf = pow(float(scaling_factor), 1.0/3.0)

    whole_extent = proxy_in.GetDataInformation().GetExtent()
    whole_dim = [whole_extent[1]-whole_extent[0]+1, whole_extent[3]-whole_extent[2]+1, whole_extent[5]-whole_extent[4]+1]

    new_dim = [max(int(x*sf),2) for x in original_dim]
    offset_dim  = np.divide(np.subtract(whole_dim, new_dim), 2).astype(int)

    new_extent = [whole_extent[0],whole_extent[0]+new_dim[0]-1,whole_extent[2],whole_extent[2]+new_dim[1]-1,whole_extent[4],whole_extent[4]+new_dim[2]-1]
    new_extent = np.add(new_extent, [x for pair in zip(offset_dim,offset_dim) for x in pair])
    if any([w-n < 0 for w,n in zip(whole_dim, new_dim)]):
        print("WARNING: scaled data set exceeds whole extent")
        print(whole_extent, new_extent, whole_dim, new_dim)
        return proxy_in

    # compute the new dimension
    extractSubset1 = pvs.ExtractSubset(registrationName='ExtractSubset1', Input=proxy_in)
    extractSubset1.VOI = new_extent
    extractSubset1.SampleRateI = 1
    extractSubset1.SampleRateJ = 1
    extractSubset1.SampleRateK = 1
    extractSubset1.IncludeBoundary = 1
    pvs.UpdatePipeline(time=0.0, proxy=extractSubset1)
    return extractSubset1


def replicate_vector(proxy_in, scaling_factor, mode='line'):
    '''
    This can be done by reading the data set multiple times and change its extent
        # 0. prime factorization of factor (only feasible if scaling factor is integer)
        1. read data multiple times
        2. change extent so that it lines up
        3. group data set 
        4. resample to image
        (5. support replication in box rather than line)
    '''
    if mode == 'line':
        print('line mode for vector scaling currently not supported')
        return proxy_in

    # box mode
    orig_extent = proxy_in.GetDataInformation().GetExtent()
    orig_bounds = proxy_in.GetDataInformation().GetBounds()
    whole_extent = list(orig_extent)
    x_increment = orig_extent[1]-orig_extent[0]
    y_increment = orig_extent[3]-orig_extent[2]
    z_increment = orig_extent[5]-orig_extent[4]
    origin_x_increment = orig_bounds[1]-orig_bounds[0]
    origin_y_increment = orig_bounds[3]-orig_bounds[2]
    origin_z_increment = orig_bounds[5]-orig_bounds[4]

    # create a new 'Extract Component'
    extractComponent1 = pvs.ExtractComponent(registrationName='ExtractComponent1', Input=proxy_in)
    extractComponent1.Component = 'X'
    extractComponent1.InputArray = ['POINTS', 'ImageFile']
    extractComponent1.OutputArrayName = 'vx'

    # create a new 'Extract Component'
    extractComponent2 = pvs.ExtractComponent(registrationName='ExtractComponent2', Input=proxy_in)
    extractComponent2.InputArray = ['POINTS', 'ImageFile']
    extractComponent2.Component = 'Y'
    extractComponent2.OutputArrayName = 'vy'

    # create a new 'Extract Component'
    extractComponent3 = pvs.ExtractComponent(registrationName='ExtractComponent3', Input=proxy_in)
    extractComponent3.InputArray = ['POINTS', 'ImageFile']
    extractComponent3.Component = 'Z'
    extractComponent3.OutputArrayName = 'vz'

    # create a new 'Append Attributes'
    appendAttributes1 = pvs.AppendAttributes(registrationName='AppendAttributes1', Input=[extractComponent2, extractComponent3, extractComponent1])
    pvs.UpdatePipeline(time=0.0, proxy=appendAttributes1)

    group_proxies=[appendAttributes1]

    if float(scaling_factor) < 0:
        sf = -pow(abs(float(scaling_factor)), 1.0/3.0)
    else:
        sf = pow(float(scaling_factor), 1.0/3.0)
    ceil_scaling_factor = max(math.ceil(sf),1.0)

    for i in range(ceil_scaling_factor):
        for j in range(ceil_scaling_factor):
            for k in range(ceil_scaling_factor):
                if i==0 and j==0 and k==0:
                    continue
                # create a new 'Transform'
                transform = pvs.Transform(registrationName='Transform'+str(i)+str(j)+str(k), Input=appendAttributes1)
                transform.Transform = 'Transform'
                transform.TransformAllInputVectors = 0
                transform.Transform.Translate = [(i+i%2)*(origin_x_increment), (j+j%2)*(origin_y_increment), (k+k%2)*(origin_z_increment)]
                scaleArray = [pow(-1,i%2), pow(-1,j%2), pow(-1,k%2)] # if i is odd than the scale has to be inverted meaning the component has to be -1 instead of 1,   alt:  int(not i%2) or -1
                transform.Transform.Scale = scaleArray

                group_proxies.append(transform)
                pvs.UpdatePipeline(time=0.0, proxy=group_proxies[-1])

    whole_extent[1] += (ceil_scaling_factor-1)*(x_increment + 1)
    whole_extent[3] += (ceil_scaling_factor-1)*(y_increment + 1)
    whole_extent[5] += (ceil_scaling_factor-1)*(z_increment + 1)
    
    groupDatasets1 = pvs.GroupDatasets(registrationName='GroupDatasets1', Input=group_proxies)
    passArrays1 = pvs.PassArrays(registrationName='PassArrays1', Input=groupDatasets1)
    passArrays1.PointDataArrays = ['vx','vy','vz']
    passArrays1.CellDataArrays = []
    pvs.UpdatePipeline(time=0.0, proxy=passArrays1)

    mergeVectorComponents1 = pvs.MergeVectorComponents(registrationName='MergeVectorComponents1', Input=passArrays1)
    mergeVectorComponents1.XArray = 'vx'
    mergeVectorComponents1.YArray = 'vy'
    mergeVectorComponents1.ZArray = 'vz'
    mergeVectorComponents1.OutputVectorName = 'ImageFile'
    pvs.UpdatePipeline(time=0.0, proxy=mergeVectorComponents1)

    x_sampling_dim = whole_extent[1]-whole_extent[0]+1
    y_sampling_dim = whole_extent[3]-whole_extent[2]+1
    z_sampling_dim = whole_extent[5]-whole_extent[4]+1
    corrected_x_sampling_dim = max(int(x_sampling_dim / float(ceil_scaling_factor) * sf),2)
    corrected_y_sampling_dim = max(int(y_sampling_dim / float(ceil_scaling_factor) * sf),2)
    corrected_z_sampling_dim = max(int(z_sampling_dim / float(ceil_scaling_factor) * sf),2)

    new_extent = whole_extent.copy()
    new_extent[1] = whole_extent[0] + corrected_x_sampling_dim -1
    new_extent[3] = whole_extent[2] + corrected_y_sampling_dim -1
    new_extent[5] = whole_extent[4] + corrected_z_sampling_dim -1
    bounds_factors = np.nan_to_num(np.divide(new_extent[1::2], orig_extent[1::2]))
    origin_increments = [origin_x_increment, origin_y_increment, origin_z_increment]
    scaled_increments = np.multiply(bounds_factors, origin_increments)
    new_bounds = list(orig_bounds).copy()
    new_bounds[1::2] = np.add(orig_bounds[::2], scaled_increments)

    resampleToImage1 = pvs.ResampleToImage(registrationName='ResampleToImage1', Input=mergeVectorComponents1)
    resampleToImage1.UseInputBounds = 0
    resampleToImage1.SamplingDimensions = [corrected_x_sampling_dim, corrected_y_sampling_dim, corrected_z_sampling_dim]
    resampleToImage1.SamplingBounds = new_bounds

    pvs.UpdatePipeline(time=0.0, proxy=resampleToImage1)
    for p in group_proxies:
        pvs.Delete(p)
    pvs.Delete(groupDatasets1)
    pvs.Delete(mergeVectorComponents1)
    return resampleToImage1