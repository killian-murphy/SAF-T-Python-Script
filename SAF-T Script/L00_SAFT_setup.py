import pandas

def setup_options():
    # Set console parameters for development
    pandas.set_option('display.max_rows',    500)
    pandas.set_option('display.max_columns', 500)
    pandas.set_option('display.width',      1000)