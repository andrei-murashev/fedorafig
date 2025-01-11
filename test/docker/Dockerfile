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
COPY test/cfgs/cfg2/. $FEDORAFIG_CFG_PATH
RUN export PATH="/usr/local/bin:$PATH"
RUN cd fedorafig && chmod u+x install.sh && ./install.sh
RUN rm -rf fedorafig
COPY test/docker/test_base.sh $FEDORAFIG_PROG_PATH

# Run tests
RUN chown -R $USER:$USER $HOME
USER user
CMD ["bash", "-c", "echo 'sudo' | sudo -S -v && sudo fedorafig run cfg.json5 -rn && sudo dnf install -y cmatrix && fedorafig base -c ok.txt && sudo dnf install neofetch -y && sudo dnf remove -y cmatrix && echo '==== BASE RESTORE ====' && sudo fedorafig base -r ok.txt"]
