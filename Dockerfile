FROM public.ecr.aws/lambda/python:3.9

# Install system deps
RUN yum install -y gcc gcc-c++ make cmake

# Copy model and code
COPY models/ /var/task/models/
COPY app.py /var/task/
COPY requirements.txt /var/task/

# Install dependencies
RUN pip3 install -r requirements.txt --target "/var/task"

CMD ["app.handler"]

