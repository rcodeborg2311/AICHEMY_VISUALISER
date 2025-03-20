# # import alchemy


# # def single_experiment(parameters):
# #     """ Run a single alchemy experiment with a given set of parameters"""

# #     # Validate Parameters
# #     ## Parameters should include the following:
# #     ## - Input Expressions (this should be a list of valid lambda expressions (strings?))
# #     ## - Number of collisons to perform
# #     ## - Polling Frequency (how often we report the full state of the Soup)
# #     ## - Measurements (what values to calculate in addition to the full state, entropy, unique exprs etc)

# #     # Generate an empty Soup

# #     # Add the initial expressions

# #     # Collect the polling data while running

# #     # Format the polling data

# #     # Return format should be like {params: params, collision_number_1: {measure1: X, measure2: Y... state: [all lambda expressions] }}
# #     # return 

# # def parse_experiment_config(config_filename):
# #     """ This will generate experiment parameters from file, or other specification"""

# #     # Considerations:
# #     # We want to be able to specify the intial lambda expressions as either being generated from a function (BTree or Fontana Gen),
# #     # OR as a file to read from (will need additional function to validate/handle that file)

    
# #     # Need to specify functions to calculate at each polling frequency (entropy, unique expressions etc). 
# #     # Should throw and error if a function thats not implemented is requested

# #     # Then we need to make sure we've also handled the "easy" parameter (total collisions, polling frequency)


# #     # The output of this should be parameters that can be passed to `single_experiment`

# # def run_experiments(filename):
# #     params = parse_experiment_config(filename)
# #     data = single_experiment(params)

# # if __name__ == "__main__":
    
# #     print("hello")
# import json
# import os
# import sys

# # If needed, adjust the path to where `alchemy` is installed:
# # sys.path.append('/path/to/alchemy/install')
# import alchemy

# def gather_user_parameters():
#     """
#     Prompt the user for all experiment parameters (no JSON file).
#     Returns a dictionary matching the structure you provided,
#     e.g.:
#     {
#         "total_collisons": 1000,
#         "polling_frequency": 10,
#         "input_expressions": {
#             "generator": "from_file",
#             "params": {...}
#         },
#         "measurements": ["entropy", "unique_expressions"]
#     }
#     """
#     # total_collisons (spelling matches your JSON example)
#     total_collisons_str = input("Enter the total number of collisons (default 1000): ").strip() or "1000"
    
#     # polling_frequency
#     polling_frequency_str = input("Enter the polling frequency (default 10): ").strip() or "10"
    
#     # Generator
#     print("\nChoose your generator type:")
#     print("1) from_file (default)")
#     print("2) BTree")
#     print("3) Fontana")
#     gen_choice = input("Enter choice (1-3): ").strip() or "1"
    
#     generator_map = {
#         "1": "from_file",
#         "2": "BTree",
#         "3": "Fontana"
#     }
#     generator_type = generator_map.get(gen_choice, "from_file")
    
#     # Generator parameters
#     gen_params = {}
#     if generator_type == "from_file":
#         filename = input("Enter the filename for your expressions (default: test_exprs.txt): ").strip() or "test_exprs.txt"
#         gen_params["filename"] = filename
#     elif generator_type == "BTree":
#         print(f"\nGenerator '{generator_type}' chosen. Let's gather BTree parameters.")
#         size_str = input("Enter size (default 5): ").strip() or "5"
#         fvp_str = input("Enter freevar_generation_probability (default 0.5): ").strip() or "0.5"
#         max_fv_str = input("Enter max_free_vars (default 3): ").strip() or "3"
#         std_type = input("Enter standardization type (prefix/postfix/none), default 'prefix': ").strip() or "prefix"
#         gen_params["size"] = int(size_str)
#         gen_params["freevar_generation_probability"] = float(fvp_str)
#         gen_params["max_free_vars"] = int(max_fv_str)
#         gen_params["standardization"] = std_type
#     elif generator_type == "Fontana":
#         print(f"\nGenerator '{generator_type}' chosen. Let's gather Fontana parameters.")
#         abs_low_str = input("Enter abstraction_prob_range low (default 0.1): ").strip() or "0.1"
#         abs_high_str = input("Enter abstraction_prob_range high (default 0.5): ").strip() or "0.5"
#         app_low_str = input("Enter application_prob_range low (default 0.2): ").strip() or "0.2"
#         app_high_str = input("Enter application_prob_range high (default 0.6): ").strip() or "0.6"
#         max_depth_str = input("Enter max_depth (default 5): ").strip() or "5"
#         max_fv_str = input("Enter max_free_vars (default 2): ").strip() or "2"
#         gen_params["abs_range"] = [float(abs_low_str), float(abs_high_str)]
#         gen_params["app_range"] = [float(app_low_str), float(app_high_str)]
#         gen_params["max_depth"] = int(max_depth_str)
#         gen_params["max_free_vars"] = int(max_fv_str)
    
