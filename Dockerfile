FROM python:3.8
RUN mkdir /app
WORKDIR /app

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD . .

CMD ["python","main.py","--kw_list='lavender shampoo','lavender soap','lavender hand sanitizer'"]