# Wireguard config generator

Written in Python.

Requirements:

* cryptography
* pydantic
* pyyaml

## Installation

    uv venv --seed
    uv sync
    uv run python run.py ...

Or source the venv and run directly with:

    source .venv/bin/activate
    python run.py ...

## Usage

### First run

    python run.py interfaces.yaml
  
This will create the `output/result.yaml` template file with the initial network 
configuration, and the individual `.conf` files for each machine.
  
### Subsequent runs

    python run.py interfaces.yaml output/result.yaml

This will merge both the `interfaces.yaml` and the `output/result.yaml` template files
into the final `output/result.yaml`.  
This is used to update an existing network configuration.

### Multiple subnets

Multiple configurations can be managed in parallel, serving different sets of clients,
living on different subnets.

Edit your YAML configuration and set `Outdir: subnet2/`

    python run.py subnet2.yaml  # will write to subnet2/

Then update with:

    python run.py subnet2.yaml subnet2/result.yaml
