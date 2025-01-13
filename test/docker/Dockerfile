FROM fedora:40

# Installing required packages.
RUN dnf install -y \
  dnf-plugins-core \
  python3-pip \
  python3 \
  ncurses \
  neovim \
  tree \
  xsel \
  git

# Creates a typical user scenario.
RUN \
  useradd -m user             && \
  echo 'user:sudo' | chpasswd && \
  usermod -aG wheel user

WORKDIR /home/user
ENV USER=user
ENV HOME=/home/user
ENV PATH=/usr/local/bin:$PATH
ENV FEDORAFIG_CFG_PATH=/home/user/.config/fedorafig
ENV FEDORAFIG_PROG_PATH=/home/user/.local/lib/fedorafig

# Install fedorafig
RUN pip install json5
RUN rm -rf /var/cache/dnf/*
COPY . $HOME/fedorafig
COPY test/cfgs/demo-cfg/. $FEDORAFIG_CFG_PATH
RUN export PATH="/usr/local/bin:$PATH"
RUN cd fedorafig && chmod u+x install.sh && ./install.sh
RUN rm -rf fedorafig

# Run tests
RUN chown -R $USER:$USER $HOME
RUN echo 'ALL ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
USER user
CMD ["bash", "-c", "sudo fedorafig -v run -pn cfg.json5"]
