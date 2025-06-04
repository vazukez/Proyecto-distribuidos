FROM openjdk:8-jdk

# Instalar dependencias necesarias
RUN apt-get update && apt-get install -y wget tar ssh rsync --fix-missing && \
    rm -rf /var/lib/apt/lists/*

# Variables de entorno
ENV HADOOP_VERSION=2.7.7
ENV PIG_VERSION=0.17.0
ENV HADOOP_HOME=/opt/hadoop
ENV PIG_HOME=/opt/pig
ENV PATH=$PATH:$HADOOP_HOME/bin:$PIG_HOME/bin

# Instalar Hadoop
RUN wget https://archive.apache.org/dist/hadoop/core/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz && \
    tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt/ && \
    mv /opt/hadoop-${HADOOP_VERSION} $HADOOP_HOME && \
    rm hadoop-${HADOOP_VERSION}.tar.gz

# Instalar Pig
RUN wget https://archive.apache.org/dist/pig/pig-${PIG_VERSION}/pig-${PIG_VERSION}.tar.gz && \
    tar -xzf pig-${PIG_VERSION}.tar.gz -C /opt/ && \
    mv /opt/pig-${PIG_VERSION} $PIG_HOME && \
    rm pig-${PIG_VERSION}.tar.gz

# Crear carpetas de trabajo
RUN mkdir -p /data /scripts /output

WORKDIR /data

CMD ["bash"]
