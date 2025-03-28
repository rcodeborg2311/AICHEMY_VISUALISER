# # # # import alchemy


# # # # def single_experiment(parameters):
# # # #     """ Run a single alchemy experiment with a given set of parameters"""

# # # #     # Validate Parameters
# # # #     ## Parameters should include the following:
# # # #     ## - Input Expressions (this should be a list of valid lambda expressions (strings?))
# # # #     ## - Number of collisons to perform
# # # #     ## - Polling Frequency (how often we report the full state of the Soup)
# # # #     ## - Measurements (what values to calculate in addition to the full state, entropy, unique exprs etc)

# # # #     # Generate an empty Soup

# # # #     # Add the initial expressions

# # # #     # Collect the polling data while running

# # # #     # Format the polling data

# # # #     # Return format should be like {params: params, collision_number_1: {measure1: X, measure2: Y... state: [all lambda expressions] }}
# # # #     # return 

# # # # def parse_experiment_config(config_filename):
# # # #     """ This will generate experiment parameters from file, or other specification"""

# # # #     # Considerations:
# # # #     # We want to be able to specify the intial lambda expressions as either being generated from a function (BTree or Fontana Gen),
# # # #     # OR as a file to read from (will need additional function to validate/handle that file)

    
# # # #     # Need to specify functions to calculate at each polling frequency (entropy, unique expressions etc). 
# # # #     # Should throw and error if a function thats not implemented is requested

# # # #     # Then we need to make sure we've also handled the "easy" parameter (total collisions, polling frequency)


# # # #     # The output of this should be parameters that can be passed to `single_experiment`

# # # # def run_experiments(filename):
# # # #     params = parse_experiment_config(filename)
# # # #     data = single_experiment(params)

# # # # if __name__ == "__main__":
    
# # # #     print("hello")

# import json
# import os
# import sys
# import alchemy

# def read_config_from_json(json_path: str) -> dict:
#     """
#     Read the experiment configuration from a JSON file.

#     The JSON file should define something like:
#     {
#         "total_collisions": 1000,
#         "polling_frequency": 10,
#         "input_expressions": {
#             "generator": "from_file" or "BTree",
#             "params": {
#                 "filename": "test_exprs.txt" OR "previous_output.json",
#                 "size": 5,  (if using BTree)
#                 "freevar_generation_probability": 0.5,
#                 "max_free_vars": 3,
#                 "standardization": "prefix",
#                 "seed": 42,  (if you want a reproducible seed)
#                 "num_expressions": 10
#             }
#         },
#         "measurements": ["entropy", "unique_expressions", "len_unique_expressions"]
#     }

#     :param json_path: Path to the configuration JSON file.
#     :return: A dictionary containing the entire configuration.
#     """
#     if not os.path.isfile(json_path):
#         raise FileNotFoundError(f"Could not find the config file: {json_path}")

#     with open(json_path, "r") as f:
#         config = json.load(f)

#     return config


# def load_btree_expressions(params: dict) -> list:
#     """
#     Create a BTree generator from the given params and generate expressions.

#     :param params: Dictionary that may include keys:
#                    - size (int)                       default 5
#                    - freevar_generation_probability (float) default 0.5
#                    - max_free_vars (int)              default 3
#                    - standardization (str)            default "prefix"
#                    - seed (int)                       optional
#                    - num_expressions (int)            default 10
#     :return: List of generated expression strings.
#     """
#     size = params.get("size", 5)
#     fvp = params.get("freevar_generation_probability", 0.5)
#     max_fv = params.get("max_free_vars", 3)
#     std_type = params.get("standardization", "prefix")
#     seed_value = params.get("seed", 0)
#     num_expr = params.get("num_expressions", 1000)

#     # Create the BTree generator configuration.
#     # The Rust side expects a 32-byte seed; for simplicity, we just place `seed_value`
#     # in the first byte and leave the rest as 0. (Adjust as needed for your needs.)
#     btree_gen = alchemy.PyBTreeGen.from_config(
#         size,
#         fvp,
#         max_fv,
#         alchemy.PyStandardization(std_type)
#     )

#     # Generate the expressions:
#     # Note that the above constructor does not yet incorporate the seed logic
#     # out of the box, but you can modify your Rust wrapper to do so if needed.
#     expressions = btree_gen.generate_n(num_expr)
#     return expressions


# def load_input_expressions(generator_type: str, gen_params: dict) -> list:
#     """
#     Depending on the generator type, load or generate expressions.

#     'from_file' now supports reading from a plain text file OR
#     reading the 'state' from a previous experiment's output JSON.

#     :param generator_type: e.g. "from_file" or "BTree"
#     :param gen_params: Dictionary of parameters for the chosen generator.
#     :return: List of input expressions (strings).
#     """
#     if generator_type == "from_file":
#         filename = gen_params.get("filename", "test_exprs.txt")

#         if not os.path.isfile(filename):
#             raise FileNotFoundError(f"Could not find file: {filename}")

#         if filename.endswith(".json"):
#             # Reading from a previous experiment's output JSON
#             with open(filename, "r") as f:
#                 data = json.load(f)

#             # Attempt to get the last collision's state
#             collisions_data = data.get("collisions_data", {})
#             if not collisions_data:
#                 raise ValueError(f"No collisions_data found in JSON: {filename}")

#             # Sort or just get the last collision key. For example:
#             all_keys = sorted(collisions_data.keys(), key=lambda x: int(x.split("_")[-1]))
#             last_key = all_keys[-1]
#             last_step = collisions_data[last_key]

#             # The 'state' is a list of expressions from that final collision
#             new_expressions = last_step.get("state", [])
#             return new_expressions
#         else:
#             # Read from plain text file
#             with open(filename, "r") as f:
#                 return [line.strip() for line in f if line.strip()]

#     elif generator_type == "BTree":
#         return load_btree_expressions(gen_params)

#     else:
#         raise ValueError(f"Unsupported generator type: {generator_type}")


# def single_experiment(config: dict) -> dict:
#     """
#     Runs the experiment using the provided config.

#     - Creates a new Soup.
#     - Loads (or generates) initial expressions.
#     - Runs collisions up to 'total_collisions'.
#     - Collects measurements every 'polling_frequency' collisions.

#     If no measurements are specified, defaults to
#     ['entropy', 'unique_expressions', 'len_unique_expressions'].

#     The returned results dictionary includes:
#     {
#       "config": <the input config>,
#       "seed_used": <seed from the config, if any>,
#       "generated_expressions": [...],
#       "collisions_data": {
#           "collision_10": {
#               "entropy": float,
#               "unique_expressions": [...],
#               "len_unique_expressions": int,
#               "state": [...]
#           },
#           ...
#       }
#     }

#     :param config: Dictionary describing the entire experiment setup.
#     :return: A dictionary of results with 'config' and 'collisions_data'.
#     """
#     generator_type = config["input_expressions"]["generator"]
#     gen_params = config["input_expressions"].get("params", {})

#     # Default the measurements if none provided
#     measurements = config.get("measurements", [])
#     if not measurements:
#         measurements = ["entropy", "unique_expressions", "len_unique_expressions"]

#     # Create a new Soup
#     soup = alchemy.PySoup()

