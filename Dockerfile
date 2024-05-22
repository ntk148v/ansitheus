FROM cytopia/ansible:2.10-infra
LABEL maintainer="Kien Nguyen-Tuan <kiennt2609@gmail.com>"
# Enable Mitogen to boostup performance
ENV ANSIBLE_STRATEGY_PLUGINS=/usr/lib/python3.10/site-packages/ansible_mitogen/plugins/strategy
ENV ANSIBLE_STRATEGY=mitogen_linear
COPY etc/ansible.example.cfg /etc/ansible/ansible.cfg
COPY . /opt/ansitheus
WORKDIR /opt/ansitheus
RUN ansible-galaxy install -r requirements.yml
# Mitogen needs sudo command to execute 
RUN apk add --no-cache sudo
ENTRYPOINT ["/opt/ansitheus/tools/ansitheus"]
