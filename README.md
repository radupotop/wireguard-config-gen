# Wireguard config generator

Written in Python.

Requirements:

* cryptography
* pydantic
* pyyaml

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