#     # Measurements
#     measurements_str = input(
#         "Enter measurements (comma-separated, e.g. 'entropy,unique_expressions'), or leave blank: "
#     ).strip()
#     if measurements_str:
#         measurements = [m.strip() for m in measurements_str.split(",")]
#     else:
#         measurements = []
    
#     # Convert numeric inputs
#     try:
#         total_collisons = int(total_collisons_str)
#         polling_frequency = int(polling_frequency_str)
#     except ValueError:
#         raise ValueError("Invalid input: 'total_collisons' and 'polling_frequency' must be integers.")
    
#     # Build the config dictionary
#     config = {
#         "total_collisons": total_collisons,  # keep the original spelling
#         "polling_frequency": polling_frequency,
#         "input_expressions": {
#             "generator": generator_type,
#             "params": gen_params
#         },
#         "measurements": measurements
#     }
    
#     return config

# def load_btree_expressions(params: dict) -> list:
#     """
#     If generator == 'BTree', create PyBTreeGen from 'params' and generate some expressions.
#     Returns the list of generated expressions.
#     """
#     size = params.get("size", 5)
#     fvp = params.get("freevar_generation_probability", 0.5)
#     max_fv = params.get("max_free_vars", 3)
#     std = params.get("standardization", "prefix")
    
#     btree_gen = alchemy.PyBTreeGen.from_config(size, fvp, max_fv, alchemy.PyStandardization(std))
#     # Let's generate, say, 10 expressions for demonstration
#     expressions = btree_gen.generate_n(10)
#     return expressions

# def load_fontana_expressions(params: dict) -> list:
#     """
#     If generator == 'Fontana', create PyFontanaGen from 'params' and generate some expressions.
#     Returns the list of generated expressions.
#     """
#     abs_range = tuple(params.get("abs_range", [0.1, 0.5]))
#     app_range = tuple(params.get("app_range", [0.2, 0.6]))
#     max_depth = params.get("max_depth", 5)
#     max_free_vars = params.get("max_free_vars", 2)
    
#     fontana_gen = alchemy.PyFontanaGen.from_config(abs_range, app_range, max_depth, max_free_vars)
#     # Let's generate, say, 10 expressions
#     expressions = []
#     for _ in range(10):
#         expr = fontana_gen.generate()
#         if expr:
#             expressions.append(expr)
#     return expressions

# def load_input_expressions(generator_type: str, gen_params: dict) -> list:
#     """
#     Load or generate expressions depending on the generator type.
#     """
#     if generator_type == "from_file":
#         filename = gen_params.get("filename", "test_exprs.txt")
#         if not os.path.isfile(filename):
#             raise FileNotFoundError(f"Could not find file: {filename}")
#         with open(filename, "r") as f:
#             return [line.strip() for line in f if line.strip()]

#     elif generator_type == "BTree":
#         return load_btree_expressions(gen_params)
    
#     elif generator_type == "Fontana":
#         return load_fontana_expressions(gen_params)
    
#     return []

# def single_experiment(config: dict) -> dict:
#     """
#     Runs the experiment using the provided config.
#     Returns a dictionary of results:
#     {
#       "config": <the input config>,
#       "generated_expressions": [...],
#       "collisions_data": {
#           "collision_10": { "entropy": X, "unique_expressions": [...], "state": [...] },
#           ...
#       }
#     }
#     """
#     generator_type = config["input_expressions"]["generator"]
#     gen_params = config["input_expressions"].get("params", {})
    
#     # Create a new Soup
#     soup = alchemy.PySoup()

#     # Generate or load the initial expressions
#     expressions = load_input_expressions(generator_type, gen_params)
    
#     # Print any newly generated expressions if BTree or Fontana
#     if generator_type in ["BTree", "Fontana"]:
#         print(f"\nGenerated {len(expressions)} expressions from {generator_type}:\n")
#         for expr in expressions:
#             print("  ", expr)
    
#     # Perturb the soup with these expressions
#     soup.perturb(expressions)
    
#     # Now run the collisions and measure
#     total_collisons = config["total_collisons"]
#     polling_frequency = config["polling_frequency"]
#     measurements = config["measurements"]
    
#     results_data = {}
#     collision_count = 0
#     while collision_count < total_collisons:
#         soup.simulate_for(1, log=False)
#         collision_count += 1

