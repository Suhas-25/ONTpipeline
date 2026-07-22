import os

from utils import run_command


def run(config):

    print("\n========== ALIGNMENT ==========\n")

    image = config["docker"]["core"]

    reference = config["input"]["reference"]

    threads = config["threads"]

    # ------------------------------------------------------
    # Select FASTQ
    # ------------------------------------------------------

    filtered_fastq = "output/qc/filtered.fastq.gz"

    if os.path.exists(filtered_fastq):

        print("Using filtered FASTQ.")

        fastq = filtered_fastq

    else:

        print("Using original FASTQ.")

        fastq = config["input"]["fastq"]

    bam = "output/alignment.sorted.bam"

    # ------------------------------------------------------
    # Alignment
    # ------------------------------------------------------

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
bash -c '
minimap2 \
-ax map-ont \
-t {threads} \
{reference} \
{fastq} \
| samtools sort \
-@ {threads} \
-o {bam}
'
"""

    run_command(cmd)

    # ------------------------------------------------------
    # BAM Index
    # ------------------------------------------------------

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
samtools index {bam}
"""

    run_command(cmd)

    print("Alignment completed.")