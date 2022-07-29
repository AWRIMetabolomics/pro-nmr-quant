# High Throughput Quantitation of Proline NMR Signals

### How This Repo Works

There are three steps to the workflow:
1. Convert NMR data to `csv` with `nmr_utils_read_single.R`. 
2. `workbook-fit.ipynb` - Fit a straight line of best fit.
3. `workbook-predict.ipynb`- Predict new test sample(s). 

Other files:
* `my_utils.py` - a text file of utility functions used by `workbook-fit.ipynb` and `workbook-predict.ipynb`
* 

* Get the data from TODO

* If the data is in Bruker's FID format, you'll need to convert it to `csv` using `nmr_utils_read_single.R`. 

### Installating Dependencies

Steps 2 and 3 were written with the most stable and popular python packages, and should thus be fairly future proof (save syntax-breaking changes); there should be not much issue using whatever the current latest stable release of the packages listed in `requirements.txt`. Otherwise, to do version-specific installation, do:

```
# optional step: create a virtual env to operate in
python3 -m venv venv
source venv/bin/activate

# install requirements
python3 -m pip3 install requirements.txt
```

### Citation

If you use this code, please cite:

```
TODO
```

### Licensing

<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" 
src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" 
href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.