#     # Generate or load the initial expressions
#     expressions = load_input_expressions(generator_type, gen_params)

#     # Record the seed if present
#     seed_used = gen_params.get("seed", None)

#     # Print newly generated expressions if BTree
#     if generator_type == "BTree":
#         print(f"\nGenerated {len(expressions)} expressions from BTree:\n")
#         for expr in expressions:
#             print("  ", expr)

#     # Perturb the soup with these expressions
#     soup.perturb(expressions)

#     total_collisions = config.get("total_collisions", 1000)
#     polling_frequency = config.get("polling_frequency", 10)

#     results_data = {}
#     collision_count = 0
#     while collision_count < total_collisions:
#         soup.simulate_for(1, log=False)
#         collision_count += 1

#         if (collision_count % polling_frequency == 0) or (collision_count == total_collisions):
#             coll_key = f"collision_{collision_count}"
#             step_data = {}

#             # Always measure 'state'
#             step_data["state"] = soup.expressions()

#             # Optional measurements
#             if "entropy" in measurements:
#                 step_data["entropy"] = soup.population_entropy()

#             if "unique_expressions" in measurements:
#                 step_data["unique_expressions"] = soup.unique_expressions()

#             if "len_unique_expressions" in measurements:
#                 step_data["len_unique_expressions"] = len(soup.unique_expressions())

#             results_data[coll_key] = step_data

    
#     # Grab the last collision key only
#     # Include both full history and final snapshot
#     last_collision_key = sorted(results_data.keys(), key=lambda x: int(x.split("_")[-1]))[-1]
#     last_collision = results_data[last_collision_key]

#     return {
#         "config": config,
#         "seed_used": seed_used,
#         "generated_expressions": expressions,
#         "collisions_data": results_data,
#         "last_state": {
#             last_collision_key: last_collision
#         }
#     }


# def main():
#     """
#     Interactive experiment loop:
#     - Runs an experiment based on a provided config file
#     - Saves output JSON and last-state expressions
#     - Offers to continue from last state or start a new config
#     """
#     if len(sys.argv) < 2:
#         print("Usage: python script.py <experiment_config.json>")
#         sys.exit(1)

#     run_id = 1
#     config_path = sys.argv[1]

#     while True:
#         config = read_config_from_json(config_path)
#         print(f"\n--- Running Experiment #{run_id} ---")
#         experiment_results = single_experiment(config)

#         # Print final collision keys
#         if "collisions_data" in experiment_results:
#             print("\nExperiment complete. Final collision keys:")
#             for key in experiment_results["collisions_data"]:
#                 print("  ", key)

#         # Save results to JSON
#         output_file = f"experiment_output_{run_id}.json"
#         with open(output_file, "w") as f:
#             json.dump(experiment_results, f, indent=4)
#         print(f"\n✅ Experiment results saved to: {output_file}")

#         # Extract and save last state
#         last_state = experiment_results.get("last_state")
#         if last_state:
#             last_key = list(last_state.keys())[0]
#             final_exprs = last_state[last_key].get("state", [])
#             txt_file = f"last_state_exprs_{run_id}.txt"
#             with open(txt_file, "w") as f:
#                 for expr in final_exprs:
#                     f.write(expr + "\n")
#             print(f"✅ Final state expressions saved to: {txt_file}")
#         else:
#             print("⚠️  No last state found — cannot continue from this run.")
#             break

#         # Ask user what they want to do next
#         print("\nWhat would you like to do next?")
#         print("1) Continue experiment from last state")
#         print("2) Start a new experiment with a different config")
#         print("3) Exit")
#         choice = input("Enter your choice (1/2/3): ").strip()

#         if choice == "1":
#             # Create next config file
#             run_id += 1
#             config_path = f"auto_followup_config_{run_id}.json"
#             next_config = {
#                 "total_collisions": config.get("total_collisions", 50),
#                 "polling_frequency": config.get("polling_frequency", 10),
#                 "input_expressions": {
#                     "generator": "from_file",
#                     "params": {
#                         "filename": txt_file
#                     }
#                 },
#                 "measurements": config.get("measurements", [
#                     "entropy", "unique_expressions", "len_unique_expressions"
#                 ])
#             }

#             with open(config_path, "w") as f:
#                 json.dump(next_config, f, indent=4)

#             print(f"\n🧪 New follow-up config created: {config_path}")

#         elif choice == "2":
#             new_path = input("Enter the new config filename (e.g. new_experiment.json): ").strip()
#             if not os.path.exists(new_path):
#                 print(f"❌ File '{new_path}' not found. Exiting.")
#                 break
#             config_path = new_path
#             run_id = 1  # Reset counter for new chain

#         else:
#             print("👋 Exiting experiment loop.")
#             break

# if __name__ == "__main__":
#     main()



# import json
# import os
# import sys
# import alchemy

# def read_config_from_json(json_path: str) -> dict:
#     """
#     Read the experiment configuration from a JSON file.
#     """
#     if not os.path.isfile(json_path):
#         raise FileNotFoundError(f"Could not find the config file: {json_path}")

#     with open(json_path, "r") as f:
#         config = json.load(f)

#     return config


# def load_btree_expressions(params: dict) -> list:
#     """
#     Create a BTree generator from the given params and generate expressions.
#     """
#     size = params.get("size", 5)
#     fvp = params.get("freevar_generation_probability", 0.5)
#     max_fv = params.get("max_free_vars", 3)
#     std_type = params.get("standardization", "prefix")
#     seed_value = params.get("seed", 0)
#     num_expr = params.get("num_expressions", 1000)

#     btree_gen = alchemy.PyBTreeGen.from_config(
#         size,
#         fvp,
#         max_fv,
#         alchemy.PyStandardization(std_type)
#     )
#     expressions = btree_gen.generate_n(num_expr)
#     return expressions


# def load_input_expressions(generator_type: str, gen_params: dict) -> list:
#     """
#     Depending on the generator type, load or generate expressions.
#     """
#     if generator_type == "from_file":
#         filename = gen_params.get("filename", "test_exprs.txt")

#         if not os.path.isfile(filename):
#             raise FileNotFoundError(f"Could not find file: {filename}")

#         if filename.endswith(".json"):
#             # Reading from a previous experiment's output JSON
#             with open(filename, "r") as f:
#                 data = json.load(f)

#             collisions_data = data.get("collisions_data", {})
#             if not collisions_data:
#                 raise ValueError(f"No collisions_data found in JSON: {filename}")

#             all_keys = sorted(collisions_data.keys(), key=lambda x: int(x.split("_")[-1]))
#             last_key = all_keys[-1]
#             last_step = collisions_data[last_key]
#             new_expressions = last_step.get("state", [])
#             return new_expressions

#         else:
#             with open(filename, "r") as f:
#                 return [line.strip() for line in f if line.strip()]

#     elif generator_type == "BTree":
#         return load_btree_expressions(gen_params)

#     else:
#         raise ValueError(f"Unsupported generator type: {generator_type}")


# def single_experiment(config: dict) -> dict:
#     """
#     Runs the experiment using the provided config.
#     """
#     generator_type = config["input_expressions"]["generator"]
#     gen_params = config["input_expressions"].get("params", {})

