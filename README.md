# To do list 3/28

## Cole
- Set up UV app
- debug the lambda unicode write issue
- modify Soup class so that perturb is correct

## Library
- Wait for update to perturb in the Soup class
- Write experiment outputs to sqlite (consider how to do it for inputs)

## Visualization
- Integrate the current library
- Read SQLite


# To do list 2/28

## Library
- Expose the total number of expressions as a parameter to specify in the generators
- Write the random number generator seed to the outputs json
- Read experiment configuration from json
- Write the length of the unique expressions list to the output (e.g. as another measurements)
- Modify "from_file" input to accept an output json, and read the state of the last collision as the input for a new experiment
- Add entropy and unique expressions as default outputs (in addition to the state)
- Remove Fontana Generator until Rust library supports it
- Document functionality that exists

## Visualization
- Check how the database is being generated, 0 unique expressions 0 entropy etc
- View state "Histogram" at a specified collision number. 
- Design new experiments tab - output to json 
- Think how to host this as a server: we want to enable users to locally, design experiments in the GUI, run the experiment, and then visualize those new results. 
- We want to log (and possibly hash) inputs + outputs + timestamps. 

# Rust Library README
A reimplementation of Walter Fontana's Alchemy. Pipe lambda expressions into 
`stdin` to start a default simulation. 

Usage:

`alchemy`

Build: 

`cargo build`

Testing:

`cargo run -- {args}`

With the binary tree generators from the 
[lambda-btree](https://github.com/AgentElement/lambda-btree) crate, you can
run a simple alchemy simulation with the following command.

`python /path/to/src/fontana_generator.py | cargo run -- {args}`


Documentation:

* Full documentation: `cargo doc --open`
* Help: `cargo run -- --help`

The documentation for the configuration file is in the `Config` object.
