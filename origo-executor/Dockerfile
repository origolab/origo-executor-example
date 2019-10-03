FROM ubuntu:18.04

# Modified from Zokrates Dockerfile

RUN adduser --disabled-password --gecos '' --shell /bin/bash origo
RUN adduser origo sudo
RUN echo 'origo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

ARG RUST_TOOLCHAIN=nightly-2018-06-04
ARG LIBSNARK_COMMIT=f7c87b88744ecfd008126d415494d9b34c4c1b20
ENV LIBSNARK_SOURCE_PATH=/home/origo/libsnark-$LIBSNARK_COMMIT
ENV WITH_LIBSNARK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    cmake \
    curl \
    libboost-dev \
    libboost-program-options-dev \
    libgmp3-dev \
    libprocps-dev \
    libssl-dev \
    pkg-config \
    python-markdown \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    iputils-ping \
    vim \
    git \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && git clone https://github.com/scipr-lab/libsnark.git $LIBSNARK_SOURCE_PATH \
    && git -C $LIBSNARK_SOURCE_PATH checkout $LIBSNARK_COMMIT \
    && git -C $LIBSNARK_SOURCE_PATH submodule update --init --recursive \
    && chown -R origo:origo $LIBSNARK_SOURCE_PATH

ENV HOME=/home/origo
WORKDIR $HOME

ENV ZOKRATES_HOME=$HOME/Zokrates
RUN git clone https://github.com/Zokrates/ZoKrates.git $ZOKRATES_HOME && \
    cd $ZOKRATES_HOME && \
    git checkout e2acdbff378ace4667933c356de9573e4e576057 && \
    cd $HOME && \
    mv $ZOKRATES_HOME src

RUN curl https://sh.rustup.rs -sSf | sh -s -- --default-toolchain $RUST_TOOLCHAIN -y \
    && export PATH=/home/origo/.cargo/bin:$PATH \
    && (cd src;./build_release.sh) \
    && mv ./src/target/release/zokrates . \
    && mv ./src/zokrates_cli/examples . \
    && rustup self uninstall -y \
    && rm -rf $LIBSNARK_SOURCE_PATH src

ENV EXECUTOR_ROOT=/home/origo-executor
ENV PYTHONPATH=$EXECUTOR_ROOT
COPY --chown=origo:origo ./executor ${EXECUTOR_ROOT}/executor
COPY --chown=origo:origo ./executor_service ${EXECUTOR_ROOT}/executor_service
COPY --chown=origo:origo ./requirements.txt ${EXECUTOR_ROOT}/
COPY --chown=origo:origo ./setup.py ${EXECUTOR_ROOT}/
COPY --chown=origo:origo ./tmp/private.pem ${EXECUTOR_ROOT}/tmp/private.pem

RUN pip3 install -r ${EXECUTOR_ROOT}/requirements.txt

WORKDIR $EXECUTOR_ROOT
RUN python3 ${EXECUTOR_ROOT}/setup.py build_ext --inplace
RUN mv ${EXECUTOR_ROOT}/executor_service/run_executor_service.py ${EXECUTOR_ROOT} \
    && mv ${EXECUTOR_ROOT}/executor/constants ${EXECUTOR_ROOT} \
    && rm ${EXECUTOR_ROOT}/executor_service/*.py \
    && rm ${EXECUTOR_ROOT}/executor_service/*.c \
    && rm ${EXECUTOR_ROOT}/executor/*.py \
    && rm ${EXECUTOR_ROOT}/executor/*.c \
    && rm ${EXECUTOR_ROOT}/executor/*/*.py \
    && rm ${EXECUTOR_ROOT}/executor/*/*.c \
    && rm ${EXECUTOR_ROOT}/executor/*/*/*.py \
    && rm ${EXECUTOR_ROOT}/executor/*/*/*.c \
    && rm ${EXECUTOR_ROOT}/requirements.txt \
    && rm ${EXECUTOR_ROOT}/setup.py \
    && rm -rf ${EXECUTOR_ROOT}/build \
    && mv ${EXECUTOR_ROOT}/run_executor_service.py ${EXECUTOR_ROOT}/executor_service/ \
    && mv ${EXECUTOR_ROOT}/constants ${EXECUTOR_ROOT}/executor/
