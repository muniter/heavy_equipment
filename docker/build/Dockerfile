FROM odoo:12.0
COPY ./requirements.txt /requirements.txt
USER root
RUN set -x; \
    pip3 install wheel \
    && pip3 install --no-cache-dir -r requirements.txt
USER odoo
