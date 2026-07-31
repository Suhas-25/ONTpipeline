import subprocess

from utils import warning


def run_primer_command(cmd, step):
    """Run ARTIC align_trim or BAM post-processing and fail clearly."""

    print(f"\n[CMD]\n{cmd}\n")

    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"{step} failed with exit code {result.returncode}.\n"
            f"Command:\n{cmd}\n"
            f"stderr:\n{result.stderr}"
        )

    return result.stdout


def run(config):
    """Trim primers with ARTIC align_trim and coordinate-sort the output BAM."""

    print("\n========== PRIMER TRIMMING ==========\n")

    bed = config["input"]["bed"]

    if not bed:

        warning(
            "Primer BED file not provided.\n"
            "Skipping ARTIC align_trim.\n"
            "Variants in primer-binding regions should be interpreted with caution."
        )

        return

    image = config["docker"]["align_trim"]

    input_bam = "output/alignment.sorted.bam"

    trimmed_bam = "output/trimmed.bam"

    sorted_bam = "output/trimmed.sorted.bam"

    report = "output/align_trim.report.tsv"

    log = "output/align_trim.log"

    cmd = f"""
docker run --rm \
-v $(pwd):/data \
-w /data \
{image} \
bash -c "
align_trim \
-b {input_bam} \
--report {report} \
{bed} \
> {trimmed_bam} \
2> {log}
"
"""

    run_primer_command(cmd, "ARTIC align_trim")

    image = config["docker"]["core"]

    cmd = f"""
docker run --rm \
-v $(pwd):/data \
-w /data \
{image} \
samtools sort \
{trimmed_bam} \
-o {sorted_bam}
"""

    run_primer_command(cmd, "samtools sort for ARTIC-trimmed BAM")

    cmd = f"""
docker run --rm \
-v $(pwd):/data \
-w /data \
{image} \
samtools index {sorted_bam}
"""

    run_primer_command(cmd, "samtools index for ARTIC-trimmed BAM")

    print("Primer trimming completed.")