#     measurements = config.get("measurements", [])
#     if not measurements:
#         measurements = ["entropy", "unique_expressions", "len_unique_expressions"]

#     soup = alchemy.PySoup()
#     expressions = load_input_expressions(generator_type, gen_params)
#     seed_used = gen_params.get("seed", None)

#     if generator_type == "BTree":
#         print(f"\nGenerated {len(expressions)} expressions from BTree:\n")
#         for expr in expressions:
#             print("  ", expr)

#     soup.perturb(expressions)

#     total_collisions = config.get("total_collisions", 1000)
#     polling_frequency = config.get("polling_frequency", 10)

#     results_data = {}
#     collision_count = 0
#     while collision_count < total_collisions:
#         soup.simulate_for(1, log=False)
#         collision_count += 1

#         if (collision_count % polling_frequency == 0) or (collision_count == total_collisions):
#             coll_key = f"collision_{collision_count}"
#             step_data = {}
#             step_data["state"] = soup.expressions()
#             if "entropy" in measurements:
#                 step_data["entropy"] = soup.population_entropy()
#             if "unique_expressions" in measurements:
#                 step_data["unique_expressions"] = soup.unique_expressions()
#             if "len_unique_expressions" in measurements:
#                 step_data["len_unique_expressions"] = len(soup.unique_expressions())
#             results_data[coll_key] = step_data

#     last_collision_key = sorted(results_data.keys(), key=lambda x: int(x.split("_")[-1]))[-1]
#     last_collision = results_data[last_collision_key]

#     return {
#         "config": config,
#         "seed_used": seed_used,
#         "generated_expressions": expressions,
#         "collisions_data": results_data,
#         "last_state": {
#             last_collision_key: last_collision
#         }
#     }


# def prompt_for_config_overrides(base_config: dict) -> dict:
#     """
#     Prompt user to override certain fields in the config.
#     Returns a new config dict with updated or unchanged fields.
#     """
#     new_config = base_config.copy()
#     print("\n--- Override Config Fields (leave blank to keep current) ---")

#     # total_collisions
#     current_collisions = new_config.get("total_collisions", 1000)
#     override = input(f"total_collisions [{current_collisions}]: ").strip()
#     if override:
#         try:
#             new_config["total_collisions"] = int(override)
#         except ValueError:
#             print("Invalid input, keeping old collisions.")

#     # polling_frequency
#     current_pf = new_config.get("polling_frequency", 10)
#     override = input(f"polling_frequency [{current_pf}]: ").strip()
#     if override:
#         try:
#             new_config["polling_frequency"] = int(override)
#         except ValueError:
#             print("Invalid input, keeping old polling_frequency.")

#     # measurements
#     current_measurements = new_config.get("measurements", ["entropy", "unique_expressions"])
#     print(f"Current measurements: {current_measurements}")
#     override = input("New measurements (comma-separated) or blank to keep: ").strip()
#     if override:
#         items = [x.strip() for x in override.split(",") if x.strip()]
#         new_config["measurements"] = items

#     # input_expressions
#     if "input_expressions" not in new_config:
#         new_config["input_expressions"] = {}
#     if "generator" not in new_config["input_expressions"]:
#         new_config["input_expressions"]["generator"] = "from_file"

#     curr_gen = new_config["input_expressions"]["generator"]
#     override = input(f"Generator type (from_file/BTree) [{curr_gen}]: ").strip()
#     if override:
#         new_config["input_expressions"]["generator"] = override

#     # If generator=from_file, prompt for filename:
#     if new_config["input_expressions"]["generator"] == "from_file":
#         if "params" not in new_config["input_expressions"]:
#             new_config["input_expressions"]["params"] = {}
#         curr_fn = new_config["input_expressions"]["params"].get("filename", "test_exprs.txt")
#         override = input(f"Filename for from_file [{curr_fn}]: ").strip()
#         if override:
#             new_config["input_expressions"]["params"]["filename"] = override

#     # If generator=BTree, override some fields
#     if new_config["input_expressions"]["generator"] == "BTree":
#         if "params" not in new_config["input_expressions"]:
#             new_config["input_expressions"]["params"] = {}
#         curr_n = new_config["input_expressions"]["params"].get("num_expressions", 50)
#         override = input(f"num_expressions for BTree [{curr_n}]: ").strip()
#         if override:
#             try:
#                 new_config["input_expressions"]["params"]["num_expressions"] = int(override)
#             except ValueError:
#                 print("Invalid, keeping old num_expressions.")

#         # Add more as needed for 'size', 'freevar_generation_probability', etc.

#     print("\n--- Done overriding config fields ---\n")
#     return new_config


# def main():
#     """
#     Interactive experiment loop:
#     """
#     if len(sys.argv) < 2:
#         print("Usage: python script.py <experiment_config.json>")
#         sys.exit(1)

#     run_id = 1
#     config_path = sys.argv[1]

#     while True:
#         config = read_config_from_json(config_path)
#         print(f"\n--- Running Experiment #{run_id} ---")
#         experiment_results = single_experiment(config)

#         # Print final collision keys
#         if "collisions_data" in experiment_results:
#             print("\nExperiment complete. Final collision keys:")
#             for key in experiment_results["collisions_data"]:
#                 print("  ", key)

#         # Save results to JSON
#         output_file = f"experiment_output_{run_id}.json"
#         with open(output_file, "w") as f:
#             json.dump(experiment_results, f, indent=4)
#         print(f"\n✅ Experiment results saved to: {output_file}")

#         # Extract and save last state
#         last_state = experiment_results.get("last_state")
#         if last_state:
#             last_key = list(last_state.keys())[0]
#             final_exprs = last_state[last_key].get("state", [])
#             txt_file = f"last_state_exprs_{run_id}.txt"
#             with open(txt_file, "w") as f:
#                 for expr in final_exprs:
#                     f.write(expr + "\n")
#             print(f"✅ Final state expressions saved to: {txt_file}")
#         else:
#             print("⚠️  No last state found — cannot continue from this run.")
#             break

#         print("\nWhat would you like to do next?")
#         print("1) Continue experiment from last state")
#         print("2) Start a new experiment with a different config")
#         print("3) Perturb a prior collision state with new random expressions and rerun")
#         print("4) Exit")
#         choice = input("Enter your choice (1/2/3/4): ").strip()

#         if choice == "1":
#             run_id += 1
#             config_path = f"auto_followup_config_{run_id}.json"

#             # Start from the last state's expressions in a file
#             next_config = {
#                 "total_collisions": config.get("total_collisions", 50),
#                 "polling_frequency": config.get("polling_frequency", 10),
#                 "input_expressions": {
#                     "generator": "from_file",
#                     "params": {
#                         "filename": txt_file
#                     }
#                 },
#                 "measurements": config.get("measurements", [
#                     "entropy", "unique_expressions", "len_unique_expressions"
#                 ])
#             }

#             # Prompt for overrides
#             next_config = prompt_for_config_overrides(next_config)

#             with open(config_path, "w") as f:
#                 json.dump(next_config, f, indent=4)

#             print(f"\n🧪 New follow-up config created: {config_path}")

