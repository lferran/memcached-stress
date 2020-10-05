FROM python:3.7.4-stretch

# Create folder where app will run and set path
WORKDIR /user/src/app

# Copy all there
COPY . .

# Install requirements
RUN pip install -r requirements.txt

# Install package
RUN pip install --no-deps -e .
