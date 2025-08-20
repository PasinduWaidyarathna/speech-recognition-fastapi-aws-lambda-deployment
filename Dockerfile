# FROM public.ecr.aws/lambda/python:3.9

# # Install system deps
# RUN yum install -y gcc gcc-c++ make cmake

# # Copy model and code
# COPY models/ /var/task/models/
# COPY app.py /var/task/
# COPY requirements.txt /var/task/

# # Install dependencies
# RUN pip3 install -r requirements.txt --target "/var/task"

# CMD ["app.handler"]

# Use AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Install build tools and dependencies
RUN yum install -y gcc gcc-c++ make cmake amazon-linux-extras \
    && amazon-linux-extras enable gcc11 \
    && yum install -y gcc11 gcc11-c++ \
    && alternatives --install /usr/bin/gcc gcc /usr/bin/gcc11 100 \
    && alternatives --install /usr/bin/g++ g++ /usr/bin/g++11 100 \
    && yum clean all

# Upgrade pip, setuptools, and wheel
RUN pip3 install --upgrade pip setuptools wheel

# Copy application code and models
COPY models/ /var/task/models/
COPY app.py /var/task/
COPY requirements.txt /var/task/

# Install Python dependencies into /var/task
RUN pip3 install -r requirements.txt --target "/var/task"

# Lambda entrypoint
CMD ["app.handler"]


