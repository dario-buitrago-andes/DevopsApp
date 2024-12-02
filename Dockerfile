FROM python:3.8-slim

# Establecer el directorio de trabajo
WORKDIR /src

# Copiar los archivos Pipfile y Pipfile.lock al directorio de trabajo actual
COPY Pipfile /src/

# Copiar el código fuente al directorio de trabajo
COPY src/ /src/

ENV VERSION=1.0
ENV FLASK_APP=main.py
ENV FLASK_DEBUG=1
ENV FLASK_ENV=production
ENV DB_USER="postgres"
ENV DB_PASSWORD="Devops123!"
ENV DB_HOST="devops-database.c1wq6u8y4zko.us-east-2.rds.amazonaws.com"
ENV DB_PORT=5432
ENV DB_NAME="blacklist"
ENV SECRET_TOKEN=token-super-secreto



# Instalar las dependencias
RUN pip install --upgrade pip
RUN pip install pipenv

# Instala las dependencias del proyecto
RUN pipenv install

# Exponer el puerto
EXPOSE 5000

# Espera 10 segundos


# Define el comando por defecto para ejecutar el microservicio, con espera de 10 segundos
CMD ["sh", "-c", "sleep 10 && pipenv run flask --app main.py run -h 0.0.0.0 -p 5000"]

RUN pip install newrelic

ENV NEW_RELIC_APP_NAME="DevopsApp"
ENV NEW_RELIC_LOG=stdout
ENV NEW_RELIC_DISTRIBUTED_TRACING_ENABLED=true
ENV NEW_RELIC_LICENSE_KEY=094D3956AF83C7C94DFE38A0FD7D065522C29DE004799C12DEBA65E1B52C1014
ENV NEW_RELIC_LOG_LEVEL=info

ENTRYPOINT [ "newrelic-admin", "run-program" ]