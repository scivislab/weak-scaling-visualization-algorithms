import time
import paraview.simple as pvs
import numpy as np
import vtkmodules.all as vtk
from global_string_identifiers import *
import sys
import paraview.benchmark as pvb

generalSettings = pvs.GetSettingsProxy('GeneralSettings')
generalSettings.UseAcceleratedFilters = 0

pvb.logbase.maximize_logs()

ttk_loaded=False
vtkm_loaded=False

def load_vtkm():
    global vtkm_loaded 
    if not vtkm_loaded:
        pvs.LoadDistributedPlugin("AcceleratedAlgorithms", remote=True, ns=None)
        pvs.LoadDistributedPlugin("VTKmFilters", remote=True, ns=None)
        vtkm_loaded = True

def load_ttk():
    global ttk_loaded
    if not ttk_loaded:
        pvs.LoadDistributedPlugin("TopologyToolKit", remote=True, ns=None)
        ttk_loaded = True

def get_last_filter_exec_timer_per_rank(logs, filtername):
    log = ''.join([l.toString(True) for l in logs])
    log_per_rank = log.split('#RunMode')
    rank_times = []
    for rank in log_per_rank:
        exec_times = rank.split('seconds')
        exec_times.reverse()
        for l in exec_times:
            if filtername in l:
                maybe_seconds = l.split(',')[-1]
                try:
                    maybe_seconds = float(maybe_seconds)
                except ValueError:
                    maybe_seconds = -1.0
                rank_times.append(maybe_seconds)
                break
    return rank_times

def add_distributed_test(proxy, exp_dict):
    '''
    Add process id scalars for distributed debugging purposes
    '''
    processIdScalars1 = pvs.ProcessIdScalars(registrationName='ProcessIdScalars1', Input=proxy)
    exp_dict[DATA_FIELDNAME] = "ProcessId"
    pvs.UpdatePipeline(time=0.0,proxy=processIdScalars1)
    return processIdScalars1


def contour_execute(proxy, reps=1, median=True, exp_dict=dict()):
    '''
    Compute contour on proxy and takes median or mean of reps runs
    '''

    iso_values = [10.0]
    if IC_VALUES in  exp_dict.keys():
        iso_values = exp_dict[IC_VALUES]

    pvs.UpdatePipeline(time=0.0, proxy=proxy)
    # proxy = pvs.ProcessIdScalars(registrationName='ProcessIdScalars1', Input=proxy)

    # proxy = add_distributed_test(proxy, exp_dict)
    # iso_values=[0.5, 1.5, 2.5, 3.5]

    exec_times = []
    rank_times = []
    for i in range(reps):
        if exp_dict[IC_ALGORITHM]=='marchingcubes':
            contour1 = pvs.Contour(registrationName='Contour1', Input=proxy)
            contour1.ComputeNormals = 0
            contour1.ComputeGradients = 0
        elif exp_dict[IC_ALGORITHM]=='flyingedges':
            load_vtkm()
            contour1 = pvs.FlyingEdges3D(registrationName='Contour1', Input=proxy)
            contour1.ComputeNormals = 0
            contour1.ComputeGradients = 0
        elif exp_dict[IC_ALGORITHM]=='vtkm':
            load_vtkm()
            contour1 = pvs.VTKmContour(registrationName='Contour1', Input=proxy)

        contour1.ContourBy = ['POINTS', exp_dict[DATA_FIELDNAME]]
        contour1.ComputeScalars = 1
        contour1.Isosurfaces = iso_values

        start = time.time()
        pvs.UpdatePipeline(time=0.0, proxy=contour1)
        exec_times.append(time.time() - start)

        pvb.logbase.get_logs()
        rt = get_last_filter_exec_timer_per_rank(pvb.logbase.logs, 'Contour1')
        rank_times.append(rt)

        # if i == 0:
        #     pvs.SaveData(exp_dict[OUT_DATA_PREFIX]+'_distributedtest.pvtp', contour1)

        pvs.Delete(contour1)
        
    exp_dict['ranktimes'] = rank_times
    if median:
        return np.median(exec_times)
    return np.mean(exec_times)


