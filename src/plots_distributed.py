import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os.path as op
import sys
import numpy as np
from matplotlib.markers import MarkerStyle
from matplotlib.ticker import *
import ast
import math

from global_string_identifiers import *

# read data path
if len(sys.argv) < 2:
    print("no data path as arg", file=sys.stderr)
data_path = sys.argv[1]

# get name of algo
if len(sys.argv) < 3:
    print("no algo name", file=sys.stderr)
algo_name = sys.argv[2]

# read data set
if len(sys.argv) < 4:
    print("no data set as arg", file=sys.stderr)
data_name = sys.argv[3]

format = ".pdf"
sns.set_style('whitegrid')
plt.rcParams["legend.labelspacing"] = 0.2
plt.rcParams["font.family"] = ['Linux Libertine O']
plt.rcParams["font.size"] = 14
short_legend = False
global_alpha=1.0
# angles=[0,0,30,30,60,60]
# linestyles_i=[(1,2), (4,5)]
# linestyles=[(4,5), (18, 2)]
linestyles_i=[(1,2), (3,4)]
linestyles=[(3,4), (1,0)]
short_legend = True
marker_size = 0

do_speedup_plots=False

x_label='number of cores'

rgba_to_method = {(0.12156862745098039, 0.4666666666666667, 0.7058823529411765): 'resampling',
                  (1.0, 0.4980392156862745, 0.054901960784313725): 'replication',
                  (0.17254901960784313, 0.6274509803921569, 0.17254901960784313): 'extent',}

method_to_angle = {'resampling': 60.0,
                   'replication': 90.0,
                   'extent': 120.0,
                   }

def create_markers(lines):
    lcount = 0
    for line in lines:
        angle = method_to_angle[rgba_to_method[line.get_color()]]
        marker_path = [(math.cos(math.radians(angle)),math.sin(math.radians(angle))),(math.cos(math.radians(angle+180)),math.sin(math.radians(angle+180)))]
        marker_style = MarkerStyle(marker_path, fillstyle='full')
        line.set_marker(marker_style)
        line.set_markeredgecolor(line.get_color())
        line.set_markeredgewidth(1.5)
        line.set_markersize(15)
        lcount += 1

def create_error_markers(num_err_lines, ax):
    if num_err_lines <= 0:
        return

    for line in ax.lines[-num_err_lines:]:
        if line.get_color() not in rgba_to_method.keys():
            continue
        angle = method_to_angle[rgba_to_method[line.get_color()]]
        marker_style = MarkerStyle((4,0,angle), fillstyle='none')
        line.set_marker(marker_style)
        line.set_markeredgecolor(line.get_color())
        line.set_markeredgewidth(1)
        line.set_markersize(20)
        if angle == 90.0:
            line.set_markersize(14)
            line.set_markersize(20)

def create_legend(ax):
    # remove duplicates
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    uhandles = [h for h,_ in unique]
    ulabels = [l for _,l in unique]

    ax.legend(uhandles[-2:], ulabels[-2:], markerscale=marker_size)

    if not short_legend:
        for h in uhandles[1:4]:
            angle = method_to_angle[rgba_to_method[h.get_color()]]
            marker_path = [(math.cos(math.radians(angle)),math.sin(math.radians(angle))),(math.cos(math.radians(angle+180)),math.sin(math.radians(angle+180)))]
            marker_style = MarkerStyle(marker_path, fillstyle='full')
            h.set_markeredgecolor(h.get_color())
            h.set_markeredgewidth(1.5)
            h.set_markersize(15)
            h.set_marker(marker_style)
        ax.legend(uhandles, ulabels, markerscale=1.0)



filename = data_path + '/' + algo_name + '_weak_' + data_name + ".csv"
dataprop_filename = data_path + "/" + algo_name + "_data_" + data_name + ".csv"

