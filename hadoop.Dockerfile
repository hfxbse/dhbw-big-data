FROM marcelmittelstaedt/spark_base:latest

LABEL org.opencontainers.image.source=https://github.com/hfxbse/dhbw-big-data

RUN sed -i '44,50 s/^#//' /startup.sh
RUN sed -i '11 i chown -R hadoop /home/hadoop/hadoopdata' /startup.sh
RUN head -n -9 /startup.sh > temp.sh ; mv temp.sh /startup.sh
RUN echo "echo executing hiveserver2; sudo -u hadoop -H sh -c /home/hadoop/hive/bin/hiveserver2" >> /startup.sh
RUN chmod +x /startup.sh

RUN sed -i 's/hadoop:/0.0.0.0:/g' /home/hadoop/hadoop/etc/hadoop/core-site.xml

HEALTHCHECK --start-interval=10s --start-period=10s --retries=7 \
    CMD /bin/sh -c "exit $((4 - $(ps aux | grep -c org.apache.hive.service.server.HiveServer2)))"