#         elif choice == "2":
#             new_path = input("Enter the new config filename (e.g. new_experiment.json): ").strip()
#             if not os.path.exists(new_path):
#                 print(f"❌ File '{new_path}' not found. Exiting.")
#                 break

#             # Let the user override fields from the new config
#             file_config = read_config_from_json(new_path)
#             updated_config = prompt_for_config_overrides(file_config)

#             # Save updated config to a new file
#             run_id = 1  # Reset counter for new chain
#             config_path = f"auto_followup_config_{run_id}.json"
#             with open(config_path, "w") as f:
#                 json.dump(updated_config, f, indent=4)
#             print(f"\n🧪 Overridden config saved as: {config_path}")

#         elif choice == "3":
#             collision_time_str = input("Enter the collision time to use (e.g. 50): ").strip()
#             collision_key = f"collision_{collision_time_str}"

#             collisions_data = experiment_results.get("collisions_data", {})
#             if collision_key not in collisions_data:
#                 print(f"❌ No data found for '{collision_key}'. Please try another time.")
#                 continue

#             collision_expressions = collisions_data[collision_key]["state"]

#             soup = alchemy.PySoup()
#             soup.perturb(collision_expressions)

#             p_str = input("How many new random expressions to add? ").strip()
#             max_depth_str = input("Max depth for the random expressions? ").strip()
#             try:
#                 p = int(p_str)
#                 max_depth = int(max_depth_str)
#             except ValueError:
#                 print("❌ Invalid numeric input. Returning to menu.")
#                 continue

#             soup.generate_random_expressions(p, max_depth)

#             rerun_collisions_str = input("How many collisions to simulate after perturbation? ").strip()
#             try:
#                 rerun_collisions = int(rerun_collisions_str)
#             except ValueError:
#                 print("❌ Invalid numeric input. Returning to menu.")
#                 continue

#             perturbed_results = {
#                 "info": {
#                     "original_experiment_file": output_file,
#                     "collision_time_used": collision_time_str,
#                     "extra_random_expressions": p,
#                     "random_expr_max_depth": max_depth,
#                     "collisions_after_perturb": rerun_collisions
#                 },
#                 "collisions_data": {}
#             }

#             for step in range(1, rerun_collisions + 1):
#                 soup.simulate_for(1, log=False)
#                 step_data = {}
#                 step_data["state"] = soup.expressions()
#                 step_data["entropy"] = soup.population_entropy()
#                 step_data["unique_expressions"] = soup.unique_expressions()
#                 step_data["len_unique_expressions"] = len(soup.unique_expressions())
#                 perturbed_results["collisions_data"][f"collision_{step}"] = step_data

#             run_id += 1
#             perturbed_file = f"perturbed_run_{run_id}.json"
#             with open(perturbed_file, "w") as pf:
#                 json.dump(perturbed_results, pf, indent=4)

#             print(f"\n✅ Perturbed run results saved to: {perturbed_file}")

#             # ----------------------------------------------------------------
#             # Fixing the issue: we do NOT automatically do a new experiment.
#             # Instead, just ask user if they want to continue or break.
#             # (If you always want to exit, do 'break' instead of 'continue'.)
#             # ----------------------------------------------------------------

#             # Ask if user wants to continue in the loop or exit now
#             again = input("\nPerturbation complete. Return to main menu? (y/n): ").strip().lower()
#             if again != "y":
#                 print("👋 Exiting after perturbation.")
#                 break
#             else:
#                 print("Returning to main menu...")
#                 continue

#         else:
#             print("👋 Exiting experiment loop.")
#             break

# if __name__ == "__main__":
#     main()


# import json
# import os
# import sys
# import alchemy

# def read_config_from_json(json_path: str) -> dict:
#     """Read the experiment configuration from a JSON file."""
#     if not os.path.isfile(json_path):
#         raise FileNotFoundError(f"Could not find the config file: {json_path}")

#     with open(json_path, "r") as f:
#         config = json.load(f)
#     return config

# def load_btree_expressions(params: dict) -> list:
#     """
#     Create a BTree generator from the given params and generate expressions.
#     """
#     size = params.get("size", 5)
#     fvp = params.get("freevar_generation_probability", 0.5)
#     max_fv = params.get("max_free_vars", 3)
#     std_type = params.get("standardization", "prefix")
#     seed_value = params.get("seed", 0)
#     num_expr = params.get("num_expressions", 1000)

#     btree_gen = alchemy.PyBTreeGen.from_config(
#         size,
#         fvp,
#         max_fv,
#         alchemy.PyStandardization(std_type)
#     )
#     expressions = btree_gen.generate_n(num_expr)
#     return expressions

# def load_input_expressions(generator_type: str, gen_params: dict) -> list:
#     """
#     Depending on the generator type, load or generate expressions.
#     """
#     if generator_type == "from_file":
#         filename = gen_params.get("filename", "test_exprs.txt")

#         if not os.path.isfile(filename):
#             raise FileNotFoundError(f"Could not find file: {filename}")

#         if filename.endswith(".json"):
#             # Reading from a previous experiment's output JSON
#             with open(filename, "r") as f:
#                 data = json.load(f)
#             collisions_data = data.get("collisions_data", {})
#             if not collisions_data:
#                 raise ValueError(f"No collisions_data found in JSON: {filename}")

#             all_keys = sorted(collisions_data.keys(), key=lambda x: int(x.split("_")[-1]))
#             last_key = all_keys[-1]
#             last_step = collisions_data[last_key]
#             new_expressions = last_step.get("state", [])
#             return new_expressions
#         else:
#             # If it's just a text file
#             with open(filename, "r") as f:
#                 return [line.strip() for line in f if line.strip()]

#     elif generator_type == "BTree":
#         return load_btree_expressions(gen_params)

#     else:
#         raise ValueError(f"Unsupported generator type: {generator_type}")

# def single_experiment(config: dict) -> dict:
#     """
#     Runs the experiment using the provided config.
#     Returns a dict with collisions_data, last_state, etc.
#     """
#     generator_type = config["input_expressions"]["generator"]
#     gen_params = config["input_expressions"].get("params", {})
#     measurements = config.get("measurements", [])
#     if not measurements:
#         measurements = ["entropy", "unique_expressions", "len_unique_expressions"]

#     soup = alchemy.PySoup()
#     expressions = load_input_expressions(generator_type, gen_params)

#     if generator_type == "BTree":
#         print(f"\nGenerated {len(expressions)} expressions from BTree:\n")
#         for expr in expressions:
#             print("  ", expr)

#     soup.perturb(expressions)

#     total_collisions = config.get("total_collisions", 1000)
#     polling_frequency = config.get("polling_frequency", 10)

#     results_data = {}
#     collision_count = 0
#     while collision_count < total_collisions:
#         soup.simulate_for(1, log=False)
#         collision_count += 1

#         if (collision_count % polling_frequency == 0) or (collision_count == total_collisions):
#             coll_key = f"collision_{collision_count}"
#             step_data = {"state": soup.expressions()}
#             if "entropy" in measurements:
#                 step_data["entropy"] = soup.population_entropy()
#             if "unique_expressions" in measurements:
#                 step_data["unique_expressions"] = soup.unique_expressions()
#             if "len_unique_expressions" in measurements:
#                 step_data["len_unique_expressions"] = len(soup.unique_expressions())