def volumerender_execute(proxy, reps=1, median=True, exp_dict=dict()):
    '''
    Do volume rendering with rotation around object
    '''
    renWin = vtk.vtkRenderWindow()
    ren = vtk.vtkRenderer()

    renWin.SetMultiSamples(0)
    renWin.AddRenderer(ren)
    ren.GetActiveCamera().Azimuth(45.0)
    ren.GetActiveCamera().Roll(45.0)

    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetInterpolationType(vtk.VTK_LINEAR_INTERPOLATION)

    reader = pvs.FetchData(proxy)[0]
    reader.SetSpacing([1.0]*3)

    sc_range = proxy.GetDataInformation().GetArrayInformation(exp_dict[DATA_FIELDNAME],0).GetComponentRange(0)
    mid_range = (sc_range[1]-sc_range[0])/2+sc_range[0]

    # Prepare 1D Transfer Functions
    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(sc_range[0], 0.0, 0.0, 0.0)
    ctf.AddRGBPoint(mid_range, 1.0, 1.0, 1.0)
    ctf.AddRGBPoint(sc_range[1], 0.9, 0.1, 0.1)

    opacity = exp_dict[VR_OPACITY]
    pf = vtk.vtkPiecewiseFunction()
    pf.AddPoint(sc_range[0], 0.0)
    pf.AddPoint(sc_range[1], opacity)

    volumeProperty.SetScalarOpacity(pf)
    volumeProperty.SetColor(ctf)
    volumeProperty.SetShade(0)

    mapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
    mapper.SetInputData(reader)

    # Modify the shader  ###to color based on the depth of the translucent voxel
    shaderProperty = vtk.vtkOpenGLShaderProperty()

    # HACK: used to crash the shader that it outputs its current source code
    # shaderProperty.AddFragmentShaderReplacement("//VTK::", True, "crap_text", False );  

    volume = vtk.vtkVolume()
    volume.SetShaderProperty(shaderProperty)
    volume.SetMapper(mapper)
    volume.SetProperty(volumeProperty)

    resolution = exp_dict[VR_IMAGE_SIZE]
    renWin.SetSize(resolution[0], resolution[1])
    ren.AddVolume(volume)
    ren.ResetCameraScreenSpace()

    # remove early ray termination from ray
    if not exp_dict[VR_ERT]:
        shaderProperty.AddFragmentShaderReplacement("//VTK::Terminate::Impl", True,
                                                    "if(any(greaterThan(max(g_dirStep, vec3(0.0))*(g_dataPos - in_texMax[0]),vec3(0.0))) ||"
                                                    "  any(greaterThan(min(g_dirStep, vec3(0.0))*(g_dataPos - in_texMin[0]),vec3(0.0))))"
                                                    "{"
                                                    "break;"      
                                                    "}", 
                                                    False);
    exec_times = []
    num_rep = reps
    steps = 12

    for j in range(num_rep):
        start = time.time()
        for i in range(steps):
            ren.GetActiveCamera().Azimuth(-360 / steps)
            renWin.Render()
        end  = time.time()
        exec_times.append((end-start)/steps)

    if median:
        return np.median(exec_times)
    return np.mean(exec_times)


