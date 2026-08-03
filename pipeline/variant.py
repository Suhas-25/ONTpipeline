import os
from utils import compress_and_index_vcf, make_directory, run_command


def select_bam(config):
    """Select the BAM produced by the currently configured workflow."""

    primer_enabled = config["primer"].get("enabled", False)
    trimmed_bam = "output/trimmed.sorted.bam"

    if primer_enabled and os.path.exists(trimmed_bam):

        print("Using primer-trimmed BAM.")

        return trimmed_bam

    print("Using untrimmed alignment BAM.")

    return "output/alignment.sorted.bam"


def write_uncompressed_vcf(config, compressed_vcf, output_vcf):

    image = config["docker"]["core"]

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
bash -c '
gunzip -c {compressed_vcf} > {output_vcf}
'
"""

    run_command(cmd)


def run(config):

    print("\n========== VARIANT CALLING ==========\n")

    tool = config["variant"]["tool"].lower()

    if tool == "bcftools":

        run_bcftools(config)

    elif tool == "medaka":

        run_medaka(config)

    elif tool == "clair3":

        run_clair3(config)

    else:

        raise ValueError(f"Unsupported variant caller: {tool}")


# ----------------------------------------------------------
# bcftools
# ----------------------------------------------------------

def run_bcftools(config):

    print("Running bcftools...")

    image = config["docker"]["core"]

    # ---------------------------------------
    # Select BAM
    # ---------------------------------------

    bam = select_bam(config)

    reference = config["input"]["reference"]

    compressed_output = "output/variants.bcftools.vcf.gz"

    uncompressed_output = "output/variants.bcftools.vcf"

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
bash -c '
bcftools mpileup \
-f {reference} \
{bam} \
| bcftools call \
-m -v \
-Oz \
-o {compressed_output} && \
bcftools index {compressed_output}
'
"""

    run_command(cmd)

    write_uncompressed_vcf(config, compressed_output, uncompressed_output)

    print("bcftools completed.")


# ----------------------------------------------------------
# Medaka
# ----------------------------------------------------------

def run_medaka(config):

    print("Running Medaka...")

    image = config["docker"]["medaka"]

    reference = config["input"]["reference"]

    bam = select_bam(config)

    output_dir = "output/medaka"

    make_directory(output_dir)

    predictions = f"{output_dir}/predictions.hdf"

    output_vcf = f"{output_dir}/medaka.vcf"

    model = config["medaka"]["model"]

    read_group_option = "--ignore_read_groups" if config["medaka"].get(
        "ignore_read_groups", False
    ) else ""

    # Predictions are run-specific. Docker may own files created in the
    # bind-mounted output directory, so clean an old file from Docker rather
    # than with host-side os.remove().
    if os.path.exists(predictions):
        cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
--entrypoint rm \
{image} \
-f {predictions}
"""

        run_command(cmd)

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
medaka inference \
--model {model} \
{read_group_option} \
{bam} \
{predictions}
"""

    run_command(cmd)

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
medaka vcf \
{predictions} \
{reference} \
{output_vcf}
"""

    run_command(cmd)

    compress_and_index_vcf(config, output_vcf)

    print("Medaka completed.")


# ----------------------------------------------------------
# Clair3
# ----------------------------------------------------------

def run_clair3(config):

    print("Running Clair3...")

    image = config["docker"]["clair3"]

    bam = select_bam(config)

    reference = config["input"]["reference"]

    output = "output/clair3"

    threads = config["threads"]

    model = config["clair3"]["model_path"]

    platform = config["clair3"]["platform"]

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
run_clair3.sh \
-b {bam} \
-f {reference} \
-m {model} \
-t {threads} \
-p {platform} \
-o {output}
"""

    run_command(cmd)

    compress_and_index_vcf(config, "output/clair3/merge_output.vcf.gz")

    write_uncompressed_vcf(
        config,
        "output/clair3/merge_output.vcf.gz",
        "output/clair3/merge_output.vcf",
    )

    print("Clair3 completed.")
