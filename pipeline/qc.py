from utils import (
    run_command,
    recommended_nanofilt,
    print_filter_settings,
)


def run(config):

    print("\n========== QC ==========\n")

    tool = config["qc"]["tool"].lower()

    if tool == "nanoplot":

        run_nanoplot(config)

        if config["nanofilt"]["enabled"]:

            run_nanofilt(config)

    elif tool == "fastp":

        run_fastp(config)

    else:

        raise ValueError(f"Unsupported QC tool: {tool}")


# ----------------------------------------------------------
# NanoPlot
# ----------------------------------------------------------

def run_nanoplot(config):

    print("Running NanoPlot...")

    image = config["docker"]["core"]

    fastq = config["input"]["fastq"]

    output = "output/qc"

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
NanoPlot \
--fastq {fastq} \
--outdir {output}
"""

    run_command(cmd)

    print("NanoPlot completed.")


# ----------------------------------------------------------
# NanoFilt
# ----------------------------------------------------------

def run_nanofilt(config):

    print("Running NanoFilt...")

    image = config["docker"]["core"]

    fastq = config["input"]["fastq"]

    output = "output/qc/filtered.fastq.gz"

    mode = config["filter"]["mode"]

    if mode == "recommended":

        stats = "output/qc/NanoStats.txt"

        q, l = recommended_nanofilt(stats)

        print_filter_settings(q, l)

    else:

        q = config["nanofilt"]["min_quality"]

        l = config["nanofilt"]["min_length"]

    

    head = config["nanofilt"]["headcrop"]

    tail = config["nanofilt"]["tailcrop"]

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
bash -c "
gunzip -c {fastq} | \
NanoFilt \
-q {q} \
-l {l} \
--headcrop {head} \
--tailcrop {tail} | \
gzip > {output}
"
"""

    run_command(cmd)

    print(f"NanoFilt parameters: -q {q} -l {l}")
    print("NanoFilt completed.")


# ----------------------------------------------------------
# fastp
# ----------------------------------------------------------

def run_fastp(config):

    print("Running fastp...")

    image = config["docker"]["core"]

    fastq = config["input"]["fastq"]

    output = "output/qc/filtered.fastq.gz"

    html = "output/qc/fastp.html"

    json = "output/qc/fastp.json"

    quality = config["fastp"]["qualified_quality_phred"]

    length = config["fastp"]["length_required"]

    cmd = f"""
docker run --rm \
-v $(pwd):/pipeline \
-w /pipeline \
{image} \
fastp \
-i {fastq} \
-o {output} \
-q {quality} \
-l {length} \
-h {html} \
-j {json}
"""

    run_command(cmd)

    print("fastp completed.")

    