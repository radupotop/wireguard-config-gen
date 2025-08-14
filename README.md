# Wireguard config generator

A `wg-quick` Wireguard config generator written in Python.

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

## Strip Config

In order to obtain a config file ready to be used directly by `wg`
(rather than through the `wg-quick` script), the following command can be used:

    wg syncconf wg0 <(exec wg-quick strip wg0)

This removes the Address and DNS from the Interface section.

### Multiple subnets

Multiple configurations can be managed in parallel, serving different sets of clients,
living on different subnets.

Edit your YAML configuration and set `Outdir: subnet2/`

    python run.py subnet2.yaml  # will write to subnet2/

Then update with:

    python run.py subnet2.yaml subnet2/result.yaml

### Passive Servers

Servers can be configured as passive with the `IsPassive: true` directive 
placed directly under the machine name in `interfaces.yaml`.

A passive server relies on its clients to initiate a connection, rather than reaching out.
Its peers section will have no configured endpoints initially, they will only get populated by the server after the peers initiate the connection.

This has a few main advantages: i.e. not having to rely on resolving the endpoint
hostnames when `wg-quick` starts up, or the server not initiating any connection at all,
i.e. being completely silent.
