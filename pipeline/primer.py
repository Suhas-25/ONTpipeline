from utils import run_command, warning


def run(config):

    print("\n========== PRIMER TRIMMING ==========\n")

    bed = config["input"]["bed"]

    if not bed:

        warning(
            "Primer BEDPE file not provided.\n"
            "Skipping BamClipper.\n"
            "Variants in primer-binding regions should be interpreted with caution."
        )

        return

    image = config["docker"]["bamclipper"]

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
bamclipper.sh \
-b output/alignment.sorted.bam \
-p {bed}
"""

    run_command(cmd)

    print("Primer trimming completed.")