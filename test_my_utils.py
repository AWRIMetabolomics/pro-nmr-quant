from nmr_targeted_utils import *
import numpy as np
import pandas as pd

from scipy.signal import fftconvolve
from scipy.stats import pearsonr

from io import StringIO
import os
import time
import sys
import pytest
import math

# Use $pytest -rP to display stdout

def test_multiplet_match_trimming():
    my_array = [1, 2, 3, 8, 9, 10, 20, 21, 22]
    result0 = multiplet_match_trimming(my_array, 5)
    result1 = multiplet_match_trimming(my_array, 10)
    result2 = multiplet_match_trimming(my_array, 11)
    assert result0 == [1, 8, 20]
    assert result1 == [1, 20]
    assert result2 == [1]


def test_do_1d_std_search():
    sys.stdout.write("WARNING in test_do_1d_std_search(): Lorentzians not being tested!")
    
    # generate synthetic data
    query0 = [1, 1, 1, 1, 1, 1, 2, 1, 7, 10, 6, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 3, 5, 4, 2, 1, 1, 1]
    target = [1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 7, 10, 6, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 3, 5, 4, 2, 1, 1, 1]
    c0 = np.array([np.array(query0), np.arange(len(query0))/10])
    c2 = np.array([np.array(target), np.arange(len(target))/10])

    multiplets_ls = [[0.1, 0.9], [0.7, 1.1]]
    query0_df = pd.DataFrame(data=np.transpose(c0), columns=["intensity", "ppm"])
    target_df_perfectmatch = pd.DataFrame(data=np.transpose(c2), columns=["intensity", "ppm"])
    query0_df = query0_df.sort_values(by="ppm", ascending=False).reset_index(drop=True)
    target_df_perfectmatch = target_df_perfectmatch.sort_values(by="ppm", ascending=False).reset_index(drop=True)

    # do 1d search
    results_dict0 = do_1d_std_search(query_df=query0_df, 
                                target_df=target_df_perfectmatch, 
                                multiplets_ls=multiplets_ls, 
                                query_l_dict={}, 
                                search_region_padding_size=0.3, 
                                floor_window=False
                               )
    # load real data
    pro_df = pd.read_csv("/Users/dteng/Documents/bin/nmr_constants/cal_data_pro/pro_stds/pro_std_10_r1.csv")
    # generate synthetic target data
    q_df = pro_df.loc[(pro_df["ppm"]>2.29) & (pro_df["ppm"]<2.43)].copy().reset_index(drop=True)
    noisy_intensity_arr = np.random.normal(min(q_df.intensity.values), 1E8, size=1500)
    noisy_intensity_arr[500:500+len(q_df)] += q_df.intensity.values # insert proline signal at index 100. This will be inserted from behind. 
    ppm_arr = pro_df.loc[pro_df["ppm"]>2.29].tail(1500).ppm.values
    target_df = pd.DataFrame(data=np.transpose([ppm_arr, noisy_intensity_arr]), columns=["ppm", "intensity"])

    # do 1d search
    results_dict1 = do_1d_std_search(query_df=pro_df, 
                                     target_df=target_df, 
                                     multiplets_ls=[[2.29, 2.43]], 
                                     query_l_dict={}, 
                                     search_region_padding_size=0.2, 
                                     floor_window=False
                                    )
    max_rho = max(results_dict1["multiplet_0"]["rho_ls"])

    assert results_dict0["multiplet_0"]["rho_ls"] == pytest.approx(np.array([ 0.76883751, 1., -0.30550505,0.61101009, -0.19720266]), 0.01)
    assert results_dict0["multiplet_0"]["coords"] == pytest.approx([0.1, 0.9], 0.01)
    assert results_dict0["multiplet_0"]["multiplet_len_idx"] == 7
    assert results_dict0["multiplet_0"]["multiplet_len_ppm"] == pytest.approx(0.8, 0.01)
    assert results_dict0["multiplet_0"]["multiplet_match_idx"] == [1]
    assert results_dict0["multiplet_0"]["multiplet_match_ppm"][0] == pytest.approx([1.0, 0.2], 0.01)

    assert results_dict0["multiplet_1"]["rho_ls"] == pytest.approx(np.array([-0.2773501, 0.30184385, 1., -0.05241424, -0.79701677,0.97072534, -0.69337525,  0.]), 0.01)
    assert results_dict0["multiplet_1"]["coords"] == pytest.approx([0.7, 1.1], 0.01)
    assert results_dict0["multiplet_1"]["multiplet_len_idx"] == 3
    assert results_dict0["multiplet_1"]["multiplet_len_ppm"] == pytest.approx(0.4, 0.01)
    assert results_dict0["multiplet_1"]["multiplet_match_idx"] == [2]
    assert results_dict0["multiplet_1"]["multiplet_match_ppm"][0] == pytest.approx([1.2, 0.8], 0.01)

    assert max_rho == pytest.approx(0.998813174428683, 0.001)
    assert results_dict1["multiplet_0"]["multiplet_match_ppm"][0] == pytest.approx([2.44616904290229, 2.30616904290229], 0.001)


def test_norm_xcorr():
    # test on a sine wave first
    x = np.sin(np.arange(0, 10, 0.1))
    y = np.sin(np.arange(math.pi, 10+math.pi, 0.1))

    assert norm_xcorr(x, x) == pytest.approx(1.0, 1E-6)
    assert norm_xcorr(x, y) == pytest.approx(-1.0, 1E-6)


def test_adjust_to_ref_peak():
    # generate synthetic data
    x = np.transpose([np.linspace(start=-1, stop=3, num=40, endpoint=False), np.array([1.0]*40)])
    x[10,1] = 4
    x[11,1] = 8
    x[12,1] = 4
    df = pd.DataFrame(data=x, columns=["ppm", "intensity"])

    df_expected = df.copy()
    temp_arr = df_expected.ppm.values - 0.1
    df_expected["ppm"] = temp_arr

    ref_pk_search_window = [-0.3, 0.3]
    ref_pk_tol_window = [0, 0]
    df2 = adjust_to_ref_peak(df, ref_pk_search_window, ref_pk_tol_window)


    pd.testing.assert_frame_equal(df2, df_expected, check_exact=False)


def test_get_scaling_factor():
    # generate synthetic data
    sf = 1.5
    x = np.transpose([np.arange(100)/10, np.sin(np.arange(0, 10, 0.1))])
    df = pd.DataFrame(data=x, columns=["ppm", "intensity"])
    df_sample = df.copy()
    temp_arr = df.intensity.values * sf
    df_sample["intensity"] = temp_arr

    sf_calc = get_scaling_factor(df, df_sample, 0.0, 9.9)

    assert sf_calc == pytest.approx(sf, 1E-6)