def volumerender_distributed_execute(proxy, reps=1, median=True, exp_dict=dict()):
    '''
    Do volume rendering with rotation around object
    '''
    pvs.UpdatePipeline(time=0.0, proxy=proxy)
    
    # proxy = add_distributed_test(proxy, exp_dict)

    extent = proxy.GetDataInformation().GetExtent()
    bounds = proxy.GetDataInformation().GetBounds()
    cor = [(extent[1]-extent[0])/2.0, (extent[3]-extent[2])/2.0,  (extent[5]-extent[4])/2.0]
    data_range =  proxy.GetDataInformation().GetArrayInformation(exp_dict[DATA_FIELDNAME],0).GetComponentRange(0)

    cell_width = bounds[1] - bounds[0] / (extent[1] - extent[0])
    scalar_opacity_unit_distance = cell_width*(3**0.5)

    renderView1 = pvs.CreateView('RenderView')
    renderView1.ViewSize = exp_dict[VR_IMAGE_SIZE]
    renderView1.AxesGrid = 'GridAxes3DActor'
    renderView1.CenterOfRotation = cor
    renderView1.StereoType = 'Crystal Eyes'
    renderView1.CameraFocalDisk = 1.0
    renderView1.CameraParallelScale = 220.83647796503186

    opacity_PWF = pvs.GetOpacityTransferFunction(exp_dict[DATA_FIELDNAME])
    opacity_PWF.Points = [data_range[0], 0.0, 0.5, 0.0, data_range[1], exp_dict[VR_OPACITY], 0.5, 0.0]
    opacity_PWF.ScalarRangeInitialized = 1

    dataDisplay = pvs.Show(proxy, renderView1, 'UniformGridRepresentation')
    dataDisplay.Representation = 'Volume'
    dataDisplay.ColorArrayName = ['POINTS', exp_dict[DATA_FIELDNAME]]
    dataDisplay.DataAxesGrid = 'GridAxesRepresentation'
    dataDisplay.PolarAxes = 'PolarAxesRepresentation'
    dataDisplay.ScalarOpacityUnitDistance = scalar_opacity_unit_distance
    dataDisplay.OpacityArrayName = ['POINTS', exp_dict[DATA_FIELDNAME]]
    dataDisplay.ColorArray2Name = ['POINTS', exp_dict[DATA_FIELDNAME]]
    dataDisplay.ScalarOpacityFunction = opacity_PWF

    # set scalar coloring
    pvs.ColorBy(dataDisplay, ('POINTS', exp_dict[DATA_FIELDNAME]))

    # reset view to fit data
    renderView1.ResetCamera(False)

    # pvs.SaveScreenshot(exp_dict[OUT_DATA_PREFIX] + '_' + str(exp_dict[SEARCH_DESTINATION_FACTOR])  + '_testrender.png',renderView1)

    exec_times = []
    rank_times = []
    
    images_per_round = 12
    for i in range(reps):
        for j in range(images_per_round):
            start = time.time()
            renderView1.AdjustAzimuth(360/images_per_round)
            pvs.Render(renderView1)
            exec_times.append(time.time()-start)

            pvb.logbase.get_logs()
            rt = get_last_filter_exec_timer_per_rank(pvb.logbase.logs, 'Still Render')
            rank_times.append(rt)


    exp_dict['ranktimes'] = rank_times
    if median:
        return np.median(exec_times)
    return np.mean(exec_times)

