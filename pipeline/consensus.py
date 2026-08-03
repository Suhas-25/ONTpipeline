import os

from utils import make_directory, run_command
from variant import select_bam


def run(config):

    print("\n========== CONSENSUS ==========\n")

    tool = config["consensus"]["tool"].lower()

    if tool == "bcftools":

        run_bcftools(config)

    elif tool == "medaka":

        run_medaka(config)

    else:

        raise ValueError(f"Unsupported consensus tool: {tool}")


# ----------------------------------------------------------
# bcftools Consensus
# ----------------------------------------------------------

def run_bcftools(config):

    print("Running bcftools consensus...")

    image = config["docker"]["core"]

    reference = config["input"]["reference"]

    variant_tool = config["variant"]["tool"].lower()

    # Select correct VCF automatically
    if variant_tool == "bcftools":

        vcf = "output/variants.bcftools.vcf.gz"

    elif variant_tool == "longshot":

        vcf = "output/variants.longshot.vcf.gz"

    elif variant_tool == "clair3":

        vcf = "output/clair3/merge_output.vcf.gz"

    elif variant_tool == "medaka":

        vcf = "output/medaka/medaka.vcf.gz"

    else:

        raise ValueError(f"Unsupported variant tool: {variant_tool}")

    output = "output/bcftools_consensus.fasta"

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
bash -c "
cat {reference} \
| bcftools consensus {vcf} \
> {output}
"
"""

    run_command(cmd)

    print("bcftools consensus completed.")


# ----------------------------------------------------------
# Medaka Consensus
# ----------------------------------------------------------

def run_medaka(config):

    print("Running Medaka consensus...")

    image = config["docker"]["medaka"]

    reference = config["input"]["reference"]

    output_dir = "output/medaka"

    # Medaka writes predictions and consensus files into this directory.
    # Create it before starting the container so the bind-mounted path exists.
    make_directory(output_dir)

    predictions = f"{output_dir}/predictions.hdf"

    consensus = f"{output_dir}/consensus.fasta"

    model = config["medaka"]["model"]

    read_group_option = "--ignore_read_groups" if config["medaka"].get(
        "ignore_read_groups", False
    ) else ""

    # ---------------------------------------
    # Step 1 : inference
    # ---------------------------------------

    if not os.path.isfile(predictions):

        bam = select_bam(config)

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

    else:
        print("Reusing Medaka predictions created during variant calling.")

    # ---------------------------------------
    # Step 2 : sequence
    # ---------------------------------------

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
medaka sequence \
{predictions} \
{reference} \
{consensus}
"""

    run_command(cmd)

    print("Medaka consensus completed.")
