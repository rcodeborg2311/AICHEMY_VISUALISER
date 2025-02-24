# import alchemy


# def single_experiment(parameters):
#     """ Run a single alchemy experiment with a given set of parameters"""

#     # Validate Parameters
#     ## Parameters should include the following:
#     ## - Input Expressions (this should be a list of valid lambda expressions (strings?))
#     ## - Number of collisons to perform
#     ## - Polling Frequency (how often we report the full state of the Soup)
#     ## - Measurements (what values to calculate in addition to the full state, entropy, unique exprs etc)

#     # Generate an empty Soup

#     # Add the initial expressions

#     # Collect the polling data while running

#     # Format the polling data

#     # Return format should be like {params: params, collision_number_1: {measure1: X, measure2: Y... state: [all lambda expressions] }}
#     # return 

# def parse_experiment_config(config_filename):
#     """ This will generate experiment parameters from file, or other specification"""

#     # Considerations:
#     # We want to be able to specify the intial lambda expressions as either being generated from a function (BTree or Fontana Gen),
#     # OR as a file to read from (will need additional function to validate/handle that file)

    
#     # Need to specify functions to calculate at each polling frequency (entropy, unique expressions etc). 
#     # Should throw and error if a function thats not implemented is requested

#     # Then we need to make sure we've also handled the "easy" parameter (total collisions, polling frequency)


#     # The output of this should be parameters that can be passed to `single_experiment`

# def run_experiments(filename):
#     params = parse_experiment_config(filename)
#     data = single_experiment(params)

# if __name__ == "__main__":
    
#     print("hello")
import json
import os
import sys

# If needed, adjust the path to where `alchemy` is installed:
# sys.path.append('/path/to/alchemy/install')
import alchemy

def gather_user_parameters():
    """
    Prompt the user for all experiment parameters (no JSON file).
    Returns a dictionary matching the structure you provided,
    e.g.:
    {
        "total_collisons": 1000,
        "polling_frequency": 10,
        "input_expressions": {
            "generator": "from_file",
            "params": {...}
        },
        "measurements": ["entropy", "unique_expressions"]
    }
    """
    # total_collisons (spelling matches your JSON example)
    total_collisons_str = input("Enter the total number of collisons (default 1000): ").strip() or "1000"
    
    # polling_frequency
    polling_frequency_str = input("Enter the polling frequency (default 10): ").strip() or "10"
    
    # Generator
    print("\nChoose your generator type:")
    print("1) from_file (default)")
    print("2) BTree")
    print("3) Fontana")
    gen_choice = input("Enter choice (1-3): ").strip() or "1"
    
    generator_map = {
        "1": "from_file",
        "2": "BTree",
        "3": "Fontana"
    }
    generator_type = generator_map.get(gen_choice, "from_file")
    
    # Generator parameters
    gen_params = {}
    if generator_type == "from_file":
        filename = input("Enter the filename for your expressions (default: test_exprs.txt): ").strip() or "test_exprs.txt"
        gen_params["filename"] = filename
    elif generator_type == "BTree":
        print(f"\nGenerator '{generator_type}' chosen. Let's gather BTree parameters.")
        size_str = input("Enter size (default 5): ").strip() or "5"
        fvp_str = input("Enter freevar_generation_probability (default 0.5): ").strip() or "0.5"
        max_fv_str = input("Enter max_free_vars (default 3): ").strip() or "3"
        std_type = input("Enter standardization type (prefix/postfix/none), default 'prefix': ").strip() or "prefix"
        gen_params["size"] = int(size_str)
        gen_params["freevar_generation_probability"] = float(fvp_str)
        gen_params["max_free_vars"] = int(max_fv_str)
        gen_params["standardization"] = std_type
    elif generator_type == "Fontana":
        print(f"\nGenerator '{generator_type}' chosen. Let's gather Fontana parameters.")
        abs_low_str = input("Enter abstraction_prob_range low (default 0.1): ").strip() or "0.1"
        abs_high_str = input("Enter abstraction_prob_range high (default 0.5): ").strip() or "0.5"
        app_low_str = input("Enter application_prob_range low (default 0.2): ").strip() or "0.2"
        app_high_str = input("Enter application_prob_range high (default 0.6): ").strip() or "0.6"
        max_depth_str = input("Enter max_depth (default 5): ").strip() or "5"
        max_fv_str = input("Enter max_free_vars (default 2): ").strip() or "2"
        gen_params["abs_range"] = [float(abs_low_str), float(abs_high_str)]
        gen_params["app_range"] = [float(app_low_str), float(app_high_str)]
        gen_params["max_depth"] = int(max_depth_str)
        gen_params["max_free_vars"] = int(max_fv_str)
    
    # Measurements
    measurements_str = input(
        "Enter measurements (comma-separated, e.g. 'entropy,unique_expressions'), or leave blank: "
    ).strip()
    if measurements_str:
        measurements = [m.strip() for m in measurements_str.split(",")]
    else:
        measurements = []
    
    # Convert numeric inputs
    try:
        total_collisons = int(total_collisons_str)
        polling_frequency = int(polling_frequency_str)
    except ValueError:
        raise ValueError("Invalid input: 'total_collisons' and 'polling_frequency' must be integers.")
    
    # Build the config dictionary
    config = {
        "total_collisons": total_collisons,  # keep the original spelling
        "polling_frequency": polling_frequency,
        "input_expressions": {
            "generator": generator_type,
            "params": gen_params
        },
        "measurements": measurements
    }
    
    return config