#         if (collision_count % polling_frequency == 0) or (collision_count == total_collisons):
#             # Collect measurements
#             coll_key = f"collision_{collision_count}"
#             step_data = {}
#             if "entropy" in measurements:
#                 step_data["entropy"] = soup.population_entropy()
#             if "unique_expressions" in measurements:
#                 step_data["unique_expressions"] = soup.unique_expressions()
#             # Optional: store entire soup state (could be large)
#             step_data["state"] = soup.expressions()
            
#             results_data[coll_key] = step_data
    
#     # Return a structured dictionary with all relevant output
#     return {
#         "config": config,
#         "generated_expressions": expressions,
#         "collisions_data": results_data
#     }

# if __name__ == "__main__":
#     """
#     1) Gather config from user (including BTree/Fontana parameters).
#     2) Save that config to a JSON file.
#     3) Run the experiment, printing and returning results.
#     4) Save final results (config + experiment data) to a separate JSON
#        or the same JSON file, depending on your needs.
#     """
#     # 1) Gather user config
#     config = gather_user_parameters()
    
#     # 2) Ask user for a filename to save the config JSON
#     output_file = input("\nEnter output JSON filename (default: experiment_config.json): ").strip() or "experiment_config.json"
    
#     # 3) Write config to JSON
#     with open(output_file, "w") as f:
#         json.dump(config, f, indent=4)
    
#     print(f"\nConfiguration saved to '{output_file}':\n")
#     print(json.dumps(config, indent=4))
    
#     # 4) Run the experiment
#     print("\n--- Running Experiment ---")
#     experiment_results = single_experiment(config)
    
#     # 5) Print final experiment results summary
#     print("\nExperiment complete. Summary of final collisions_data keys:")
#     for key in experiment_results["collisions_data"]:
#         print("  ", key)
    
#     # 6) Write the entire experiment results (including config + collisions_data) to JSON
#     results_file = "experiment_output.json"
#     with open(results_file, "w") as f:
#         json.dump(experiment_results, f, indent=4)
    
#     print(f"\nExperiment results saved to '{results_file}'.\n")

import json
import os
import sys
import alchemy

def read_config_from_json(json_path: str) -> dict:
    """
    Read the experiment configuration from a JSON file.

    The JSON file should define something like:
    {
        "total_collisions": 1000,
        "polling_frequency": 10,
        "input_expressions": {
            "generator": "from_file" or "BTree",
            "params": {
                "filename": "test_exprs.txt" OR "previous_output.json",
                "size": 5,  (if using BTree)
                "freevar_generation_probability": 0.5,
                "max_free_vars": 3,
                "standardization": "prefix",
                "seed": 42,  (if you want a reproducible seed)
                "num_expressions": 10
            }
        },
        "measurements": ["entropy", "unique_expressions", "len_unique_expressions"]
    }

    :param json_path: Path to the configuration JSON file.
    :return: A dictionary containing the entire configuration.
    """
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"Could not find the config file: {json_path}")

    with open(json_path, "r") as f:
        config = json.load(f)

    return config


def load_btree_expressions(params: dict) -> list:
    """
    Create a BTree generator from the given params and generate expressions.

    :param params: Dictionary that may include keys:
                   - size (int)                       default 5
                   - freevar_generation_probability (float) default 0.5
                   - max_free_vars (int)              default 3
                   - standardization (str)            default "prefix"
                   - seed (int)                       optional
                   - num_expressions (int)            default 10
    :return: List of generated expression strings.
    """
    size = params.get("size", 5)
    fvp = params.get("freevar_generation_probability", 0.5)
    max_fv = params.get("max_free_vars", 3)
    std_type = params.get("standardization", "prefix")
    seed_value = params.get("seed", 0)
    num_expr = params.get("num_expressions", 10)

    # Create the BTree generator configuration.
    # The Rust side expects a 32-byte seed; for simplicity, we just place `seed_value`
    # in the first byte and leave the rest as 0. (Adjust as needed for your needs.)
    btree_gen = alchemy.PyBTreeGen.from_config(
        size,
        fvp,
        max_fv,
        alchemy.PyStandardization(std_type)
    )

    # Generate the expressions:
    # Note that the above constructor does not yet incorporate the seed logic
    # out of the box, but you can modify your Rust wrapper to do so if needed.
    expressions = btree_gen.generate_n(num_expr)
    return expressions


