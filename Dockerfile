FROM python:3.8

RUN pip install configparser requests
RUN mkdir /coupon-loader
COPY load_coupons.py /coupon-loader/
COPY config.ini /coupon-loader/
WORKDIR /coupon-loader/
CMD python load_coupons.py
