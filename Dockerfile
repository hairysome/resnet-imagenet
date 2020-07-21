FROM bentoml/model-server:0.8.3

# copy over model files
COPY . /bento
WORKDIR /bento

# Configuring PyPI index
ARG PIP_INDEX_URL=https://pypi.python.org/simple/
ARG PIP_TRUSTED_HOST=pypi.python.org
ENV PIP_INDEX_URL $PIP_INDEX_URL
ENV PIP_TRUSTED_HOST $PIP_TRUSTED_HOST

# Execute permission for bentoml-init.sh
RUN chmod +x /bento/bentoml-init.sh

# Install conda, pip dependencies and run user defined setup script
RUN if [ -f /bento/bentoml-init.sh ]; then bash -c /bento/bentoml-init.sh; fi

# the env var $PORT is required by heroku container runtime
ENV PORT 5000
EXPOSE $PORT

COPY docker-entrypoint.sh /usr/local/bin/

# Execute permission for docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT [ "docker-entrypoint.sh" ]
CMD ["bentoml", "serve-gunicorn", "/bento"]
