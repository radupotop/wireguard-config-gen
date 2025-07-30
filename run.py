import argparse

from parseyamlconfig import merge_yaml, parse_yaml_config

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process template YAML files')
    parser.add_argument(
        'yaml_files',
        type=argparse.FileType(mode='r', encoding='UTF-8'),  # read in Text Mode
        nargs='+',
        help='Template YAML files',
    )

    args = parser.parse_args()
    yaml_contents = merge_yaml(args.yaml_files)
    parse_yaml_config(yaml_contents)
