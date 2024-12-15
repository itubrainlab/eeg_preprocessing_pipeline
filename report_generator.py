import markdown
import os


def __print_text(font_style, string, output_file_path, start_with_linebreak):
    """ This function should not be used directly, but is the print function 
        behind the other print functions that have the formatting. 
    """
    with open((output_file_path), 'a') as f:
        if start_with_linebreak:
             print("<br>", file=f)
        print((font_style + string + " <br>"), file=f)
        
        
def print_h1(string, run):
    """ Print "string" to file "file path" as Header 1"""
    file_path = run.get_report_path()
    __print_text('# ', string, file_path, False)
    
def print_h2(string, run):
    """ Print "string" to file "file path" as Header 2"""
    file_path = run.get_report_path()
    __print_text('## ', string, file_path, False)
    
def print_h3(string, run):
    """ Print "string" to file "file path" as Header 3"""
    file_path = run.get_report_path()
    __print_text('### ', string, file_path, False)
    
def print_h4(string, run):
    """ Print "string" to file "file path" as Header 4"""
    file_path = run.get_report_path()
    __print_text('#### ', string, file_path, False)
    
def print_h5(string, run):
    """ Print "string" to file "file path" as Header 5"""
    file_path = run.get_report_path()
    __print_text('##### ', string, file_path, False)
    
def print_normal(string, run):
    """ Print "string" to file "file path" as normal text"""
    file_path = run.get_report_path()
    __print_text('', string, file_path, False)
    
def add_plot(run, plot, filename, add_run_number):
    """ Adds a plot to the report and saves the plot image in session directory."""
    new_filename =  run.get_run_id() + "_" + filename + str(".png")
    image_path = os.path.join(run.get_report_dir(), new_filename)
    plot.savefig(image_path)
    report_path = run.get_report_path()
    
    if add_run_number:
        print_h4((str(filename) + " of " + run.get_run_id()), run)
    else:
        print_h4(str(filename), run)
    __print_text('', ('![' + new_filename + '](' + new_filename + ')'), report_path, False)
    
def md_to_html(file_path):
    """ Creates HTML file from markdown file. Not fully implemented  yet."""
    #read the whole file to a variable
    #create a new path for the html file
    #append for every line or convert the whole thing at once?

    html_string = markdown.markdown("# Helloooo")
    print(html_string)
    # with open(html_path, 'a') as f:
    #     print(html_string, file = f)
    
# md_to_html("path")

def clear_md_file(filepath):
    # Open the file in write mode to clear its contents
    with open(filepath, 'w') as file:
        pass  # Do nothing, just open and close to truncate the file


def start_report(run):
    if len(run.get_session().get_participant().get_sessions()) > 1:
        headline = f"Report for participant {run.get_session().get_sub_id()}, session {run.get_session().get_session_id()}"
    else:    
        headline = f"Report for participant {run.get_session().get_sub_id()}"
    print_h1(headline, run)
    for current_run in run.get_session().get_run_list():
        print_normal(f"{current_run.get_run_id()} has file path: {current_run.get_filepath()}", current_run)
        
    