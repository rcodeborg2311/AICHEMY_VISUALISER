import alchemy


def single_experiment(parameters):
    """ Run a single alchemy experiment with a given set of parameters"""

    # Validate Parameters
    ## Parameters should include the following:
    ## - Input Expressions (this should be a list of valid lambda expressions (strings?))
    ## - Number of collisons to perform
    ## - Polling Frequency (how often we report the full state of the Soup)
    ## - Measurements (what values to calculate in addition to the full state, entropy, unique exprs etc)

    # Generate an empty Soup

    # Add the initial expressions

    # Collect the polling data while running

    # Format the polling data

    # Return format should be like {params: params, collision_number_1: {measure1: X, measure2: Y... state: [all lambda expressions] }}
    # return 

def parse_experiment_config(config_filename):
    """ This will generate experiment parameters from file, or other specification"""

    # Considerations:
    # We want to be able to specify the intial lambda expressions as either being generated from a function (BTree or Fontana Gen),
    # OR as a file to read from (will need additional function to validate/handle that file)

    
    # Need to specify functions to calculate at each polling frequency (entropy, unique expressions etc). 
    # Should throw and error if a function thats not implemented is requested

    # Then we need to make sure we've also handled the "easy" parameter (total collisions, polling frequency)


    # The output of this should be parameters that can be passed to `single_experiment`

def run_experiments(filename):
    params = parse_experiment_config(filename)
    data = single_experiment(params)

if __name__ == "__main__":
    
    print("hello")