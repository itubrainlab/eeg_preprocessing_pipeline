from contextlib import redirect_stdout
import matplotlib.pyplot as plt

#importing local python files
import report_generator as rg
import read_directories as rd
import cleanup_functions as cf

import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

file_extension = ".edf"
eeg_placement_scheme = 'standard_1020'
generate_report = True
reference_channel = ""
reference_channel_set_automatically = True
dataset_path = ""
participant_list = []
function_list = []
line_frequency = 50
printed = False
interpolate_bads = False
save_eeg_as_fif = False

def set_eeg_file_extension(eeg_form):
    rd.set_eeg_file_extension(eeg_form)
    global file_extension
    file_extension = eeg_form

def set_eeg_placement_scheme(eeg_pl_scheme):
    global eeg_placement_scheme
    eeg_placement_scheme = eeg_pl_scheme

def set_generate_report(gen_report):
    global generate_report
    generate_report = gen_report   

def set_reference_channel(ref_channel):
    global reference_channel
    reference_channel = ref_channel

def set_dataset_path(data_path):
    global dataset_path
    dataset_path = data_path

def create_participant_list():
    global dataset_path
    global participant_list
    participant_list = rd.get_participant_list(dataset_path)

def set_line_frequency(freq):
    global line_frequency
    line_frequency = freq

def set_reference_channel_boolean(bool):
    global reference_channel_set_automatically
    reference_channel_set_automatically = bool
    
def set_interpolate_bads(interpolate_bads_):
    global interpolate_bads
    interpolate_bads = interpolate_bads_

def set_save_raw_as_fif(save_raw_as_fif_):
    global save_eeg_as_fif
    save_eeg_as_fif = save_raw_as_fif_


### Function for running the pipeline from main
def run_pipeline(dataset_path, file_extension, eeg_placement_scheme, reference_channel, line_freq, interpolate_bads, save_raw_as_fif):
    set_parameters(dataset_path, file_extension, eeg_placement_scheme, reference_channel, line_freq, interpolate_bads, save_raw_as_fif)
    pipeline_for_participants()
    

def set_parameters(dataset_path, file_extension, eeg_placement_scheme, reference_channel, line_freq, interpolate_bads, save_raw_as_fif):
    if len(file_extension) > 0:
        set_eeg_file_extension(file_extension)
    if len(eeg_placement_scheme) > 0:
        set_eeg_placement_scheme(eeg_placement_scheme)
    if len(reference_channel) > 0:
        set_reference_channel_boolean(False)
    set_reference_channel(reference_channel)
    set_dataset_path(dataset_path)
    create_participant_list()
    add_functions_to_list()
    if len(line_freq) > 0:
        set_line_frequency(int(line_freq))
    set_interpolate_bads(interpolate_bads)
    set_save_raw_as_fif(save_raw_as_fif)
    cf.set_parameters_for_bad_channel_detection()

            
def pipeline_for_participants():
    global participant_list
    while (len(participant_list) > 0):
        participant = participant_list.pop(0)
        try:
            print(f"Processing participant: {participant.get_sub_id()}")
            print(f"Remaining participants: {len(participant_list)}")
            for session in participant.get_sessions():
                # if the participant has eeg files there will be a run list, otherwise empty
                if session.get_run_list():
                    # Clears the reports
                    rg.clear_md_file(session.get_report_path())
                    # Starts the report with headline
                    rg.start_report(session.get_run_list()[0])
                plt.close('all')
                for_each_session(session, function_list)
        except Exception as e:
            print(f"Error processing participant {participant.get_sub_id}: {e}")
     


def step1_create_and_print_raw(run):
    cf.create_raw(run)
    global printed
    if not printed:
        headline = "Visualization of sensor placement on head"
        text = "The following shows the standard sensor placement for the selected placement scheme. \
            The plot is not an accurate represenation of the actual sensor placements on the individual participant, \
            but rather a reference for visualization purposes."
        rg.print_h2(headline, run)
        rg.print_normal(text, run)
        cf.plot_sensors(run)
        headline = "Raw info for all runs"
        text = "The following shows the number of channels, \
            list of channel names, highpass and lowpass filters and sampling frequency. \
            All parameters are extracted from the unaltered EEG file."
        rg.print_h2(headline, run)
        rg.print_normal(text, run)
        printed = True
    
    cf.print_raw_info(run)


