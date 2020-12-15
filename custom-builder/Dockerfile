FROM gcr.io/cloud-builders/kubectl

RUN curl -L https://k14s.io/install.sh | bash
RUN curl -L https://github.com/knative/client/releases/download/v0.19.1/kn-linux-amd64 --output /usr/local/sbin/kn &&\
  chmod +x /usr/local/sbin/kn
