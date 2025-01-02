FROM fedora:40

# Installing required packages.
RUN dnf install -y \
  dnf-plugins-core \
  python3-pip \
  python3 \
  ncurses \
  neovim \
  tree \
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

# Install fedorafig
RUN pip install json5
COPY . $HOME/fedorafig
COPY test/cfgs/cfg2/. $FEDORAFIG_CFG_PATH
RUN export PATH="/usr/local/bin:$PATH"
RUN cd fedorafig && chmod u+x install.sh && ./install.sh
RUN rm -rf fedorafig

# Run tests
USER user
CMD ["bash"]
