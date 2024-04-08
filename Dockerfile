FROM python:3.12.2-alpine3.19
RUN pip install Flask
RUN pip install waitress
RUN pip install PuLP
RUN pip install networkx
RUN pip install waitress
RUN pip install jsonschema
EXPOSE 5001
COPY *.py .
CMD ["python", "server.py"]