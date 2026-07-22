import argparse

from utils import load_config
from workflow import execute_pipeline


def main():

    parser = argparse.ArgumentParser(
        description="Oxford Nanopore Variant Analysis Pipeline"
    )

    parser.add_argument(
        "--config",
        default="config/default.yaml",
        help="Path to YAML configuration file"
    )

    args = parser.parse_args()

    config = load_config(args.config)

    execute_pipeline(config)


if __name__ == "__main__":
    main()