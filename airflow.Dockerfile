FROM marcelmittelstaedt/airflow:latest

LABEL org.opencontainers.image.source=https://github.com/hfxbse/dhbw-big-data

ENV HADOOP_HOST="hadoop"

RUN sed -i '34,41d' /startup.sh
RUN sed -i '3 i service ssh start' /startup.sh
RUN git clone --depth 1 https://github.com/marcelmittelstaedt/BigData.git /tmp/upstream
RUN wget https://jdbc.postgresql.org/download/postgresql-42.7.4.jar -P  /home/airflow/spark/jars/
RUN mv /tmp/upstream/exercises/winter_semester_2024-2025/05_airflow/plugins /home/airflow/airflow
RUN mv /tmp/upstream/exercises/winter_semester_2024-2025/05_airflow/dags /home/airflow/airflow
RUN mv /tmp/upstream/exercises/winter_semester_2024-2025/05_airflow/python /home/airflow/airflow
RUN sed -i 's/hadoop:/${HADOOP_HOST}:/g' /home/airflow/hadoop/etc/hadoop/core-site.xml
RUN sed -i 's/hadoop:/${HADOOP_HOST}:/g' /home/airflow/hadoop/etc/hadoop/yarn-site.xml
# Setting AIRFLOW__WEBSERVER__BASE_URL did not get applied for unknown reasons, update the config file instead
RUN sed -i "34 i sed -i 's#base_url = http://localhost:8080#base_url = http://localhost:8080/airflow#' /home/airflow/airflow/airflow.cfg" /startup.sh

COPY airflow/ /home/airflow/airflow/
COPY spark/ /home/airflow/airflow/python/
RUN chown -R airflow /home/airflow/airflow
RUN rm -r /tmp/upstream
