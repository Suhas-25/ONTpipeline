import os
from utils import run_command


def select_bam():
    """Use ARTIC-trimmed coordinate-sorted BAM when primer trimming ran."""

    if os.path.exists("output/trimmed.sorted.bam"):

        return "output/trimmed.sorted.bam"

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

    elif tool == "longshot":

        run_longshot(config)

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

    bam = select_bam()

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
# Longshot
# ----------------------------------------------------------

def run_longshot(config):

    print("Running Longshot...")

    image = config["docker"]["longshot"]

    bam = select_bam()

    reference = config["input"]["reference"]

    output = "output/variants.longshot.vcf"

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
longshot \
--bam {bam} \
--ref {reference} \
--out {output}
"""

    run_command(cmd)

    print("Longshot completed.")


# ----------------------------------------------------------
# Medaka
# ----------------------------------------------------------

def run_medaka(config):

    print("Running Medaka...")

    image = config["docker"]["medaka"]

    fastq = config["input"]["fastq"]

    reference = config["input"]["reference"]

    output = "output/medaka"

    threads = config["threads"]

    model = config["medaka"]["variant_model"]

    if model:

        cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
medaka_variant \
-i {fastq} \
-r {reference} \
-o {output} \
-m {model} \
-t {threads}
"""

    else:

        cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
medaka_variant \
-i {fastq} \
-r {reference} \
-o {output} \
-t {threads}
"""

    run_command(cmd)

    print("Medaka completed.")


# ----------------------------------------------------------
# Clair3
# ----------------------------------------------------------

def run_clair3(config):

    print("Running Clair3...")

    image = config["docker"]["clair3"]

    bam = select_bam()

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

    write_uncompressed_vcf(
        config,
        "output/clair3/merge_output.vcf.gz",
        "output/clair3/merge_output.vcf",
    )

    print("Clair3 completed.")
