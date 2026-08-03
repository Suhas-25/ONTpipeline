# ONTpipeline

> A modular, Docker-based Oxford Nanopore Technologies (ONT) analysis pipeline for Lumpy Skin Disease Virus (LSDV).

ONTpipeline turns ONT FASTQ reads into quality-control results, a reference alignment, variants, a consensus sequence, annotated results, and a final report. Each stage is selected through one YAML configuration file, so the workflow can be adapted without editing Python code.

## At a glance

| Input | Processing | Main outputs |
| --- | --- | --- |
| ONT FASTQ (`.fastq.gz`) | QC → alignment → optional primer trimming → variant calling | BAM, VCF, consensus FASTA, annotation, report |
| LSDV reference FASTA | Docker containers keep tools reproducible | Files are written to `output/` |

## Features

- Docker-based, reproducible tool execution
- YAML-controlled workflow and tool selection
- NanoPlot or fastp quality control
- minimap2 alignment with sorted and indexed BAM output
- Optional ARTIC `align_trim` primer trimming
- Variant calling with bcftools, Medaka, or Clair3
- Consensus creation with bcftools or Medaka
- snpEff annotation using a custom LSDV database
- Text report generation

## Workflow

```text
FASTQ reads
   │
   ├── Quality control ────────────── NanoPlot / fastp / optional NanoFilt
   │
   ├── Alignment ──────────────────── minimap2 → samtools sort + index
   │
   ├── Primer trimming (optional) ─── ARTIC align_trim → samtools sort + index
   │
   ├── Variant calling ────────────── bcftools / Medaka / Clair3
   │
   ├── Consensus ──────────────────── bcftools / Medaka
   │
   ├── Annotation ─────────────────── snpEff
   │
   └── Final report
```

## Quick start

### What users need before running

Users do **not** need to prepare output folders or software indexes manually. Start with the following project layout:

```text
ONTpipeline/
├── config/default.yaml
├── input/
│   └── sample.fastq.gz          # Required: ONT reads
├── reference/
│   └── reference.fasta          # Required: matching reference genome
└── primer_scheme.bed            # Required only for amplicon sequencing
```

| Workflow | Required user files | Configuration |
| --- | --- | --- |
| Whole-genome sequencing (WGS) | FASTQ and reference FASTA | Set `primer.enabled: false` |
| Amplicon sequencing | FASTQ, reference FASTA, and matching primer BED | Set `primer.enabled: true` and provide `input.bed` |

For amplicon data, the BED contig names and coordinates must match the reference FASTA exactly. The pipeline creates the FASTA `.fai` index automatically when it is missing.

The pipeline creates these folders and files itself: `output/`, `output/qc/`, BAM indexes, Medaka prediction files, VCFs, consensus FASTA files, and reports.

### 1. Prerequisites

- Python 3.10 or newer
- Docker Engine, with the Docker daemon running
- Permission to run Docker commands

Install the Python dependency:

```bash
pip install -r requirements.txt
```

### 2. Set your inputs

Edit [`config/default.yaml`](config/default.yaml) and set the paths for your reads and reference:

```yaml
input:
  fastq: input/SRR25593956.fastq.gz
  reference: reference/lsdv_reference.fasta
  bed: primers.bed  # optional ARTIC primer-scheme BED file
```

If you do not want primer trimming, leave `bed` empty:

```yaml
bed:
```

### 3. Run the pipeline

From the project directory:

```bash
python3 pipeline/main.py --config config/default.yaml
```

## Configuration

All workflow choices are in [`config/default.yaml`](config/default.yaml). For example, select a variant caller:

```yaml
variant:
  tool: bcftools
```

Supported values are `bcftools`, `medaka`, and `clair3`.

| Section | Controls |
| --- | --- |
| `input` | FASTQ, reference FASTA, and optional primer BED paths |
| `threads` | Number of CPU threads used by supported tools |
| `qc` / `filter` | Quality-control and filtering behaviour |
| `alignment` | Alignment tool selection |
| `variant` | Variant caller selection |
| `consensus` | Consensus method selection |
| `docker` | Docker image names used by each stage |

## Primer trimming

Primer trimming uses ARTIC `align_trim` when a BED primer scheme is supplied. The trimmed BAM is coordinate-sorted and indexed before variant calling. Without a BED file, the pipeline continues using the original alignment; variants in primer-binding regions should then be interpreted carefully.

## Outputs

Results are written to `output/`.

| Output | Description |
| --- | --- |
| `output/qc/` | NanoPlot or fastp quality-control reports |
| `output/alignment.sorted.bam` | Sorted reference alignment |
| `output/alignment.sorted.bam.bai` | Alignment index |
| `output/trimmed.sorted.bam` | Primer-trimmed BAM, when enabled |
| `output/variants.*.vcf` and `.vcf.gz` + `.csi` | Plain user-readable and compressed/indexed variant calls |
| `output/bcftools_consensus.fasta` | bcftools consensus, when selected |
| `output/medaka_consensus.fasta` | Medaka consensus, when selected |
| `output/annotated.vcf` and `.vcf.gz` + `.csi` | Plain user-readable and compressed/indexed snpEff annotation |
| `output/pipeline_report.txt` | Final pipeline summary |

## Docker images

| Stage | Image |
| --- | --- |
| Core tools | `suhas0/lsdv_core:v4` |
| Medaka | `ontresearch/medaka:latest` |
| Clair3 | `hkubal/clair3:latest` |
| Primer trimming | `align_trim:v1` |
| snpEff annotation | `suhas0/snpeff_lsdv:v1` |

## Project structure

```text
ONTpipeline/
├── config/
│   └── default.yaml        # Workflow settings
├── pipeline/
│   ├── main.py             # Command-line entry point
│   ├── workflow.py         # Runs stages in order
│   ├── qc.py               # Quality control
│   ├── align.py            # Reference alignment
│   ├── primer.py           # Primer trimming
│   ├── variant.py          # Variant calling
│   ├── consensus.py        # Consensus generation
│   ├── annotation.py       # snpEff annotation
│   └── report.py           # Final report
├── input/                  # Input reads
├── reference/              # Reference data
├── Dockerfile/             # align_trim Docker image definition
├── requirements.txt
└── README.md
```

## Pipeline design

The pipeline is organised as independent modules. `main.py` loads the configuration, then `workflow.py` runs QC, alignment, primer trimming, variant calling, consensus generation, annotation, and reporting in sequence. This modular design keeps individual stages easy to maintain and replace.

## Troubleshooting

| Problem | Check |
| --- | --- |
| `No module named 'yaml'` | Run `pip install -r requirements.txt` |
| Docker command fails | Confirm Docker is running with `docker ps` |
| Input file not found | Verify paths in `config/default.yaml` from the project directory |
| Primer trimming fails | Confirm the BED file exists and matches the reference/amplicon scheme |

---

Built for ONT sequencing analysis and planned Dharini platform integration.