#             results_data[coll_key] = step_data

#     # Find the final collision
#     last_collision_key = sorted(results_data.keys(), key=lambda x: int(x.split("_")[-1]))[-1]
#     last_collision = results_data[last_collision_key]

#     return {
#         "config": config,
#         "collisions_data": results_data,
#         "last_state": {
#             last_collision_key: last_collision
#         }
#     }

# def main():
#     """
#     High-level manager:
#       1) Ask user for experiment name, create folder
#       2) Ask user for path to a JSON config in the specified format
#       3) Run the experiment, then show menu (continue from last state, new config, perturb, exit)
#     """
#     # 1) Ask user for experiment name
#     exp_name = input("Enter name for this experiment: ").strip()
#     if not exp_name:
#         exp_name = "default_experiment"
#     if not os.path.exists(exp_name):
#         os.makedirs(exp_name)
#         print(f"Created folder: {exp_name}")

#     # 2) Ask for config path
#     config_path = input("\nEnter path to a JSON config (e.g. my_config.json): ").strip()
#     if not os.path.isfile(config_path):
#         print(f"❌ File '{config_path}' not found. Exiting.")
#         return

#     # read the config
#     config = read_config_from_json(config_path)

#     run_id = 1
#     while True:
#         # --- Run experiment ---
#         print(f"\n--- Running Experiment #{run_id} in folder '{exp_name}' ---")
#         experiment_results = single_experiment(config)

#         # Save results to folder
#         output_file = os.path.join(exp_name, f"experiment_output_{run_id}.json")
#         with open(output_file, "w") as f:
#             json.dump(experiment_results, f, indent=4)
#         print(f"\n✅ Experiment results saved to: {output_file}")

#         # Save last state expressions to a text file
#         last_state = experiment_results.get("last_state")
#         if last_state:
#             last_key = list(last_state.keys())[0]
#             final_exprs = last_state[last_key].get("state", [])
#             txt_file = os.path.join(exp_name, f"last_state_exprs_{run_id}.txt")
#             with open(txt_file, "w") as f:
#                 for expr in final_exprs:
#                     f.write(expr + "\n")
#             print(f"✅ Final state expressions saved to: {txt_file}")
#         else:
#             print("⚠️  No last state found — cannot continue from this run.")
#             break

#         print("\nWhat would you like to do next?")
#         print("1) Continue experiment from last state")
#         print("2) Start a new experiment with a different config (still in folder)")
#         print("3) Perturb a prior collision state with new random expressions and rerun")
#         print("4) Exit")
#         choice = input("Enter your choice (1/2/3/4): ").strip()

#         if choice == "1":
#             # Continue from last state => same config except we force from_file
#             run_id += 1
#             config["input_expressions"] = {
#                 "generator": "from_file",
#                 "params": {
#                     "filename": txt_file  # path to last state's expressions
#                 }
#             }
#             # keep measurements, collisions, etc. from old config
#             print("\nContinuing from last state...")

#         elif choice == "2":
#             # Start new experiment => ask user for a new config file
#             new_cfg_path = input("Enter path to new config JSON: ").strip()
#             if not os.path.isfile(new_cfg_path):
#                 print(f"❌ File '{new_cfg_path}' not found. Returning to menu.")
#                 continue
#             config = read_config_from_json(new_cfg_path)
#             run_id = 1  # reset run id if you want a fresh chain in the same folder
#             print("\n🔄 Switched to new config. Next run will be #1 in the same folder.")

#         elif choice == "3":
#             collision_time_str = input("Enter the collision time to use (e.g. 50): ").strip()
#             collision_key = f"collision_{collision_time_str}"

#             collisions_data = experiment_results.get("collisions_data", {})
#             if collision_key not in collisions_data:
#                 print(f"❌ No data found for '{collision_key}'. Please try another time.")
#                 continue

#             # Grab old expressions
#             collision_expressions = collisions_data[collision_key]["state"]

#             # Create a new soup, load them in
#             soup = alchemy.PySoup()
#             soup.perturb(collision_expressions)

#             p_str = input("How many new random expressions to add? ").strip()
#             max_depth_str = input("Max depth for the random expressions? ").strip()
#             try:
#                 p = int(p_str)
#                 max_depth = int(max_depth_str)
#             except ValueError:
#                 print("❌ Invalid numeric input. Returning to menu.")
#                 continue

#             soup.generate_random_expressions(p, max_depth)

#             rerun_collisions_str = input("How many collisions to simulate after perturbation? ").strip()
#             try:
#                 rerun_collisions = int(rerun_collisions_str)
#             except ValueError:
#                 print("❌ Invalid numeric input. Returning to menu.")
#                 continue

#             # We'll store these results in a new JSON
#             run_id += 1
#             perturbed_data = {
#                 "info": {
#                     "original_experiment_file": output_file,
#                     "collision_time_used": collision_time_str,
#                     "extra_random_expressions": p,
#                     "random_expr_max_depth": max_depth,
#                     "collisions_after_perturb": rerun_collisions
#                 },
#                 "collisions_data": {}
#             }
#             for step in range(1, rerun_collisions + 1):
#                 soup.simulate_for(1, log=False)
#                 step_data = {
#                     "state": soup.expressions(),
#                     "entropy": soup.population_entropy(),
#                     "unique_expressions": soup.unique_expressions(),
#                     "len_unique_expressions": len(soup.unique_expressions())
#                 }
#                 perturbed_data["collisions_data"][f"collision_{step}"] = step_data

#             perturbed_file = os.path.join(exp_name, f"perturbed_run_{run_id}.json")
#             with open(perturbed_file, "w") as pf:
#                 json.dump(perturbed_data, pf, indent=4)
#             print(f"\n✅ Perturbed run results saved to: {perturbed_file}")

#         else:
#             print("👋 Exiting experiment loop.")
#             break

# if __name__ == "__main__":
#     main()

# import os
# import json
# import alchemy

# def find_experiment_folders() -> list:
#     """
#     Return a list of existing experiment folders in the current directory.
#     We'll define an 'experiment folder' as any directory that's not hidden.
#     """
#     all_items = os.listdir(".")
#     # Filter to directories that aren't hidden
#     dirs = [d for d in all_items if os.path.isdir(d) and not d.startswith(".")]
#     return dirs

# def pick_experiment_folder() -> str:
#     """
#     Lists existing experiment folders, asks user to pick or create a new one.
#     Returns the chosen folder name, or an empty string if user chooses to exit.
#     """
#     while True:
#         folders = find_experiment_folders()
#         print("\nExisting experiment folders:")
#         if not folders:
#             print("  [None found]")
#         else:
#             for i, folder in enumerate(folders, start=1):
#                 print(f"  {i}) {folder}")
#         print("  n) Create a new experiment folder")
#         print("  x) Exit script entirely")
#         choice = input("\nChoose a folder #, 'n' for new, or 'x' to exit: ").strip().lower()

#         if choice == "x":
#             return ""  # means user wants to exit the script

#         elif choice == "n":
#             new_name = input("Enter name for your new experiment folder: ").strip()
#             return new_name

