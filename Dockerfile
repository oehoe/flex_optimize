FROM python:slim
RUN pip install Flask
RUN pip install waitress
RUN pip install PuLP
RUN pip install networkx
RUN pip install waitress
RUN pip install jsonschema
EXPOSE 5001
COPY server.py .
COPY optimize.py .
copy request_schema.json .
CMD ["python", "server.py"]