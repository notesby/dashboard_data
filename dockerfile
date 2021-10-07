#FROM python:3.9.1
FROM continuumio/anaconda3
ADD . /dashboard2
WORKDIR /dashboard2
#ENV PATH="/root/miniconda3/bin:${PATH}"
#ARG PATH="/root/miniconda3/bin:${PATH}"
#RUN apt-get update

#RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

#RUN wget \
#    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
#    && mkdir /root/.conda \
#    && bash Miniconda3-latest-Linux-x86_64.sh -b \
#    && rm -f Miniconda3-latest-Linux-x86_64.sh
#RUN conda init bash
#RUN conda --version
#RUN conda activate dashboard

<<<<<<< Updated upstream
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh
RUN conda --version
RUN conda env list
=======
>>>>>>> Stashed changes
RUN conda env create -f dashboard.yml
RUN echo "conda activate env" > ~/.bashrc
ENV PATH /opt/conda/envs/env/bin:$PATH

