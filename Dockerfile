FROM python:3.8-slim

# Establecer el directorio de trabajo
WORKDIR /src

# Copiar los archivos Pipfile y Pipfile.lock al directorio de trabajo actual
COPY Pipfile /src/

# Copiar el código fuente al directorio de trabajo
COPY src/ /src/

# Instalar las dependencias
RUN pip install --upgrade pip
RUN pip install pipenv

# Instala las dependencias del proyecto
RUN pipenv install

# Exponer el puerto
EXPOSE 2000

# Espera 10 segundos


# Define el comando por defecto para ejecutar el microservicio, con espera de 10 segundos
CMD ["sh", "-c", "sleep 10 && pipenv run flask --app main.py run -h 0.0.0.0 -p 2000"]