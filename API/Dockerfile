FROM python

RUN pip install flask requests PyJWT flask_cors cryptography
COPY report_api.py /opt
WORKDIR /opt
CMD ["python", "report_api.py"]