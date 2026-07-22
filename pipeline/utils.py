import os
import sys
import json
import yaml
import subprocess


# =====================================================
# CONFIG
# =====================================================

def load_config(config_file):
    """Load YAML configuration."""

    with open(config_file, "r") as f:
        return yaml.safe_load(f)


# =====================================================
# COMMAND EXECUTION
# =====================================================

def run_command(cmd):
    """Run shell command."""

    print(f"\n[CMD]\n{cmd}\n")

    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:

        print(result.stderr)

        sys.exit(1)

    return result.stdout


# =====================================================
# FILE HELPERS
# =====================================================

def check_file(path, name):

    if not os.path.isfile(path):

        print(f"[ERROR] {name} not found")

        print(path)

        sys.exit(1)


def make_directory(path):

    os.makedirs(path, exist_ok=True)


def warning(message):

    print(f"[WARNING] {message}")


def info(message):

    print(f"[INFO] {message}")


# =====================================================
# JSON
# =====================================================

def read_json(json_file):

    with open(json_file, "r") as f:

        return json.load(f)


# =====================================================
# NANOSTATS PARSER
# =====================================================

def parse_nanostats(stats_file):

    """
    Reads NanoPlot NanoStats.txt

    Returns

    {
        "mean_quality":9.9,
        "mean_length":1292
    }
    """

    data = {}

    with open(stats_file) as f:

        for line in f:

            line = line.strip()

            if line.startswith("Mean read quality"):

                value = line.split(":")[1].strip()

                data["mean_quality"] = float(value)

            elif line.startswith("Mean read length"):

                value = line.split(":")[1].strip()

                value = value.replace(",", "")

                data["mean_length"] = float(value)

    return data


# =====================================================
# AUTO NANOFILT
# =====================================================

def recommended_nanofilt(stats_file):

    """
    Recommend NanoFilt thresholds
    based on NanoPlot statistics.
    """

    stats = parse_nanostats(stats_file)

    q = stats["mean_quality"]

    l = stats["mean_length"]

    # ------------------------
    # Quality
    # ------------------------

    if q < 8:

        quality = 8

    elif q < 10:

        quality = 10

    elif q < 12:

        quality = 12

    else:

        quality = 12

    # ------------------------
    # Read Length
    # ------------------------

    if l < 800:

        length = 300

    elif l < 2000:

        length = 500

    else:

        length = 1000

    return quality, length


# =====================================================
# FASTP SUMMARY
# =====================================================

def parse_fastp_json(json_file):

    """
    Parse fastp.json

    Returns

    {
        "q20":97.5,
        "q30":93.2,
        "mean_length":1420
    }
    """

    data = read_json(json_file)

    before = data["summary"]["before_filtering"]

    q20 = before.get("q20_rate", 0) * 100

    q30 = before.get("q30_rate", 0) * 100

    mean_length = before.get("read1_mean_length", 0)

    return {

        "q20": q20,

        "q30": q30,

        "mean_length": mean_length,

    }


# =====================================================
# PRINT AUTO SETTINGS
# =====================================================

def print_filter_settings(q, l):

    print("\nRecommended NanoFilt settings")

    print("----------------------------")

    print(f"Minimum Quality : {q}")

    print(f"Minimum Length  : {l}")

    print()