
# ONTpipeline

A modular, Docker-based Oxford Nanopore (ONT) sequencing analysis pipeline for
Lumpy Skin Disease Virus (LSDV).

The pipeline is designed to support both Whole Genome Sequencing (WGS) and
Amplicon Sequencing workflows while allowing users to choose different tools
for each analysis stage through a simple YAML configuration file.

The project is intended for integration into the Dharini platform and follows a
modular architecture where every analysis step is implemented independently.

---

# Features

✔ Oxford Nanopore FASTQ input

✔ Modular workflow

✔ Docker-based execution

✔ YAML configuration

✔ Optional primer trimming

✔ Multiple variant callers

✔ Multiple consensus methods

✔ Variant annotation

✔ Final report generation

✔ Easily extensible

---

# Pipeline Workflow

```

FASTQ
│
▼
Input Validation
│
▼
Load Configuration
(default.yaml)
│
▼
Quality Control
│
├── NanoPlot
│ │
│ └── NanoFilt (Optional)
│
└── fastp
│
▼
Alignment
│
└── minimap2
│
▼
samtools sort
│
▼
samtools index
│
▼
Primer Trimming
│
BED provided?
│
├── YES
│ │
│ ▼
│ ARTIC align_trim
│ │
│ ▼
│ samtools sort/index
│
└── NO
│ │
│ ▼
│ Warning
│ Continue analysis
│
▼
Variant Calling
│
├── bcftools
├── Longshot
├── Medaka
└── Clair3
│
▼
Consensus Generation
│
├── bcftools
└── Medaka
│
▼
Annotation
│
└── snpEff
│
▼
Pipeline Report


Directory Structure
ONTpipeline/

config/
    default.yaml

pipeline/
    main.py
    workflow.py
    utils.py

    qc.py
    align.py
    primer.py
    variant.py
    consensus.py
    annotation.py
    report.py

input/

reference/

output/

logs/

docs/

test_data/

README.md

Architecture
The pipeline follows a modular architecture.
Each module performs one specific task.
main.py

↓

workflow.py

↓

qc.py

↓

align.py

↓

primer.py

↓

variant.py

↓

consensus.py

↓

annotation.py

↓

report.py
Each module can be modified independently without affecting the rest of the pipeline.

Configuration
The entire pipeline is controlled using
config/default.yaml
No Python code needs to be modified to change the workflow.
Example
variant:

    tool: bcftools
Change to
variant:

    tool: clair3
The pipeline will automatically use Clair3.

Supported QC Tools
NanoPlot
Purpose
    • Read quality assessment
    • Read length distribution
    • QC visualization
Produces
NanoPlot-report.html

NanoStats.txt

NanoFilt (Optional)
Runs only when enabled.
Purpose
    • Remove low-quality reads
    • Remove short reads
    • Optional head/tail cropping
Supports
Recommended Mode

Manual Mode

fastp
Alternative QC tool.
Provides
    • Read filtering
    • Quality trimming
    • Adapter trimming
    • HTML report
    • JSON report

Alignment
Current aligner
minimap2
Output
alignment.sorted.bam

alignment.sorted.bam.bai

Primer Trimming
Uses
ARTIC align_trim
Input
BED primer scheme
Behaviour
If BED file is supplied
↓
Primer trimming performed
↓
Trimmed BAM is coordinate sorted and indexed
Otherwise
↓
Pipeline continues
↓
Warning displayed
Primer BED not provided.

Variants within primer-binding regions should be interpreted with caution.

Variant Calling
Currently supports
bcftools

Longshot

Medaka

Clair3
Selection is controlled using
variant:

    tool:

Consensus Generation
Supported
bcftools

Medaka
Produces
Consensus FASTA sequence.

Annotation
Uses
snpEff
with
Custom LSDV database.
Produces
Annotated VCF.

Report
The final report summarizes
    • QC
    • Alignment
    • Variant Calling
    • Consensus
    • Annotation
Future versions may support HTML/PDF reports.

Docker Images
Core Image
suhas0/lsdv_core:v4
Contains
    • Python
    • Java
    • minimap2
    • samtools
    • bcftools
    • fastp
    • NanoPlot

Medaka
ontresearch/medaka:latest

Clair3
hkubal/clair3:latest

Longshot
staphb/longshot:latest

ARTIC align_trim
align_trim:v1

snpEff
suhas0/snpeff_lsdv:v1
Contains
    • snpEff
    • Custom LSDV database

Running the Pipeline
python3 pipeline/main.py
The pipeline automatically
    • Loads configuration
    • Performs QC
    • Aligns reads
    • Performs optional primer trimming
    • Calls variants
    • Generates consensus
    • Annotates variants
    • Creates final report

Outputs
output/

qc/

NanoPlot-report.html

NanoStats.txt

fastp.html

fastp.json

filtered.fastq.gz (optional)

alignment.sorted.bam

alignment.sorted.bam.bai

variants.bcftools.vcf.gz

variants.longshot.vcf

medaka/

clair3/

bcftools_consensus.fasta

medaka_consensus.fasta

annotated.vcf

pipeline_report.txt

Design Philosophy
The pipeline was designed around five principles.
1. Modular
Every analysis stage is isolated into its own Python module.
This simplifies maintenance and future development.

2. Configurable
Pipeline behaviour is controlled entirely through YAML.
No Python code changes are required to switch tools.

3. Reproducible
Every bioinformatics tool runs inside a Docker container.
This ensures identical execution across systems.

4. Extensible
New tools can be added with minimal code changes.
Examples
    • New aligners
    • New variant callers
    • Additional annotation tools

5. Platform Ready
The pipeline was developed with Dharini platform integration in mind.
The platform only needs to
    • Upload user inputs
    • Update YAML configuration
    • Execute
python3 pipeline/main.py
    • Collect output files

Current Supported Workflow
FASTQ

↓

NanoPlot / fastp

↓

Optional NanoFilt

↓

minimap2

↓

samtools

↓

Optional ARTIC align_trim

↓

samtools sort/index

↓

bcftools / Longshot / Medaka / Clair3

↓

Consensus

↓

snpEff

↓

Pipeline Report

run by --python3 /ONTpipeline/main.py

✔ Oxford Nanopore FASTQ (.fastq.gz) input

# Prerequisites

Before running the pipeline ensure the following are installed.

## Software

- Python 3.10+
- Docker Engine
- Docker daemon running

## Python dependency

```bash
pip install -r requirements.txt
