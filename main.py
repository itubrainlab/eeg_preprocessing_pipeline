# importing pipeline files
import pipeline_manager as pln
import configReader as cr


pln.run_pipeline(cr.dataset_path, cr.file_extension, cr.eeg_placement_scheme, cr.reference_channel, cr.line_frequency_Hz, cr.interpolate_bad_channels, cr.save_eeg_as_fif)