# weak scaling vs input scaling plots
if (op.exists(filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df['ranktimes'] = df['ranktimes'].apply(ast.literal_eval)
    df = df.explode('ranktimes')
    df['max_rank_time'] = df['ranktimes'].apply(max)

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)
    
    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])
    res[SEARCH_SCALING_FACTOR] = res[SEARCH_SCALING_FACTOR].where(res[WEAK_MODE]!='input scaling', res[SEARCH_DESTINATION_FACTOR])

    res['data scaling method'] = res[SEARCH_SCALING_METHOD]

    # filter all weak scaling point with larger error
    res['relative_error'] = res[SEARCH_ERROR] / res[SEARCH_DESTINATION_FACTOR]
    large_err = res[((res['relative_error'] >= 0.05) | (res['relative_error'] <= -0.05)) & (res[WEAK_MODE]!='input scaling')]

    # plot data
    fig, ax = plt.subplots(1,1)

    ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y='max_rank_time', hue='data scaling method',hue_order=['resampling', 'replication', 'extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], dashes=linestyles, ms=10, alpha=global_alpha)
    # ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y=WEAK_TIME, hue='data scaling method',hue_order=['resampling', 'replication', 'extent'], style=WEAK_MODE, markers=['d','d'], dashes=linestyles, ms=10, alpha=global_alpha)

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_markers(ax.lines[:6])

    create_legend(ax)

    if short_legend:
        if 'perlin' in data_name:
            sns.move_legend(ax, loc=7, bbox_to_anchor=(0.65, 0.55, 0.35, 0.3), markerscale=marker_size) # manual placement for perlin noise plots

    # add error markers
    tmp_num_lines = len(ax.lines)
    # ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y='max_rank_time', hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, ms=10, linewidth=0.1, errorbar=("pi", 100), legend=None, alpha=global_alpha)
    # ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y=WEAK_TIME, hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, markers=['X'], ms=10, linewidth=0.1, errorbar=None, legend=None, alpha=global_alpha)
    ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y='max_rank_time', hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], ms=10, linewidth=0.1, legend=None, alpha=global_alpha)
    num_err_lines = len(ax.lines) - tmp_num_lines
    create_error_markers(num_err_lines, ax)

    # axis label
    ax.set(xlabel='number of ranks', ylabel='execution time in seconds')

    # add x ticks at core counts
    xticks = list(set(df[SEARCH_DESTINATION_FACTOR]))
    xticks.sort()
    ax.set_xticks(xticks, labels=xticks)

    xticks_minor = [x*8 for x in xticks]

    ax2 = ax.twiny()  # Creates a twin axis sharing the same y-axis
    ax2.grid(False)
    ax2.set_xlim(ax.get_xlim()) 
    ax2.set_xticks(xticks, labels=xticks_minor)
    ax2.set_frame_on(False)
    ax2.set_xlabel("number of cores")
    
    plt.savefig( data_path + "/" + algo_name + "_" + data_name + format, bbox_inches='tight')


# weak scaling vs input scaling plots - load balance corrected
if (op.exists(filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df['ranktimes'] = df['ranktimes'].apply(ast.literal_eval)
    df = df.explode('ranktimes')
    df['mean_rank_time'] = df['ranktimes'].apply(np.mean)

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)
    
    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])
    res[SEARCH_SCALING_FACTOR] = res[SEARCH_SCALING_FACTOR].where(res[WEAK_MODE]!='input scaling', res[SEARCH_DESTINATION_FACTOR])
    res['data scaling method'] = res[SEARCH_SCALING_METHOD]

    # filter all weak scaling point with larger error
    res['relative_error'] = res[SEARCH_ERROR] / res[SEARCH_DESTINATION_FACTOR]
    large_err = res[((res['relative_error'] >= 0.05) | (res['relative_error'] <= -0.05)) & (res[WEAK_MODE]!='input scaling')]

    # plot data
    fig, ax = plt.subplots(1,1)

    ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y='mean_rank_time', hue='data scaling method',hue_order=['resampling', 'replication', 'extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], dashes=linestyles, ms=10, alpha=global_alpha)

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_markers(ax.lines[:6])

    create_legend(ax)

    if short_legend:
        if 'perlin' in data_name:
            sns.move_legend(ax, loc=7, bbox_to_anchor=(0.65, 0.55, 0.35, 0.3), markerscale=marker_size) # manual placement for perlin noise plots

    # add error markers
    tmp_num_lines = len(ax.lines)
    ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y='mean_rank_time', hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], ms=10, linewidth=0.1, errorbar=None, legend=None, alpha=global_alpha)
    num_err_lines = len(ax.lines) - tmp_num_lines
    create_error_markers(num_err_lines, ax)

    # axis label
    ax.set(xlabel='number of ranks', ylabel='execution time in seconds averaged over all ranks')

    # add x ticks at core counts
    xticks = list(set(df[SEARCH_DESTINATION_FACTOR]))
    xticks.sort()
    ax.set_xticks(xticks, labels=xticks)

    xticks_minor = [x*8 for x in xticks]

    ax2 = ax.twiny()  # Creates a twin axis sharing the same y-axis
    ax2.grid(False)
    ax2.set_xlim(ax.get_xlim()) 
    ax2.set_xticks(xticks, labels=xticks_minor)
    ax2.set_frame_on(False)
    ax2.set_xlabel("number of cores")
    
    plt.savefig( data_path + "/" + algo_name + "_" + data_name + "_load_balance_corrected" + format, bbox_inches='tight')


