import argparse

from wgconf.parseyamlconfig import (
    initial_parse_yaml_config,
    merge_yaml,
    populate_yaml_config,
)


def runall():
    """
    Parse args and run the entire script.
    """
    parser = argparse.ArgumentParser(description='Process template YAML files')
    parser.add_argument(
        'yaml_files',
        type=argparse.FileType(mode='r', encoding='UTF-8'),  # read in Text Mode
        nargs='+',
        help='Template YAML files',
    )

    args = parser.parse_args()
    yaml_contents = merge_yaml(args.yaml_files)
    yamlcfg = initial_parse_yaml_config(yaml_contents)
    populate_yaml_config(yamlcfg)
