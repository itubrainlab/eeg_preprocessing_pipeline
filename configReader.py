import configparser


#def read_config():
# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read('config.ini')

# Access values from the configuration file
dataset_path = config.get('General', 'dataset_path')
file_extension = config.get('General', 'file_extension')
eeg_placement_scheme = config.get('General', 'eeg_placement_scheme')
reference_channel = config.get('General', 'reference_channel')
line_frequency_Hz = config.get('General', 'line_frequency_Hz')
run_ica = config.get('General', 'run_ica')
interpolate_bad_channels = config.getboolean('General', 'interpolate_bad_channels')
save_eeg_as_fif = config.getboolean('General', 'save_eeg_as_fif')



# Access values for which algorithms to include in the run's bads
# Be aware that nan_flat always runs when any other algorithm is run
# Ransac excludes bads channels found by correlation and deviation. If you want to see
# the excluded channels, you should run correlation and deviation
bads_by_nan_flat = config.get('Select_algorithms_run', 'bads_by_nan_flat')
bads_by_hfnoise = config.get('Select_algorithms_run', 'bads_by_hfnoise')
bads_by_deviation = config.get('Select_algorithms_run', 'bads_by_deviation')
bads_by_correlation = config.get('Select_algorithms_run', 'bads_by_correlation')
bads_by_SNR = config.get('Select_algorithms_run', 'bads_by_SNR')
bads_by_ransac = config.get('Select_algorithms_run', 'bads_by_ransac')



# Access values for bad channel detection
hf_zscore_threshold = config.get('Bads_by_hfnoise', 'hf_zscore_threshold')

deviation_threshold = config.get('Bads_by_deviation', 'deviation_threshold')

correlation_secs = config.get('Bads_by_correlation', 'correlation_secs')
correlation_threshold = config.get('Bads_by_correlation', 'correlation_threshold')
frac_bad_corr = config.get('Bads_by_correlation', 'frac_bad_corr')

n_samples = config.get('Bads_by_ransac', 'n_samples')
sample_prop = config.get('Bads_by_ransac', 'sample_prop')
corr_thresh = config.get('Bads_by_ransac', 'corr_thresh')
frac_bad_ransac = config.get('Bads_by_ransac', 'frac_bad_ransac')
corr_window_secs = config.get('Bads_by_ransac', 'corr_window_secs')
channel_wise = config.get('Bads_by_ransac', 'channel_wise')



    # Return a dictionary with the retrieved values
    # config_values = {
    #     'debug_mode': debug_mode,
    #     'log_level': log_level,
    #     'db_name': db_name,
    #     'db_host': db_host,
    #     'db_port': db_port
    # }

    # return config_values


#if __name__ == &quot;__main__&quot;:
    # Call the function to read the configuration file
# config_data = read_config()

    # Print the retrieved values
print("Dataset path: " + dataset_path)
print("File extension: " + file_extension)
print("Eeg placement scheme: " + eeg_placement_scheme)
print("reference_channel: " + reference_channel)