# scaling factor plots
if (op.exists(filename) and op.exists(dataprop_filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)

    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])
    res[SEARCH_SCALING_FACTOR] = res[SEARCH_SCALING_FACTOR].where(res[WEAK_MODE]!='input scaling', res[SEARCH_DESTINATION_FACTOR])

    res['data scaling method'] = res[SEARCH_SCALING_METHOD]
    
    work_res = res[res[WEAK_MODE]=='work scaling']
    # input_res = res[((res[WEAK_MODE]!='input scaling') | (res[SEARCH_SCALING_METHOD]=='extent'))]
    input_res = res[((res[WEAK_MODE]=='input scaling') & (res[SEARCH_SCALING_METHOD]=='extent'))]
    input_res.loc[(input_res[WEAK_MODE] == 'input scaling') & (input_res[SEARCH_SCALING_METHOD] == 'extent'), SEARCH_SCALING_METHOD] = 'input scaling'

    # filter all weak scaling point with larger error
    res['relative_error'] = res[SEARCH_ERROR] / res[SEARCH_DESTINATION_FACTOR]
    large_err = res[((res['relative_error'] >= 0.05) | (res['relative_error'] <= -0.05)) & (res[WEAK_MODE]!='input scaling')]

    # plot data
    fig, ax = plt.subplots(1,1)
    ax = sns.lineplot(data=work_res, x=SEARCH_DESTINATION_FACTOR, y=SEARCH_SCALING_FACTOR, hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, dashes=[linestyles[1]], ms=10, alpha=global_alpha)
    
    create_markers(ax.lines[:3])

    ax = sns.lineplot(data=input_res, x=SEARCH_DESTINATION_FACTOR, y=SEARCH_SCALING_FACTOR, style=WEAK_MODE, dashes=[linestyles[0]], ms=10, alpha=global_alpha, color='gray')

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_legend(ax)

    # add error markers
    tmp_num_lines = len(ax.lines)
    ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y=SEARCH_SCALING_FACTOR, hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, ms=10, linewidth=0.1, errorbar=None, legend=None, alpha=global_alpha)
    num_err_lines = len(ax.lines) - tmp_num_lines
    create_error_markers(num_err_lines, ax)

    # axis label
    ax.set(xlabel='number of ranks', ylabel='data size in multiples of base data size')

    # add x ticks at core counts
    xticks = list(set(df[SEARCH_DESTINATION_FACTOR]))
    xticks.sort()
    ax.set_xticks(xticks, labels=xticks)

    xticks_minor = [x*8 for x in xticks]

    ax2 = ax.twiny()  # Creates a twin axis sharing the same y-axis
    ax2.grid(False)
    ax2.set_xlim(ax.get_xlim()) 
    ax2.set_xticks(xticks, labels=xticks_minor)
    ax2.set_frame_on(False)
    #ax2.xaxis.set_ticks_position('bottom')  # Move ticks to the bottom
    #ax2.xaxis.set_label_position('bottom')  # Move label to the bottom
    #ax2.spines['bottom'].set_position(('outward', 20))  # Offset for clarity
    ax2.set_xlabel("number of cores")

    plt.savefig( data_path + "/" + algo_name + "_" + data_name + '_scalingfactor' + format, bbox_inches='tight')


