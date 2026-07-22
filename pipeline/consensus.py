from utils import run_command


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

        vcf = "output/variants.longshot.vcf"

    elif variant_tool == "clair3":

        vcf = "output/clair3/merge_output.vcf.gz"

    elif variant_tool == "medaka":

        vcf = "output/medaka/medaka.vcf"

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

    bam = "output/alignment.sorted.bam"

    reference = config["input"]["reference"]

    threads = config["threads"]

    output_dir = "output/medaka_consensus"

    predictions = f"{output_dir}/predictions.hdf"

    consensus = f"{output_dir}/consensus.fasta"

    model = config["medaka"]["consensus_model"]

    # ---------------------------------------
    # Step 1 : inference
    # ---------------------------------------

    if model:

        cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
medaka inference \
{bam} \
{predictions} \
--model {model}
"""

    else:

        cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
medaka inference \
{bam} \
{predictions}
"""

    run_command(cmd)

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