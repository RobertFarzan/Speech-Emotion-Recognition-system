FROM public.ecr.aws/lambda/python:3.8

RUN mkdir -m 777 /tmp/NUMBA_CACHE_DIR
ENV NUMBA_CACHE_DIR=/tmp/NUMBA_CACHE_DIR

RUN yum -y install libsndfile

COPY requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt
COPY handler.py ./

CMD ["handler.lambda_handler"]