# input scaling plots
if (op.exists(filename) and op.exists(dataprop_filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df['ranktimes'] = df['ranktimes'].apply(ast.literal_eval)
    df = df.explode('ranktimes')
    df['max_rank_time'] = df['ranktimes'].apply(max)

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)

    df = df[df[WEAK_MODE] == 'input scaling']
    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])

    # find min for each category and apply it there. 
    set_of_data_scaling_methods = set(df[SEARCH_SCALING_METHOD].to_list())
    result_list = []
    for scaling_method in set_of_data_scaling_methods: 
    
        current = res[res[SEARCH_SCALING_METHOD] == scaling_method].copy()

        find_mean = current[current[SEARCH_DESTINATION_FACTOR] == 1]
        mean_time = np.mean(list(find_mean[SEARCH_TIME_ORIGINAL]))

        current['number of cores'] = '8 cores, 1 rank'
        current['exec_time'] = current[SEARCH_TIME_SCALED] / mean_time

        for i in current.index:
            sf = float(current.loc[i, SEARCH_SCALING_FACTOR])
            if sf == 1.0:
                current.loc[i, 'exec_time'] = 1.0

        # copy in order to have the same field with different computation
        current_c = res.copy()
        current_c['number of cores'] = 'scaling factor\nmany ranks\neach with 8 cores'
        # current_c['exec_time'] = current[WEAK_TIME] / mean_time
        current_c['exec_time'] = current['max_rank_time'] / mean_time

        for i in current_c.index:
            sf = float(current_c.loc[i, SEARCH_SCALING_FACTOR])
            if sf == 1.0:
                current_c.loc[i, 'exec_time'] = 1.0

        result_list.append(current)
        result_list.append(current_c)

    # and then concatenate them 
    res = pd.concat(result_list, ignore_index=True)
    res['data scaling method'] = res[SEARCH_SCALING_METHOD]

    # plot data
    fig, ax = plt.subplots(1,1)
    ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y='exec_time', hue='data scaling method', hue_order=['resampling', 'replication', 'extent'], style='number of cores', dashes=linestyles_i, ms=10, alpha=global_alpha)
    ax.set(xlabel='scaling factor', ylabel='execution time in multiples of single core time')

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_markers(ax.lines[:6])

    create_legend(ax)

    # plot target line
    # --- retrieve the 'abstract' size
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    coord = min(28, min(y_max,x_max))
    # --- apply the proportional conversion
    Dx = (coord-2) / (x_max - x_min)
    Dy = (coord-2) / (y_max - y_min) * 0.8
    # --- convert gaps into an angle
    angle = (180/np.pi)*np.arctan( Dy / Dx)
    ax.plot([1, coord],[1, coord], color='black', linestyle='dashed', alpha=0.2, scalex=False, scaley=False)
    ax.text((max(coord-2,1+(coord-1)/2)), (max(coord-2,1+(coord-1)/2)), 'target', rotation=angle, horizontalalignment='center', verticalalignment='center', backgroundcolor='white')

    # add x ticks at core counts
    xticks = set(res[SEARCH_DESTINATION_FACTOR])
    ax.set_xticks(list(xticks), labels=xticks)

    plt.savefig( data_path + "/" + algo_name + "_" + data_name + '_input_scaling' + format, bbox_inches='tight')


