# Neutron Tomography Showcase

A collection of jupyter notebooks showcasing reconstruction of neutron tomography datasets, using different acquisition protocols and different reconstruction techniques.

The datasets are reconstructed using the [Core Imaging Library (CIL)](https://github.com/TomographicImaging/CIL)

## Install an environment to run the demos locally

The easiest way to install an environment to run the demos is using our maintained environment file which contains the required packages. Running the command below will create a new environment which has specific and tested versions of all CIL dependencies and additional packages required to run the demos:

conda env create -f https://tomographicimaging.github.io/scripts/env/cil_demos.yml

Check the [main CIL repo](https://github.com/TomographicImaging/CIL) for full details on CIL and its dependencies and how to install into a custom environment.

## Case Studies
Information on the case studies and the datasets used  are as follows:

### Angles_vs_Exposure
This case study investigates the importance of number of projections (or angles), vs exposure time of the projections when total experiment time is limited.
The case study will showcase how the iterative methods available in Mantid Imaging can be used to improve the quality of reconstructed data.

The dataset used in this study is the Aluminium Cylinder Flexible Neutron Tomography Dataset.
This is available on zenodo at: https://zenodo.org/records/17250237
Specifically, these notebooks work with the pre-processed data, for which the direct download link is: https://zenodo.org/records/17250237/files/preprocessed_data.zip?download=1

For more information on loading the Aluminium Cylinder dataset see: [data_io/README.md](data_io/README.md)
