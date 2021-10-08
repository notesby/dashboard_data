FROM continuumio/anaconda3
ADD . /dashboard2
WORKDIR /dashboard2
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update
RUN apt-get install -y gnupg2
RUN apt-get install -y wget

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN apt-get install -y unixodbc-dev

#RUN conda init bash
#RUN conda --version
#RUN conda activate dashboard

RUN conda env create -f dashboard.yml
RUN echo "conda activate dashboard" > ~/.bashrc
ENV PATH /opt/conda/envs/dashboard/bin:$PATH

