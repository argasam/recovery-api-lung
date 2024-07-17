# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN apt-get update
RUN apt-get install pkg-config -y
RUN apt-get install libhdf5-serial-dev
RUN pip install --upgrade "setuptools>=44.0.0"
RUN pip install --upgrade "wheel>=0.37.1"
RUN pip install --upgrade Cython
RUN pip install --no-binary=h5py h5py
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app

# 
CMD ["fastapi", "run", "app/main.py", "--port", "80"]