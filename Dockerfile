# FROM public.ecr.aws/lambda/python:3.9

# COPY models/ /var/task/models/
# COPY app.py /var/task/
# COPY requirements.txt /var/task/

# # Install dependencies into /var/task
# RUN pip3 install -r requirements.txt --target "/var/task"

# # Lambda entrypoint
# CMD ["app.handler"]

FROM public.ecr.aws/lambda/python:3.9

# Install build dependencies
RUN yum update -y && \
    yum groupinstall -y "Development Tools" && \
    yum install -y cmake gcc-c++ && \
    yum clean all

COPY models/ /var/task/models/
COPY app.py /var/task/
COPY requirements.txt /var/task/

# Install dependencies into /var/task
RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt --target "/var/task"

# Lambda entrypoint
CMD ["app.handler"]