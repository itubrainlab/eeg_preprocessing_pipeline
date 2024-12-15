### IMPORTANT ###
# Running this file will overwrite your current config.ini deleting all comments.
# This file is only to be run if you implement changes in the pipeline.

import configparser

def create_config():
    config = configparser.ConfigParser()

    config['General'] = {'dataset_path': '', 
                         'file_extension': '',
                         'eeg_placement_scheme': '',
                         'reference_channel' : '',
                         'line_frequency_Hz': 50,
                         'run_ica': True,
                         'interpolate_bad_channels': False,
                         'save_eeg_as_fif': False
                         }
    
    
    config['Select_algorithms_run'] = {
                        'bads_by_nan_flat': True,
                        'bads_by_hfnoise': True,
                        'bads_by_deviation': True,
                        'bads_by_correlation': True,
                        'bads_by_SNR': True,
                        'bads_by_ransac': True
                        }
    
    config['Bads_by_hfnoise'] = {
                         'HF_zscore_threshold': ''
                        }
    
    config['Bads_by_deviation'] = {
                         'deviation_threshold': ''
                        }
    
    
    config['Bads_by_correlation'] = {
                         'correlation_secs': '',
                         'correlation_threshold': '',
                         'frac_bad_corr': ''
                        }
    
    config['Bads_by_ransac'] = {
                         'n_samples': '',
                         'sample_prop': '',
                         'corr_thresh': '',
                         'frac_bad_ransac': '',
                         'corr_window_secs': '',
                         'channel_wise': False
                        }
    


    # Write the configuration to a file
    with open('config.ini', 'w') as configfile:
        config.write(configfile)


create_config()