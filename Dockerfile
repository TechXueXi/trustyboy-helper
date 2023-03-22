FROM alpine:3.12 as builder
ENV TZ Asia/Shanghai
ENV LC_ALL=zh_CN.UTF-8

RUN echo "https://mirrors.aliyun.com/alpine/v3.12/main/" > /etc/apk/repositories && \
    echo "https://mirrors.aliyun.com/alpine/v3.12/community/" >> /etc/apk/repositories && \
    apk update && \
    apk add --no-cache bash && \
    apk add --no-cache py3-pip python3 python3-dev && \
    apk add --no-cache libxml2-dev libxslt-dev libffi-dev gcc musl-dev libgcc openssl-dev curl && \
    apk add --no-cache jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev && \   
    rm -rf /var/cache/apk/* && \
    mkdir -p /data/XueQG/Config 
    
COPY Config/Config.cfg /data/XueQG/Config/Config.cfg
COPY answers /data/XueQG/answers
COPY func /data/XueQG/func
COPY study /data/XueQG/study
COPY XueQG.py /data/XueQG/XueQG.py
COPY requirements.txt /data/XueQG/requirements.txt

ENV LIBRARY_PATH=/lib:/usr/lib

RUN cd /data/XueQG && \
    pip3 install -r requirements.txt && \
    pyinstaller -F XueQG.py

FROM alpine:3.12
ENV TZ Asia/Shanghai
ENV LC_ALL=zh_CN.UTF-8  

RUN echo "https://mirrors.aliyun.com/alpine/v3.12/main/" > /etc/apk/repositories && \
    echo "https://mirrors.aliyun.com/alpine/v3.12/community/" >> /etc/apk/repositories && \
    apk update && \
    apk add --no-cache tzdata && cp /usr/share/zoneinfo/${TZ} /etc/localtime && echo ${TZ} > /etc/timezone && \
    apk add --no-cache ttf-dejavu fontconfig && mkfontscale && mkfontdir && fc-cache && \    
    apk add --no-cache zbar && \
    apk add --no-cache chromium && \
    apk add --no-cache chromium-chromedriver && \
    sed -i "s/\$cdc_/\$abc_/" /usr/lib/chromium/chromedriver && \
    rm -rf /var/cache/apk/* && \
    mkdir -p /data/XueQG/Config && \
    cd /data/XueQG

COPY Config/Config.cfg /data/XueQG/Config/Config.cfg
COPY --from=builder /data/XueQG/dist/XueQG /data/XueQG/XueQG

WORKDIR /data/XueQG
ENTRYPOINT ["./XueQG"]
