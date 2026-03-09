FROM willhallonline/ansible:2.17-ubuntu-24.04
LABEL maintainer="Kien Nguyen-Tuan <kiennt2609@gmail.com>"
# Enable Mitogen to boostup performance
ENV ANSIBLE_STRATEGY_PLUGINS=/usr/local/lib/python3.12/dist-packages/ansible_mitogen/plugins/strategy
ENV ANSIBLE_STRATEGY=mitogen_linear
ENV ANSIBLE_CALLBACK_PLUGINS=/root/.local/share/pipx/venvs/ansible-core/lib/python3.12/site-packages/ara/plugins/callback
ENV ANSIBLE_ACTION_PLUGINS=/root/.local/share/pipx/venvs/ansible-core/lib/python3.12/site-packages/ara/plugins/action
ENV ANSIBLE_LOOKUP_PLUGINS=/root/.local/share/pipx/venvs/ansible-core/lib/python3.12/site-packages/ara/plugins/lookup
COPY etc/ansible.example.cfg /etc/ansible/ansible.cfg
COPY . /opt/ansitheus
WORKDIR /opt/ansitheus
RUN apt-get update && apt-get install -y sudo \
    && rm -rf /var/lib/apt/lists/*
RUN ansible-galaxy install -r requirements.yml
RUN pipx inject ansible-core ara>=1.7.2 jmespath
# Mitogen needs sudo command to execute
ENTRYPOINT ["/opt/ansitheus/tools/ansitheus"]
