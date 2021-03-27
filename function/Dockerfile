FROM --platform=${TARGETPLATFORM:-linux/amd64} openfaas/of-watchdog:0.7.7 as watchdog
FROM --platform=${TARGETPLATFORM:-linux/amd64} besn0847/arm-tiny-yolo:latest

COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog
RUN chmod +x /usr/bin/fwatchdog

ENTRYPOINT []

# Add non root user
RUN addgroup -S app && adduser app -S -G app
RUN chown app /usr/python

WORKDIR /usr/python

USER app
ENV PATH=$PATH:/usr/python/.local/bin

COPY yolov3-tiny.cfg .
COPY yolov3-tiny.txt .
COPY yolov3-tiny.weights .
COPY app.py .
#COPY startup.sh /

USER root
RUN chmod +x /startup.sh
RUN pip install waitress
RUN pip install requests

#RUN pip install --upgrade pip

# Populate example here - i.e. "cat", "sha512sum" or "node index.j>ENV fprocess="/startup.sh"
ENV fprocess="python app.py"
# Set to true to see request in function logs
ENV upstream_url="http://127.0.0.1:5000"
ENV mode="http"
ENV cgi_headers="true"

HEALTHCHECK --interval=3s CMD [ -e /tmp/.lock ] || exit 1

CMD ["fwatchdog"]