def load_btree_expressions(params: dict) -> list:
    """
    If generator == 'BTree', create PyBTreeGen from 'params' and generate some expressions.
    Returns the list of generated expressions.
    """
    size = params.get("size", 5)
    fvp = params.get("freevar_generation_probability", 0.5)
    max_fv = params.get("max_free_vars", 3)
    std = params.get("standardization", "prefix")
    
    btree_gen = alchemy.PyBTreeGen.from_config(size, fvp, max_fv, alchemy.PyStandardization(std))
    # Let's generate, say, 10 expressions for demonstration
    expressions = btree_gen.generate_n(10)
    return expressions

def load_fontana_expressions(params: dict) -> list:
    """
    If generator == 'Fontana', create PyFontanaGen from 'params' and generate some expressions.
    Returns the list of generated expressions.
    """
    abs_range = tuple(params.get("abs_range", [0.1, 0.5]))
    app_range = tuple(params.get("app_range", [0.2, 0.6]))
    max_depth = params.get("max_depth", 5)
    max_free_vars = params.get("max_free_vars", 2)
    
    fontana_gen = alchemy.PyFontanaGen.from_config(abs_range, app_range, max_depth, max_free_vars)
    # Let's generate, say, 10 expressions
    expressions = []
    for _ in range(10):
        expr = fontana_gen.generate()
        if expr:
            expressions.append(expr)
    return expressions

def load_input_expressions(generator_type: str, gen_params: dict) -> list:
    """
    Load or generate expressions depending on the generator type.
    """
    if generator_type == "from_file":
        filename = gen_params.get("filename", "test_exprs.txt")
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Could not find file: {filename}")
        with open(filename, "r") as f:
            return [line.strip() for line in f if line.strip()]

    elif generator_type == "BTree":
        return load_btree_expressions(gen_params)
    
    elif generator_type == "Fontana":
        return load_fontana_expressions(gen_params)
    
    return []

def single_experiment(config: dict) -> dict:
    """
    Runs the experiment using the provided config.
    Returns a dictionary of results:
    {
      "config": <the input config>,
      "generated_expressions": [...],
      "collisions_data": {
          "collision_10": { "entropy": X, "unique_expressions": [...], "state": [...] },
          ...
      }
    }
    """
    generator_type = config["input_expressions"]["generator"]
    gen_params = config["input_expressions"].get("params", {})
    
    # Create a new Soup
    soup = alchemy.PySoup()

    # Generate or load the initial expressions
    expressions = load_input_expressions(generator_type, gen_params)
    
    # Print any newly generated expressions if BTree or Fontana
    if generator_type in ["BTree", "Fontana"]:
        print(f"\nGenerated {len(expressions)} expressions from {generator_type}:\n")
        for expr in expressions:
            print("  ", expr)
    
    # Perturb the soup with these expressions
    soup.perturb(expressions)
    
    # Now run the collisions and measure
    total_collisons = config["total_collisons"]
    polling_frequency = config["polling_frequency"]
    measurements = config["measurements"]
    
    results_data = {}
    collision_count = 0
    while collision_count < total_collisons:
        soup.simulate_for(1, log=False)
        collision_count += 1

        if (collision_count % polling_frequency == 0) or (collision_count == total_collisons):
            # Collect measurements
            coll_key = f"collision_{collision_count}"
            step_data = {}
            if "entropy" in measurements:
                step_data["entropy"] = soup.population_entropy()
            if "unique_expressions" in measurements:
                step_data["unique_expressions"] = soup.unique_expressions()
            # Optional: store entire soup state (could be large)
            step_data["state"] = soup.expressions()
            
            results_data[coll_key] = step_data
    
    # Return a structured dictionary with all relevant output
    return {
        "config": config,
        "generated_expressions": expressions,
        "collisions_data": results_data
    }

if __name__ == "__main__":
    """
    1) Gather config from user (including BTree/Fontana parameters).
    2) Save that config to a JSON file.
    3) Run the experiment, printing and returning results.
    4) Save final results (config + experiment data) to a separate JSON
       or the same JSON file, depending on your needs.
    """
    # 1) Gather user config
    config = gather_user_parameters()
    
    # 2) Ask user for a filename to save the config JSON
    output_file = input("\nEnter output JSON filename (default: experiment_config.json): ").strip() or "experiment_config.json"
    
    # 3) Write config to JSON
    with open(output_file, "w") as f:
        json.dump(config, f, indent=4)
    
    print(f"\nConfiguration saved to '{output_file}':\n")
    print(json.dumps(config, indent=4))
    
    # 4) Run the experiment
    print("\n--- Running Experiment ---")
    experiment_results = single_experiment(config)
    
    # 5) Print final experiment results summary
    print("\nExperiment complete. Summary of final collisions_data keys:")
    for key in experiment_results["collisions_data"]:
        print("  ", key)
    
    # 6) Write the entire experiment results (including config + collisions_data) to JSON
    results_file = "experiment_output.json"
    with open(results_file, "w") as f:
        json.dump(experiment_results, f, indent=4)
    
    print(f"\nExperiment results saved to '{results_file}'.\n")