# normalized by base case exec time plots
dataprop_filename = data_path + "/" + algo_name + "_data_" + data_name + ".csv"
if (op.exists(filename) and op.exists(dataprop_filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df['ranktimes'] = df['ranktimes'].apply(ast.literal_eval)
    df = df.explode('ranktimes')
    df['max_rank_time'] = df['ranktimes'].apply(max)
    df['mean_rank_time'] = df['ranktimes'].apply(np.mean)

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)
    
    # compute normalized by base case exec time
    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])
    # res['norm_time'] =  res[WEAK_TIME] / res[SEARCH_TIME_ORIGINAL]
    res['norm_time'] =  res['max_rank_time'] / res[SEARCH_TIME_ORIGINAL]
    
    search_scaling_methods = set(res[SEARCH_SCALING_METHOD])
    for ssm in search_scaling_methods:
        ssm_sf_view = res[(res[SEARCH_SCALING_FACTOR] == 1.0) & (res[SEARCH_SCALING_METHOD] == ssm)]
        # mean_single_rank_time = np.mean(list(ssm_sf_view[WEAK_TIME]))
        mean_single_rank_time = np.mean(list(ssm_sf_view['max_rank_time']))

        ssm_view = res[res[SEARCH_SCALING_METHOD] == ssm]
        for i in ssm_view.index:
            # res.loc[i, 'norm_time'] = res.loc[i, WEAK_TIME] / mean_single_rank_time
            res.loc[i, 'norm_time'] = res.loc[i, 'max_rank_time'] / mean_single_rank_time


    res['data scaling method'] = res[SEARCH_SCALING_METHOD]

    # filter all weak scaling point with larger error
    res['relative_error'] = res[SEARCH_ERROR] / res[SEARCH_DESTINATION_FACTOR]
    large_err = res[((res['relative_error'] >= 0.05) | (res['relative_error'] <= -0.05)) & (res[WEAK_MODE]!='input scaling')]

    # plot data
    fig, ax = plt.subplots(1,1)
    ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y='norm_time', hue='data scaling method', hue_order=['resampling', 'replication', 'extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], dashes=linestyles, ms=10, alpha=global_alpha)

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_markers(ax.lines[:6])

    create_legend(ax)
        
    # add error markers
    tmp_num_lines = len(ax.lines)
    ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y='norm_time', hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], ms=10, linewidth=0.1, errorbar=None, legend=None, alpha=global_alpha)
    num_err_lines = len(ax.lines) - tmp_num_lines
    create_error_markers(num_err_lines, ax)

    # axis label
    ax.set(xlabel='scaling factor', ylabel='execution time / base case execution time')

    # add x ticks at core counts
    xticks = set(res[SEARCH_DESTINATION_FACTOR])
    ax.set_xticks(list(xticks), labels=xticks)

    plt.savefig( data_path + "/" + algo_name + "_" + data_name + '_normalized' + format, bbox_inches='tight')


# normalized plots - load balance corrected
dataprop_filename = data_path + "/" + algo_name + "_data_" + data_name + ".csv"
if (op.exists(filename) and op.exists(dataprop_filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df['ranktimes'] = df['ranktimes'].apply(ast.literal_eval)
    df = df.explode('ranktimes')
    df['max_rank_time'] = df['ranktimes'].apply(max)
    df['mean_rank_time'] = df['ranktimes'].apply(np.mean)

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)
    
    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])

    res['norm_time'] =  res['mean_rank_time'] / res[SEARCH_TIME_ORIGINAL]
    
    search_scaling_methods = set(res[SEARCH_SCALING_METHOD])
    for ssm in search_scaling_methods:
        ssm_sf_view = res[(res[SEARCH_SCALING_FACTOR] == 1.0) & (res[SEARCH_SCALING_METHOD] == ssm)]
        # mean_single_rank_time = np.mean(list(ssm_sf_view[WEAK_TIME]))
        mean_single_rank_time = np.mean(list(ssm_sf_view['mean_rank_time']))

        ssm_view = res[res[SEARCH_SCALING_METHOD] == ssm]
        for i in ssm_view.index:
            res.loc[i, 'norm_time'] = res.loc[i, 'mean_rank_time'] / mean_single_rank_time

    res['data scaling method'] = res[SEARCH_SCALING_METHOD]

    # filter all weak scaling point with larger error
    res['relative_error'] = res[SEARCH_ERROR] / res[SEARCH_DESTINATION_FACTOR]
    large_err = res[((res['relative_error'] >= 0.05) | (res['relative_error'] <= -0.05)) & (res[WEAK_MODE]!='input scaling')]

    # plot data
    fig, ax = plt.subplots(1,1)
    ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y='norm_time', hue='data scaling method', hue_order=['resampling', 'replication', 'extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], dashes=linestyles, ms=10, alpha=global_alpha)

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_markers(ax.lines[:6])

    create_legend(ax)
        
    # add error markers
    tmp_num_lines = len(ax.lines)
    ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y='norm_time', hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], ms=10, linewidth=0.1, errorbar=None, legend=None, alpha=global_alpha)
    num_err_lines = len(ax.lines) - tmp_num_lines
    create_error_markers(num_err_lines, ax)

    # axis label
    ax.set(xlabel='scaling factor', ylabel='execution time / base case execution time')

    # add x ticks at core counts
    xticks = set(res[SEARCH_DESTINATION_FACTOR])
    ax.set_xticks(list(xticks), labels=xticks)

    plt.savefig( data_path + "/" + algo_name + "_" + data_name + '_normalized_load_balance_corrected' + format, bbox_inches='tight')


