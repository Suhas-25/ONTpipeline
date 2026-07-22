from qc import run as qc_run
from align import run as align_run
from primer import run as primer_run
from variant import run as variant_run
from consensus import run as consensus_run
from annotation import run as annotation_run
from report import run as report_run


def execute_pipeline(config):

    print("\n========== STARTING PIPELINE ==========\n")

    qc_run(config)

    align_run(config)

    primer_run(config)

    variant_run(config)

    consensus_run(config)

    annotation_run(config)

    report_run(config)

    print("\n========== PIPELINE COMPLETED ==========\n")