def contourtree_execute(proxy, reps=1, median=True, exp_dict=dict()):
    '''
    Compute contour on proxy and takes median or mean of reps runs
    '''

    pvs.UpdatePipeline(time=0.0, proxy=proxy)
    # proxy = pvs.ProcessIdScalars(registrationName='ProcessIdScalars1', Input=proxy)

    exec_times = []
    rank_times = []
    for i in range(reps):
        if exp_dict[CT_ALGORITHM] == "ttk":
            load_ttk()

            # create a new 'TTK Merge and Contour Tree (FTM)'
            contourTree1 = pvs.TTKMergeandContourTreeFTM(registrationName='contourTree1', Input=proxy)
            contourTree1.ScalarField = ['POINTS', exp_dict[DATA_FIELDNAME]]
            contourTree1.InputOffsetField = ['POINTS', exp_dict[DATA_FIELDNAME]]
            contourTree1.ForceInputOffsetScalarField = 0
            contourTree1.TreeType = 'Contour Tree'
            contourTree1.ArcSampling = 0
            contourTree1.Deterministicarcandnodeidentifiers = 1
            contourTree1.AdvancedStatistics = 0
            contourTree1.UseAllCores = 1
            contourTree1.ThreadNumber = 12
            contourTree1.DebugLevel = 0
            contourTree1.Cache = 0.2
        elif exp_dict[CT_ALGORITHM] == "vtkm":
            load_vtkm()
            contourTree1 = pvs.VTKmContourTree(registrationName='contourTree1', Input=proxy)
            contourTree1.ScalarField = ['POINTS', exp_dict[DATA_FIELDNAME]]
        else:
            print("Contourtree algorithm " + str(exp_dict[CT_ALGORITHM]) + " is not a valid option. Aborting.")
            quit()

        start = time.time()
        pvs.UpdatePipeline(time=0.0, proxy=contourTree1)
        exec_times.append(time.time() - start)

        pvb.logbase.get_logs()
        rt = get_last_filter_exec_timer_per_rank(pvb.logbase.logs, 'ContourTree1')
        rank_times.append(rt)

        # if i == 0:
        #     pvs.SaveData(exp_dict[OUT_DATA_PREFIX]+'_distributedtest2.pvti', contourTree1)

        pvs.Delete(contourTree1)

    exp_dict['ranktimes'] = rank_times
    if median:
        return np.median(exec_times)
    return np.mean(exec_times)


def streamlines_execute(proxy, reps=1, median=True, exp_dict=dict()):
    '''
    Compute contour on proxy and takes median or mean of reps runs
    '''

    pvs.UpdatePipeline(time=0.0, proxy=proxy)
    bounds = proxy.GetDataInformation().GetBounds()
    max_length = max(bounds[1] - bounds[0], max(bounds[3] - bounds[2], bounds[5]- bounds[4]))
    number = 4000
    ratio = 1
    if exp_dict[SL_MODE] == 'fixed_density':
        ratio = 1000
    elif exp_dict[SL_MODE] == 'fixed_number':
        ratio = int(proxy.GetDataInformation().GetNumberOfPoints() / number)
        print(ratio)
    else:
        print('Error: invalid streamline seeding mode', file=sys.stderr)

    maskPoints = pvs.MaskPoints(registrationName='maskPoints', Input=proxy)
    maskPoints.OnRatio = ratio
    maskPoints.MaximumNumberofPoints = number
    maskPoints.ProportionallyDistributeMaximumNumberOfPoints = 0
    maskPoints.Offset = 0
    maskPoints.RandomSampling = 0
    maskPoints.RandomSamplingMode = 'Randomized Id Strides'
    maskPoints.GenerateVertices = 0
    maskPoints.SingleVertexPerCell = 0
    pvs.UpdatePipeline(time=0.0, proxy=maskPoints)

    exec_times = []
    for i in range(reps):
        streamline = pvs.StreamTracerWithCustomSource(registrationName='maskPoints', Input=proxy, SeedSource=maskPoints)
        streamline.Vectors = ['POINTS', exp_dict[DATA_FIELDNAME]]
        streamline.MaximumStreamlineLength = max_length
        streamline.InterpolatorType = 'Interpolator with Point Locator'
        streamline.SurfaceStreamlines = 0
        streamline.IntegrationDirection = 'BOTH'
        streamline.IntegratorType = 'Runge-Kutta 4-5'
        streamline.IntegrationStepUnit = 'Cell Length'
        streamline.InitialStepLength = 0.2
        streamline.MinimumStepLength = 0.01
        streamline.MaximumStepLength = 0.5
        streamline.MaximumSteps = 2000
        streamline.TerminalSpeed = 1e-12
        streamline.MaximumError = 1e-06
        streamline.ComputeVorticity = 1

        start = time.time()
        pvs.UpdatePipeline(time=0.0, proxy=streamline)
        exec_times.append(time.time() - start)

        pvs.Delete(streamline)
    if median:
        return np.median(exec_times)
    return np.mean(exec_times)
