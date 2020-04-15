FROM python:3.8

RUN pip install -r requirements.txt
RUN mkdir /coupon-loader
COPY load_*_coupons.py /coupon-loader/
COPY config.ini /coupon-loader/
WORKDIR /coupon-loader/
CMD python load_all_coupons.py
