FROM willhallonline/ansible:2.16.4-bookworm
LABEL maintainer="Kien Nguyen-Tuan <kiennt2609@gmail.com>"
COPY etc/ansible.example.cfg /etc/ansible/ansible.cfg
RUN mkdir -p /opt/ansitheus
COPY . /opt/ansitheus
WORKDIR /opt/ansitheus
RUN pip install -r requirements.txt && \
    ansible-galaxy install -r requirements.yml
ENTRYPOINT ["/opt/ansitheus/tools/ansitheus"]