if not do_speedup_plots:
    exit()

# speedup plots
dataprop_filename = data_path + "/" + algo_name + "_data_" + data_name + ".csv"
if (op.exists(filename) and op.exists(dataprop_filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)
    
    # compute speedup
    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])
    # res['speedup'] = res[SEARCH_TIME_ORIGINAL] / res[WEAK_TIME]
    # res['speedup'] = res[SEARCH_TIME_SEARCHED] / res[WEAK_TIME]
    res.loc[res[WEAK_MODE] == 'work scaling', 'speedup'] = res[SEARCH_TIME_SEARCHED] / res[WEAK_TIME]
    res.loc[res[WEAK_MODE] == 'input scaling', 'speedup'] = res[SEARCH_TIME_SCALED] / res[WEAK_TIME]
    # input_scaling_view['speedup'] = input_scaling_view[SEARCH_TIME_SEARCHED] / input_scaling_view[WEAK_TIME]

    # search_scaling_methods = set(res[SEARCH_SCALING_METHOD])
    # for ssm in search_scaling_methods:
    #     ssm_sf_view = res[(res[SEARCH_SCALING_FACTOR] == 1.0) & (res[SEARCH_SCALING_METHOD] == ssm)]
    #     mean_single_rank_time = np.mean(list(ssm_sf_view[WEAK_TIME]))

    #     ssm_view = res[res[SEARCH_SCALING_METHOD] == ssm]
    #     for i in ssm_view.index:
    #         res.loc[i, 'speedup'] = mean_single_rank_time / res.loc[i, WEAK_TIME]


    res['data scaling method'] = res[SEARCH_SCALING_METHOD]

    # filter all weak scaling point with larger error
    res['relative_error'] = res[SEARCH_ERROR] / res[SEARCH_DESTINATION_FACTOR]
    large_err = res[((res['relative_error'] >= 0.05) | (res['relative_error'] <= -0.05)) & (res[WEAK_MODE]!='input scaling')]

    # plot data
    fig, ax = plt.subplots(1,1)
    ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y='speedup', hue='data scaling method', hue_order=['resampling', 'replication', 'extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], dashes=linestyles, ms=10, alpha=global_alpha) # dashes=[(1, 2), (4, 1.5)]

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_markers(ax.lines[:6])

    create_legend(ax)
        
    # add error markers
    tmp_num_lines = len(ax.lines)
    ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y='speedup', hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], ms=10, linewidth=0.1, errorbar=None, legend=None, alpha=global_alpha)
    num_err_lines = len(ax.lines) - tmp_num_lines
    create_error_markers(num_err_lines, ax)

    # axis label
    ax.set(xlabel='scaling factor', ylabel='scaled speedup')

    # add x ticks at core counts
    xticks = set(res[SEARCH_DESTINATION_FACTOR])
    ax.set_xticks(list(xticks), labels=xticks)

    plt.savefig( data_path + "/" + algo_name + "_" + data_name + '_speedup' + format, bbox_inches='tight')