#         else:
#             # Try to interpret choice as an integer
#             try:
#                 index = int(choice)
#                 if 1 <= index <= len(folders):
#                     return folders[index - 1]
#             except ValueError:
#                 pass

#             # If invalid
#             print("Invalid selection. Please try again.")

# def read_config_from_json(json_path: str) -> dict:
#     if not os.path.isfile(json_path):
#         raise FileNotFoundError(f"Could not find the config file: {json_path}")
#     with open(json_path, "r") as f:
#         return json.load(f)

# def load_btree_expressions(params: dict) -> list:
#     size = params.get("size", 5)
#     fvp = params.get("freevar_generation_probability", 0.5)
#     max_fv = params.get("max_free_vars", 3)
#     std_type = params.get("standardization", "prefix")
#     num_expr = params.get("num_expressions", 10)

#     btree_gen = alchemy.PyBTreeGen.from_config(
#         size,
#         fvp,
#         max_fv,
#         alchemy.PyStandardization(std_type)
#     )
#     expressions = btree_gen.generate_n(num_expr)
#     return expressions

# def load_input_expressions(generator_type: str, gen_params: dict) -> list:
#     if generator_type == "from_file":
#         filename = gen_params.get("filename", "test_exprs.txt")
#         if not os.path.isfile(filename):
#             raise FileNotFoundError(f"Could not find file: {filename}")

#         if filename.endswith(".json"):
#             with open(filename, "r") as f:
#                 data = json.load(f)
#             collisions_data = data.get("collisions_data", {})
#             if not collisions_data:
#                 raise ValueError(f"No collisions_data found in JSON: {filename}")
#             all_keys = sorted(collisions_data.keys(), key=lambda x: int(x.split("_")[-1]))
#             last_key = all_keys[-1]
#             last_step = collisions_data[last_key]
#             new_expressions = last_step.get("state", [])
#             return new_expressions
#         else:
#             with open(filename, "r") as f:
#                 return [line.strip() for line in f if line.strip()]

#     elif generator_type == "BTree":
#         return load_btree_expressions(gen_params)

#     else:
#         raise ValueError(f"Unsupported generator type: {generator_type}")

# def single_experiment(config: dict) -> dict:
#     generator_type = config["input_expressions"]["generator"]
#     gen_params = config["input_expressions"].get("params", {})
#     measurements = config.get("measurements", [])
#     if not measurements:
#         measurements = ["entropy", "unique_expressions", "len_unique_expressions"]

#     soup = alchemy.PySoup()
#     expressions = load_input_expressions(generator_type, gen_params)
#     if generator_type == "BTree":
#         print(f"\nGenerated {len(expressions)} expressions from BTree:\n")
#         for expr in expressions:
#             print("   ", expr)

#     soup.perturb(expressions)

#     total_collisions = config.get("total_collisions", 1000)
#     polling_frequency = config.get("polling_frequency", 10)

#     results_data = {}
#     collision_count = 0
#     while collision_count < total_collisions:
#         soup.simulate_for(1, log=False)
#         collision_count += 1

#         if (collision_count % polling_frequency == 0) or (collision_count == total_collisions):
#             coll_key = f"collision_{collision_count}"
#             step_data = {"state": soup.expressions()}
#             if "entropy" in measurements:
#                 step_data["entropy"] = soup.population_entropy()
#             if "unique_expressions" in measurements:
#                 step_data["unique_expressions"] = soup.unique_expressions()
#             if "len_unique_expressions" in measurements:
#                 step_data["len_unique_expressions"] = len(soup.unique_expressions())

#             results_data[coll_key] = step_data

#     last_collision_key = sorted(results_data.keys(), key=lambda x: int(x.split("_")[-1]))[-1]
#     last_collision = results_data[last_collision_key]

#     return {
#         "config": config,
#         "collisions_data": results_data,
#         "last_state": {
#             last_collision_key: last_collision
#         }
#     }

# def do_experiment_loop(exp_folder: str):
#     """
#     A loop that:
#       - asks user for a config path
#       - runs single_experiment
#       - gives main menu (1/2/3/4)
#       - returns to caller if user picks "4) Exit"
#     """
#     # Prompt for config
#     while True:
#         config_path = input(f"\n[{exp_folder}] Enter path to a JSON config (or 'x' to stop): ").strip()
#         if config_path.lower() == "x":
#             print("Returning to folder selection.")
#             return

#         if not os.path.isfile(config_path):
#             print(f"❌ File '{config_path}' not found. Please try again.")
#             continue

#         break  # we have a valid config_path

#     config = read_config_from_json(config_path)
#     run_id = 1

#     while True:
#         print(f"\n--- Running Experiment #{run_id} in folder '{exp_folder}' ---")
#         experiment_results = single_experiment(config)

#         # Save results
#         output_file = os.path.join(exp_folder, f"experiment_output_{run_id}.json")
#         with open(output_file, "w") as f:
#             json.dump(experiment_results, f, indent=4)
#         print(f"\n✅ Experiment results saved to: {output_file}")

#         last_state = experiment_results.get("last_state")
#         if last_state:
#             last_key = list(last_state.keys())[0]
#             final_exprs = last_state[last_key].get("state", [])
#             txt_file = os.path.join(exp_folder, f"last_state_exprs_{run_id}.txt")
#             with open(txt_file, "w") as f:
#                 for expr in final_exprs:
#                     f.write(expr + "\n")
#             print(f"✅ Final state expressions saved to: {txt_file}")
#         else:
#             print("⚠️  No last state found — cannot continue from this run.")
#             break

#         print("\nWhat would you like to do next?")
#         print("1) Continue experiment from last state")
#         print("2) Start a new experiment with a different config (still in folder)")
#         print("3) Perturb a prior collision state with new random expressions and rerun")
#         print("4) Exit to folder selection")
#         choice = input("Enter your choice (1/2/3/4): ").strip()

#         if choice == "1":
#             run_id += 1
#             # Force from_file
#             config["input_expressions"] = {
#                 "generator": "from_file",
#                 "params": {
#                     "filename": txt_file
#                 }
#             }
#             print("\nContinuing from last state...")

#         elif choice == "2":
#             new_cfg_path = input("Enter path to new config JSON: ").strip()
#             if not os.path.isfile(new_cfg_path):
#                 print(f"❌ File '{new_cfg_path}' not found. Returning to menu.")
#                 continue
#             config = read_config_from_json(new_cfg_path)
#             run_id = 1
#             print("\n🔄 Loaded new config. Next run will be #1 in the same folder.")

#         elif choice == "3":
#             collision_time_str = input("Enter the collision time to use (e.g. 50): ").strip()
#             collision_key = f"collision_{collision_time_str}"
#             collisions_data = experiment_results.get("collisions_data", {})
#             if collision_key not in collisions_data:
#                 print(f"❌ No data found for '{collision_key}'. Please try another time.")
#                 continue

#             collision_expressions = collisions_data[collision_key]["state"]

#             soup = alchemy.PySoup()
#             soup.perturb(collision_expressions)

#             p_str = input("How many new random expressions to add? ").strip()
#             max_depth_str = input("Max depth for the random expressions? ").strip()
#             try:
#                 p = int(p_str)
#                 max_depth = int(max_depth_str)
#             except ValueError:
#                 print("❌ Invalid numeric input. Returning to menu.")
#                 continue

