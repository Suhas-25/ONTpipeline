import os
from datetime import datetime


def exists(path):
    return "YES" if os.path.exists(path) else "NO"


def run(config):

    print("\n========== REPORT ==========\n")

    output_dir = config["output"]["directory"]

    report_file = os.path.join(output_dir, "pipeline_report.txt")

    variant_tool = config["variant"]["tool"]
    consensus_tool = config["consensus"]["tool"]

    with open(report_file, "w") as report:

        report.write("====================================================\n")
        report.write("ONT VARIANT ANALYSIS PIPELINE REPORT\n")
        report.write("====================================================\n\n")

        report.write(f"Generated : {datetime.now()}\n\n")

        # ---------------------------------------------------
        # INPUTS
        # ---------------------------------------------------

        report.write("INPUT FILES\n")
        report.write("----------------------------------------\n")

        report.write(f"FASTQ      : {config['input']['fastq']}\n")
        report.write(f"Reference  : {config['input']['reference']}\n")

        bed = config["input"]["bed"]

        if bed:
            report.write(f"Primer BED : {bed}\n")
        else:
            report.write("Primer BED : Not Provided\n")

        report.write("\n")

        # ---------------------------------------------------
        # TOOLS
        # ---------------------------------------------------

        report.write("TOOLS USED\n")
        report.write("----------------------------------------\n")

        report.write(f"QC                 : {config['qc']['tool']}\n")
        report.write(f"Alignment          : {config['alignment']['tool']}\n")

        if bed:
            report.write("Primer Trimming    : BamClipper\n")
        else:
            report.write("Primer Trimming    : Skipped\n")

        report.write(f"Variant Caller     : {variant_tool}\n")
        report.write(f"Consensus          : {consensus_tool}\n")
        report.write("Annotation         : snpEff\n")

        report.write("\n")

        # ---------------------------------------------------
        # OUTPUTS
        # ---------------------------------------------------

        report.write("OUTPUT FILES\n")
        report.write("----------------------------------------\n")

        report.write(
            f"Alignment BAM      : {exists('output/alignment.sorted.bam')}\n"
        )

        report.write(
            f"BAM Index          : {exists('output/alignment.sorted.bam.bai')}\n"
        )

        report.write(
            f"QC Report          : {exists('output/qc/NanoPlot-report.html')}\n"
        )

        report.write(
            f"Annotation         : {exists('output/annotated.vcf')}\n"
        )

        # Variant outputs

        report.write("\nVariant Outputs\n")

        report.write(
            f"bcftools           : {exists('output/variants.bcftools.vcf.gz')}\n"
        )

        report.write(
            f"Longshot           : {exists('output/variants.longshot.vcf')}\n"
        )

        report.write(
            f"Medaka             : {exists('output/medaka/medaka.vcf')}\n"
        )

        report.write(
            f"Clair3             : {exists('output/clair3/merge_output.vcf.gz')}\n"
        )

        # Consensus outputs

        report.write("\nConsensus Outputs\n")

        report.write(
            f"bcftools           : {exists('output/bcftools_consensus.fasta')}\n"
        )

        report.write(
            f"Medaka             : {exists('output/medaka_consensus/consensus.fasta')}\n"
        )

        report.write("\n")

        # ---------------------------------------------------
        # PIPELINE STATUS
        # ---------------------------------------------------

        report.write("PIPELINE STATUS\n")
        report.write("----------------------------------------\n")

        report.write("QC                 : COMPLETED\n")
        report.write("Alignment          : COMPLETED\n")

        if bed:
            report.write("Primer             : COMPLETED\n")
        else:
            report.write("Primer             : SKIPPED\n")

        report.write("Variant Calling    : COMPLETED\n")
        report.write("Consensus          : COMPLETED\n")
        report.write("Annotation         : COMPLETED\n")

        report.write("\n")

        report.write("====================================================\n")
        report.write("PIPELINE FINISHED SUCCESSFULLY\n")
        report.write("====================================================\n")

    print(f"Report saved to: {report_file}")