FROM willhallonline/ansible:2.9-centos
LABEL maintainer="Kien Nguyen-Tuan <kiennt2609@gmail.com>"
COPY etc/ansible.example.cfg /etc/ansible/ansible.cfg
RUN mkdir -p /opt/ansible-monitoring
COPY . /opt/ansible-monitoring
WORKDIR /opt/ansible-monitoring
RUN pip install -r requirements.txt
ENTRYPOINT ["./tools/ansible-monitoring"]