#             soup.generate_random_expressions(p, max_depth)

#             rerun_collisions_str = input("How many collisions to simulate after perturbation? ").strip()
#             try:
#                 rerun_collisions = int(rerun_collisions_str)
#             except ValueError:
#                 print("❌ Invalid numeric input. Returning to menu.")
#                 continue

#             # We'll store these results in a separate JSON
#             run_id += 1
#             perturbed_data = {
#                 "info": {
#                     "original_experiment_file": output_file,
#                     "collision_time_used": collision_time_str,
#                     "extra_random_expressions": p,
#                     "random_expr_max_depth": max_depth,
#                     "collisions_after_perturb": rerun_collisions
#                 },
#                 "collisions_data": {}
#             }
#             for step in range(1, rerun_collisions + 1):
#                 soup.simulate_for(1, log=False)
#                 step_data = {
#                     "state": soup.expressions(),
#                     "entropy": soup.population_entropy(),
#                     "unique_expressions": soup.unique_expressions(),
#                     "len_unique_expressions": len(soup.unique_expressions())
#                 }
#                 perturbed_data["collisions_data"][f"collision_{step}"] = step_data

#             perturbed_file = os.path.join(exp_folder, f"perturbed_run_{run_id}.json")
#             with open(perturbed_file, "w") as pf:
#                 json.dump(perturbed_data, pf, indent=4)
#             print(f"\n✅ Perturbed run results saved to: {perturbed_file}")

#             # After the perturbation, just go back to the main menu loop again
#             print("Returning to main menu...")

#         else:
#             print(f"\nExiting experiment loop for folder '{exp_folder}'...")
#             # break out of the while True, so we go back to folder selection
#             break

# def main():
#     """
#     1) Folder selection loop
#     2) For chosen folder, run do_experiment_loop
#     3) Return to folder selection on exit
#     """
#     print("=== Welcome to the AlChemy Experiment Manager ===")

#     while True:
#         folder = pick_experiment_folder()
#         if not folder:
#             # means user typed 'x' or something that indicated exit
#             print("No folder selected. Exiting script.")
#             break

#         # Ensure the folder exists
#         if not os.path.exists(folder):
#             os.makedirs(folder)
#             print(f"Created folder: {folder}")

#         # Now handle experiments in that folder
#         do_experiment_loop(folder)

#         # After do_experiment_loop returns, we ask if user wants to pick another folder or exit
#         again = input("\nPick another folder? (y/n): ").strip().lower()
#         if again != "y":
#             print("Goodbye!")
#             break

# if __name__ == "__main__":
#     main()
import os
import json
import alchemy

def find_experiment_folders() -> list:
    """
    Return a list of existing experiment folders in the current directory.
    We'll define an 'experiment folder' as any directory that's not hidden.
    """
    all_items = os.listdir(".")
    # Filter to directories that aren't hidden
    dirs = [d for d in all_items if os.path.isdir(d) and not d.startswith(".")]
    return dirs

def pick_experiment_folder() -> str:
    """
    Lists existing experiment folders, asks user to pick or create a new one.
    Returns the chosen folder name, or an empty string if user chooses to exit.
    """
    while True:
        folders = find_experiment_folders()
        print("\nExisting experiment folders:")
        if not folders:
            print("  [None found]")
        else:
            for i, folder in enumerate(folders, start=1):
                print(f"  {i}) {folder}")
        print("  n) Create a new experiment folder")
        print("  x) Exit script entirely")
        choice = input("\nChoose a folder #, 'n' for new, or 'x' to exit: ").strip().lower()

        if choice == "x":
            return ""  # means user wants to exit the script
        elif choice == "n":
            new_name = input("Enter name for your new experiment folder: ").strip()
            return new_name
        else:
            try:
                index = int(choice)
                if 1 <= index <= len(folders):
                    return folders[index - 1]
            except ValueError:
                pass
            print("Invalid selection. Please try again.")

def read_config_from_json(json_path: str) -> dict:
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"Could not find the config file: {json_path}")
    with open(json_path, "r") as f:
        return json.load(f)

def load_btree_expressions(params: dict) -> list:
    size = params.get("size", 5)
    fvp = params.get("freevar_generation_probability", 0.5)
    max_fv = params.get("max_free_vars", 3)
    std_type = params.get("standardization", "prefix")
    num_expr = params.get("num_expressions", 10)

    btree_gen = alchemy.PyBTreeGen.from_config(
        size,
        fvp,
        max_fv,
        alchemy.PyStandardization(std_type)
    )
    expressions = btree_gen.generate_n(num_expr)
    return expressions

def load_input_expressions(generator_type: str, gen_params: dict) -> list:
    if generator_type == "from_file":
        filename = gen_params.get("filename", "test_exprs.txt")
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Could not find file: {filename}")
        if filename.endswith(".json"):
            with open(filename, "r") as f:
                data = json.load(f)
            collisions_data = data.get("collisions_data", {})
            if not collisions_data:
                raise ValueError(f"No collisions_data found in JSON: {filename}")
            all_keys = sorted(collisions_data.keys(), key=lambda x: int(x.split("_")[-1]))
            last_key = all_keys[-1]
            last_step = collisions_data[last_key]
            new_expressions = last_step.get("state", [])
            return new_expressions
        else:
            with open(filename, "r") as f:
                return [line.strip() for line in f if line.strip()]
    elif generator_type == "BTree":
        return load_btree_expressions(gen_params)
    else:
        raise ValueError(f"Unsupported generator type: {generator_type}")

def single_experiment(config: dict) -> dict:
    generator_type = config["input_expressions"]["generator"]
    gen_params = config["input_expressions"].get("params", {})
    measurements = config.get("measurements", [])
    if not measurements:
        measurements = ["entropy", "unique_expressions", "len_unique_expressions"]

    soup = alchemy.PySoup()
    expressions = load_input_expressions(generator_type, gen_params)
    if generator_type == "BTree":
        print(f"\nGenerated {len(expressions)} expressions from BTree:\n")
        for expr in expressions:
            print("   ", expr)

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
            step_data = {"state": soup.expressions()}
            if "entropy" in measurements:
                step_data["entropy"] = soup.population_entropy()
            if "unique_expressions" in measurements:
                step_data["unique_expressions"] = soup.unique_expressions()
            if "len_unique_expressions" in measurements:
                step_data["len_unique_expressions"] = len(soup.unique_expressions())
            results_data[coll_key] = step_data
    last_collision_key = sorted(results_data.keys(), key=lambda x: int(x.split("_")[-1]))[-1]
    last_collision = results_data[last_collision_key]
    return {
        "config": config,
        "collisions_data": results_data,
        "last_state": {last_collision_key: last_collision}
    }