def step2_make_raw_ch_plots(run):
    global printed
    if not printed:
        headline = "Preview of raw channel plot"
        text = "The following shows the first 5 seconds of the raw channel plots \
            for each run in the session."
        rg.print_h2(headline, run)
        rg.print_normal(text, run)
        printed = True
    cf.raw_channel_plot(run)


def step3_psd_plots(run):
    global printed
    if not printed:
        headline = "PSD plots"
        text = "The following shows the PSD (power spectral density) plots \
                for each run in the session before and after applying notch filter \
                - filtering line frequency noise based on selected frequency."
        rg.print_h2(headline, run)
        rg.print_normal(text, run)
        rg.print_normal(f"Selected frequency: {line_frequency} Hz", run)
        printed = True
    cf.plot_psd(run)
    cf.apply_notch_filter_and_plot_psd(run)


def step4_find_bad_channels(run):
    global printed
    if not printed:
        headline = "Bad channel detection"
        text = "The following is an overview of all bad channels found by \
                each selected bad channel detection method for each run in the session. \
                Note that if any bad channels are found by \"bads-by-nan-flat\", these channels will \
                appear in the list of all other algorithms as well. \
                Additionally, \"bads-by-ransac\" will always also include the bad channels found by \
                \"bads-by-deviation\" and \"bads-by-correlation\" "
        rg.print_h2(headline, run)
        rg.print_normal(text, run)
        printed = True
    rg.print_h4("Bad channels found for " + str(run.get_run_id()), run)
    cf.find_bad_by_nan_flat(run)
    cf.find_bad_by_hfnoise(run)
    cf.find_bad_by_deviation(run)
    cf.find_bad_by_correlation(run)
    cf.find_bad_by_SNR(run)
    cf.find_bad_by_ransac(run)
    cf.set_bad_channels(run)


def step5_interpolate_bads(run):
    global interpolate_bads
    global printed
    # TODO: implement this fully
    if(interpolate_bads):
        if not printed:
            rg.print_h2("Bad channel interpolation", run)
            printed = True
        cf.interpolate_bads(run)
        

def step6_ica(run):
    if(cf.run_ica):
        global printed
        if not printed:
            headline = "ICA components plot"
            text = "The following plots show the independent components found by applying ICA (Independent Component Analysis) \
                    for each run in the session. The components are plotted in two different ways. The first plot shows a\
                    time series plot of the components. The plot depicts the first 20 seconds and shows up to 19 different components. \
                    The second plot is a spatial image of the components, representing where on the scalp \
                    the signal is active."
            rg.print_h2(headline, run)
            rg.print_normal(text, run)
            printed = True
        cf.ica(run)


def step7_save_eeg_as_fif(run):
    global save_eeg_as_fif
    global printed
    if(save_eeg_as_fif):
        if not printed:
            rg.print_h2("Saving cleaned EEG files", run)
            printed = True
        cf.save_raw_as_fif(run)
    

def for_each_session(session, list_of_func):
    global printed
    list_of_runs = session.get_run_list()
    
    #creating log file for each session and redirecting stdout
    log_filepath = session.get_log_filepath()
    session_id = session.get_session_id()
    participant_id = session.get_participant().get_sub_id()
    # Clears the log file
    rg.clear_md_file(log_filepath)
    with open(log_filepath, 'w') as log_file, redirect_stdout(log_file):
        try:
            print(f"Starting processing for session {session_id} of participant {participant_id}")
            
            for func in list_of_func:
                printed = False
                for run in list_of_runs:
                    func(run)
            
            print(f"Finished processing for session {session_id}")
        except Exception as e:
            print(f"Error processing session {session_id} of participant {participant_id}: {e}")


# make sure all functions we want to call are added to this list
def add_functions_to_list():
    global function_list
    function_list.append(step1_create_and_print_raw)
    function_list.append(step2_make_raw_ch_plots)
    function_list.append(step3_psd_plots)
    function_list.append(step4_find_bad_channels)
    function_list.append(step5_interpolate_bads)
    function_list.append(step6_ica)
    function_list.append(step7_save_eeg_as_fif)

