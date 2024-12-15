# eeg_preprocessing_pipeline
This pipeline was created as part of a 7.5 ECTS research project during the MSc in Software Design program at the IT University of Copenhagen. It is an EEG data preprocessing tool designed to support newcomers in preprocessing of EEG data. The pipeline outputs a cleaned EEG file in .fif format along with a detailed report.

This pipeline uses MNE* and PyPrep** libraries to preprocess EEG data, based on datasets in the BIDS*** format. The pipeline includes preprocessing steps such as bad channel detection, interpolation, ICA, and more, with customization options available through a configuration file.

## Authors
Laura Kazlauskaite - kazlauskaite.lau@gmail.com // lkaz@itu.dk <br>
Amalie Kaa - amaliekkm@gmail.com // akmo@itu.dk

### Getting started
#### Download repository
Clone or download this repository.

#### Install necessary packages
Create project environment and install necessary packages using requirements.txt

#### Set up the configuration file (config.ini)
Make sure to set your dataset path in the config.ini file, and also check the file format for your EEG files (defaults to .edf) and placcement scheme (defaults to "standard_1020") matches the chosen formats in the configuration file. If your EEG files have another format than .edf you will have to implement the creation of the MNE raw objects in the cleanup_functions.py. Alto choose whether you would like the pipeline to interpolate bad channels and create cleaned .fif files. Other configurations can be set. 

Dataset path (mandatory)
File extension (optional, defaults to .edf)
EEG placement scheme (optional, defaults to standard_1020)
Reference channel (optional)
Line frequency (optional, defaults to 50)
Run ICA (optional, defaults to False)
Interpolate bad channels (mandatory)
Save EEG as fif (mandatory)

For more details on parameters see config.ini and project_report.pdf at the root directory of this repository.

#### Run the pipeline
To run the pipeline, execute the Main.py file either in the terminal or in an editor. 

#### Output
The pipeline created a colder at the root directory called "report". In this folder a folder for each participant is created along with subfolders for each session. In the session folder a report is generated showing relevant information and visualizations based on the given EEG data. A log file is also created to ease troubleshooting should you run into problems. If the option to save .fif file is enabled, a directory named "eeg" wil appear in each session folder with the cleaned EEG files. 

### Notes
The pipeline at this stage does not apply lowpass or highpass filters, as it aims to preserve original data for emotion detection.
Bad channel detection and interpolation are handled through the PyPrep library, which includes several algorithms for identifying problematic channels.

### References
\* MNE: https://mne.tools/stable/index.html <br>
** PyPrep: https://github.com/sappelhoff/pyprep <br>
*** BIDS: https://bids.neuroimaging.io/ <br>