# --------------------------------------------------------------------
# CLEAR EXPERIMENT OUTPUTS: Remove specific JSON and TXT files in the folder.
# --------------------------------------------------------------------
def clear_experiment_outputs_in_folder(folder: str):
    """
    Remove any 'experiment_output_*.json', 'perturbed_run_*.json', and any '.txt' files
    in the specified folder.
    """
    import glob
    patterns = [
        os.path.join(folder, "experiment_output_*.json"),
        os.path.join(folder, "perturbed_run_*.json"),
        os.path.join(folder, "*.txt")
    ]
    for pattern in patterns:
        files_to_remove = glob.glob(pattern)
        for f in files_to_remove:
            try:
                os.remove(f)
                print(f"  Deleted: {f}")
            except OSError as e:
                print(f"  Could not delete {f}: {e}")

# --------------------------------------------------------------------
# GATHER ALL COLLISIONS FROM ALL JSON IN A FOLDER
# --------------------------------------------------------------------
def gather_all_collisions_in_folder(folder: str) -> list:
    """
    Scan all *.json files in 'folder'.
    For each file, load the 'collisions_data' if present.
    Return a list of tuples: [(filename, collision_key, collision_dict), ...].
    """
    import glob
    results = []
    json_files = glob.glob(os.path.join(folder, "*.json"))
    for jf in json_files:
        try:
            with open(jf, "r") as f:
                data = json.load(f)
            collisions_data = data.get("collisions_data", {})
            for ck, cdict in collisions_data.items():
                results.append((jf, ck, cdict))
        except Exception:
            pass
    return results

def pick_any_collision_in_folder(folder: str):
    """
    Collect all collisions from all .json in 'folder'.
    Let user pick which (file + collision key) to use.
    Return (filename, collision_key, collision_dict) or None.
    """
    all_colls = gather_all_collisions_in_folder(folder)
    if not all_colls:
        print("No collisions found in this folder.")
        return None
    def coll_sort_key(item):
        fname, ck, _ = item
        num_str = ck.split("_")[-1]
        return (fname, int(num_str))
    all_colls.sort(key=coll_sort_key)
    print("\n--- Collisions from all JSON in folder ---")
    for i, (fname, ck, cdict) in enumerate(all_colls, start=1):
        print(f"{i}) {os.path.basename(fname)} -> {ck}")
    choice = input("Pick a collision # or leave blank to cancel: ").strip()
    if not choice:
        return None
    try:
        idx = int(choice)
        if 1 <= idx <= len(all_colls):
            return all_colls[idx - 1]
    except ValueError:
        pass
    print("Invalid choice. Canceling.")
    return None

# --------------------------------------------------------------------
# MAIN EXPERIMENT LOOP
# --------------------------------------------------------------------
def do_experiment_loop(exp_folder: str):
    """
    A loop that:
      - asks user for a config path
      - runs single_experiment
      - gives main menu (1/2/3/4)
      - returns to caller if user picks "4) Exit"
    """
    while True:
        config_path = input(f"\n[{exp_folder}] Enter path to a JSON config (or 'x' to stop): ").strip()
        if config_path.lower() == "x":
            print("Returning to folder selection.")
            return
        if not os.path.isfile(config_path):
            print(f"❌ File '{config_path}' not found. Please try again.")
            continue
        break

    config = read_config_from_json(config_path)
    run_id = 1

    while True:
        print(f"\n--- Running Experiment #{run_id} in folder '{exp_folder}' ---")
        experiment_results = single_experiment(config)
        output_file = os.path.join(exp_folder, f"experiment_output_{run_id}.json")
        with open(output_file, "w") as f:
            json.dump(experiment_results, f, indent=4)
        print(f"\n✅ Experiment results saved to: {output_file}")

        last_state = experiment_results.get("last_state")
        if last_state:
            last_key = list(last_state.keys())[0]
            final_exprs = last_state[last_key].get("state", [])
            txt_file = os.path.join(exp_folder, f"last_state_exprs_{run_id}.txt")
            with open(txt_file, "w") as f:
                for expr in final_exprs:
                    f.write(expr + "\n")
            print(f"✅ Final state expressions saved to: {txt_file}")
        else:
            print("⚠️  No last state found — cannot continue from this run.")
            break

        print("\nWhat would you like to do next?")
        print("1) Continue experiment from last state")
        print("2) Start a new experiment with a different config (still in folder)")
        print("3) Perturb a prior collision state with new random expressions and rerun")
        print("4) Exit to folder selection")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            run_id += 1
            config["input_expressions"] = {
                "generator": "from_file",
                "params": {"filename": txt_file}
            }
            print("\nContinuing from last state...")

        elif choice == "2":
            clear_experiment_outputs_in_folder(exp_folder)
            new_cfg_path = input("Enter path to new config JSON: ").strip()
            if not os.path.isfile(new_cfg_path):
                print(f"❌ File '{new_cfg_path}' not found. Returning to menu.")
                continue
            config = read_config_from_json(new_cfg_path)
            run_id = 1
            print("\n🔄 Cleared old experiment outputs. Loaded new config. Next run will be #1 in the same folder.")

        elif choice == "3":
            collision_info = pick_any_collision_in_folder(exp_folder)
            if not collision_info:
                print("No collision chosen. Returning to menu.")
                continue
            filename_used, collision_key, collision_dict = collision_info
            collision_expressions = collision_dict.get("state", [])
            soup = alchemy.PySoup()
            soup.perturb(collision_expressions)
            p_str = input("How many new random expressions to add? ").strip()
            max_depth_str = input("Max depth for the random expressions? ").strip()
            try:
                p = int(p_str)
                max_depth = int(max_depth_str)
            except ValueError:
                print("❌ Invalid numeric input. Returning to menu.")
                continue
            soup.generate_random_expressions(p, max_depth)
            rerun_collisions_str = input("How many collisions to simulate after perturbation? ").strip()
            try:
                rerun_collisions = int(rerun_collisions_str)
            except ValueError:
                print("❌ Invalid numeric input. Returning to menu.")
                continue
            run_id += 1
            perturbed_data = {
                "info": {
                    "original_experiment_file": filename_used,
                    "collision_time_used": collision_key,
                    "extra_random_expressions": p,
                    "random_expr_max_depth": max_depth,
                    "collisions_after_perturb": rerun_collisions
                },
                "collisions_data": {}
            }
            for step in range(1, rerun_collisions + 1):
                soup.simulate_for(1, log=False)
                step_data = {
                    "state": soup.expressions(),
                    "entropy": soup.population_entropy(),
                    "unique_expressions": soup.unique_expressions(),
                    "len_unique_expressions": len(soup.unique_expressions())
                }
                perturbed_data["collisions_data"][f"collision_{step}"] = step_data
            perturbed_file = os.path.join(exp_folder, f"perturbed_run_{run_id}.json")
            with open(perturbed_file, "w") as pf:
                json.dump(perturbed_data, pf, indent=4)
            print(f"\n✅ Perturbed run results saved to: {perturbed_file}")
            print("\nNo further run desired after perturbation. Exiting to folder selection.")
            break

        else:
            print(f"\nExiting experiment loop for folder '{exp_folder}'...")
            break

def main():
    """
    1) Folder selection loop
    2) For chosen folder, run do_experiment_loop
    3) Return to folder selection on exit
    """
    print("=== Welcome to the AlChemy Experiment Manager ===")
    while True:
        folder = pick_experiment_folder()
        if not folder:
            print("No folder selected. Exiting script.")
            break
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")
        do_experiment_loop(folder)
        again = input("\nPick another folder? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()