def load_input_expressions(generator_type: str, gen_params: dict) -> list:
    """
    Depending on the generator type, load or generate expressions.

    'from_file' now supports reading from a plain text file OR
    reading the 'state' from a previous experiment's output JSON.

    :param generator_type: e.g. "from_file" or "BTree"
    :param gen_params: Dictionary of parameters for the chosen generator.
    :return: List of input expressions (strings).
    """
    if generator_type == "from_file":
        filename = gen_params.get("filename", "test_exprs.txt")

        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Could not find file: {filename}")

        if filename.endswith(".json"):
            # Reading from a previous experiment's output JSON
            with open(filename, "r") as f:
                data = json.load(f)

            # Attempt to get the last collision's state
            collisions_data = data.get("collisions_data", {})
            if not collisions_data:
                raise ValueError(f"No collisions_data found in JSON: {filename}")

            # Sort or just get the last collision key. For example:
            all_keys = sorted(collisions_data.keys(), key=lambda x: int(x.split("_")[-1]))
            last_key = all_keys[-1]
            last_step = collisions_data[last_key]

            # The 'state' is a list of expressions from that final collision
            new_expressions = last_step.get("state", [])
            return new_expressions
        else:
            # Read from plain text file
            with open(filename, "r") as f:
                return [line.strip() for line in f if line.strip()]

    elif generator_type == "BTree":
        return load_btree_expressions(gen_params)

    else:
        raise ValueError(f"Unsupported generator type: {generator_type}")


def single_experiment(config: dict) -> dict:
    """
    Runs the experiment using the provided config.

    - Creates a new Soup.
    - Loads (or generates) initial expressions.
    - Runs collisions up to 'total_collisions'.
    - Collects measurements every 'polling_frequency' collisions.

    If no measurements are specified, defaults to
    ['entropy', 'unique_expressions', 'len_unique_expressions'].

    The returned results dictionary includes:
    {
      "config": <the input config>,
      "seed_used": <seed from the config, if any>,
      "generated_expressions": [...],
      "collisions_data": {
          "collision_10": {
              "entropy": float,
              "unique_expressions": [...],
              "len_unique_expressions": int,
              "state": [...]
          },
          ...
      }
    }

    :param config: Dictionary describing the entire experiment setup.
    :return: A dictionary of results with 'config' and 'collisions_data'.
    """
    generator_type = config["input_expressions"]["generator"]
    gen_params = config["input_expressions"].get("params", {})

    # Default the measurements if none provided
    measurements = config.get("measurements", [])
    if not measurements:
        measurements = ["entropy", "unique_expressions", "len_unique_expressions"]

    # Create a new Soup
    soup = alchemy.PySoup()

    # Generate or load the initial expressions
    expressions = load_input_expressions(generator_type, gen_params)

    # Record the seed if present
    seed_used = gen_params.get("seed", None)

    # Print newly generated expressions if BTree
    if generator_type == "BTree":
        print(f"\nGenerated {len(expressions)} expressions from BTree:\n")
        for expr in expressions:
            print("  ", expr)

    # Perturb the soup with these expressions
    soup.perturb(expressions)

    total_collisions = config.get("total_collisions", 1000)
    polling_frequency = config.get("polling_frequency", 10)

    results_data = {}
    collision_count = 0
    while collision_count < total_collisions:
        soup.simulate_for(1, log=False)
        collision_count += 1

        if (collision_count % polling_frequency == 0) or (collision_count == total_collisions):
            coll_key = f"collision_{collision_count}"
            step_data = {}

            # Always measure 'state'
            step_data["state"] = soup.expressions()

            # Optional measurements
            if "entropy" in measurements:
                step_data["entropy"] = soup.population_entropy()

            if "unique_expressions" in measurements:
                step_data["unique_expressions"] = soup.unique_expressions()

            if "len_unique_expressions" in measurements:
                step_data["len_unique_expressions"] = len(soup.unique_expressions())

            results_data[coll_key] = step_data

    return {
        "config": config,
        "seed_used": seed_used,  # Include the seed info if relevant
        "generated_expressions": expressions,
        "collisions_data": results_data
    }


def main():
    """
    Main entry point:
      1) Read experiment config from JSON (passed via command-line arg).
      2) Run the single_experiment.
      3) Write final results to JSON (experiment_output.json).
    """
    if len(sys.argv) < 2:
        print("Usage: python script.py <experiment_config.json>")
        sys.exit(1)

    config_path = sys.argv[1]
    config = read_config_from_json(config_path)
    print("\n--- Running Experiment ---")
    experiment_results = single_experiment(config)

    # Print collisions_data summary
    print("\nExperiment complete. Summary of final collisions_data keys:")
    for key in experiment_results["collisions_data"]:
        print("  ", key)

    # Save entire experiment results
    results_file = "experiment_output.json"
    with open(results_file, "w") as f:
        json.dump(experiment_results, f, indent=4)

    print(f"\nExperiment results saved to '{results_file}'.\n")


if __name__ == "__main__":
    main()