# speedup plots - load balance corrected
dataprop_filename = data_path + "/" + algo_name + "_data_" + data_name + ".csv"
if (op.exists(filename) and op.exists(dataprop_filename)):
    df = pd.read_csv(filename, sep=";")
    df_data = pd.read_csv(dataprop_filename, sep=";")

    df[SEARCH_DESTINATION_FACTOR] = df[SEARCH_DESTINATION_FACTOR].astype(int)
    df_data[SEARCH_DESTINATION_FACTOR] = df_data[SEARCH_DESTINATION_FACTOR].astype(int)
    
    res = pd.merge(df, df_data, how='left', on=[SEARCH_DESTINATION_FACTOR, SEARCH_SCALING_METHOD])

    # extract load imbalance induced overhead
    res['load imbalance corrected time'] = res[WEAK_TIME]
    for i in range(len(res)):
        diffs = []
        rt_list = np.matrix(res.loc[i, 'ranktimes_x'].replace('],[','];[')).tolist()
        for a in rt_list:
            rt_max = np.max(a)
            rt_mean = np.mean(a)
            diff = rt_max - rt_mean
            diffs.append(diff)
        res.loc[i, 'load imbalance corrected time'] = res.loc[i, WEAK_TIME] - np.mean(diffs)

    # compute speedup
    # res['speedup'] = res[SEARCH_TIME_ORIGINAL] / res['load imbalance corrected time']
    # res['speedup'] = res[SEARCH_TIME_SEARCHED] / res[WEAK_TIME]
    res.loc[res[WEAK_MODE] == 'work scaling', 'speedup'] = res[SEARCH_TIME_SEARCHED] / res['load imbalance corrected time']
    res.loc[res[WEAK_MODE] == 'input scaling', 'speedup'] = res[SEARCH_TIME_SCALED] / res['load imbalance corrected time']

    # search_scaling_methods = set(res[SEARCH_SCALING_METHOD])
    # for ssm in search_scaling_methods:
    #     ssm_sf_view = res[(res[SEARCH_SCALING_FACTOR] == 1.0) & (res[SEARCH_SCALING_METHOD] == ssm)]
    #     mean_single_rank_time = np.mean(list(ssm_sf_view['load imbalance corrected time']))

    #     ssm_view = res[res[SEARCH_SCALING_METHOD] == ssm]
    #     for i in ssm_view.index:
    #         res.loc[i, 'speedup'] = mean_single_rank_time / res.loc[i, 'load imbalance corrected time']


    res['data scaling method'] = res[SEARCH_SCALING_METHOD]

    # filter all weak scaling point with larger error
    res['relative_error'] = res[SEARCH_ERROR] / res[SEARCH_DESTINATION_FACTOR]
    large_err = res[((res['relative_error'] >= 0.05) | (res['relative_error'] <= -0.05)) & (res[WEAK_MODE]!='input scaling')]

    # plot data
    fig, ax = plt.subplots(1,1)
    ax = sns.lineplot(data=res, x=SEARCH_DESTINATION_FACTOR, y='speedup', hue='data scaling method', hue_order=['resampling', 'replication', 'extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], dashes=linestyles, ms=10, alpha=global_alpha)

    for poly in ax.collections:
        poly.set_alpha(0.08)

    create_markers(ax.lines[:6])

    create_legend(ax)
        
    # add error markers
    tmp_num_lines = len(ax.lines)
    ax = sns.lineplot(data=large_err, x=SEARCH_DESTINATION_FACTOR, y='speedup', hue='data scaling method', hue_order=['resampling','replication','extent'], style=WEAK_MODE, style_order=['input scaling', 'work scaling'], ms=10, linewidth=0.1, errorbar=None, legend=None, alpha=global_alpha)
    num_err_lines = len(ax.lines) - tmp_num_lines
    create_error_markers(num_err_lines, ax)

    # axis label
    ax.set(xlabel='scaling factor', ylabel='scaled speedup')

    # add x ticks at core counts
    xticks = set(res[SEARCH_DESTINATION_FACTOR])
    ax.set_xticks(list(xticks), labels=xticks)

    plt.savefig( data_path + "/" + algo_name + "_" + data_name + '_speedup_load_balance_corrected' + format, bbox_inches='tight')
