# Base image with Conda
FROM continuumio/miniconda3:latest

LABEL maintainer="Suhas"
LABEL description="Docker image for ARTIC align_trim"

# Install align_trim and samtools
RUN conda install -y -c bioconda align_trim samtools && \
    conda clean -afy

# Verify installation
RUN align_trim --help
RUN samtools --version

# Default working directory
WORKDIR /data

# Default command
ENTRYPOINT ["align_trim"]
