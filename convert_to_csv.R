#!/usr/bin/env Rscript

# 16 Feb 2021
# A script that reads a raw fid data (a single folder containing the fid file)
# and writes it out as csv. Presumably, a fourier transform is done as well.
# Usage:
# $ Rscript ~/Documents/bin/r_tools/nmr_utils_read_single.R <fn_in> <fn_out>

args <- commandArgs(trailingOnly = TRUE)

# ========== START ==========
library("pacman")
pacman::p_load("NMR.Utils")

fn_in <- args[1]
fn_out <- args[2]

nmr_spectrum <- read.nmr(fn_in)
write.csv(nmr_spectrum, fn_out, row.names=FALSE)
