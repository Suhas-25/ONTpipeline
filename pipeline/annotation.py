from utils import run_command


def run(config):

    print("\n========== ANNOTATION ==========\n")

    image = config["docker"]["snpeff"]

    variant_tool = config["variant"]["tool"].lower()

    # ----------------------------------------------------
    # Select correct VCF based on variant caller
    # ----------------------------------------------------

    if variant_tool == "bcftools":

        vcf = "output/variants.bcftools.vcf.gz"

    elif variant_tool == "longshot":

        vcf = "output/variants.longshot.vcf"

    elif variant_tool == "medaka":

        vcf = "output/medaka/medaka.vcf"

    elif variant_tool == "clair3":

        vcf = "output/clair3/merge_output.vcf.gz"

    else:

        raise ValueError(f"Unsupported variant caller: {variant_tool}")

    output = "output/annotated.vcf"

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
bash -c "
snpEff \
-c /snpEff/snpEff.config \
LSDV \
{vcf} \
> {output}
"
"""

    run_command(cmd)

    print("Annotation completed.")