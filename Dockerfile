FROM willhallonline/ansible:2.9-centos
LABEL maintainer="Kien Nguyen-Tuan <kiennt2609@gmail.com>"
COPY etc/ansible.example.cfg /etc/ansible/ansible.cfg
RUN mkdir -p /opt/ansitheus
COPY . /opt/ansitheus
WORKDIR /opt/ansitheus
RUN pip install -r requirements.txt
ENTRYPOINT ["./tools/ansitheus"]
