FROM fedora:40

# Installing required packages.
RUN dnf install -y    \
  python3-pip python3 \
  dnf-plugins-core    \
  ncurses tree        \
  neovim git

# Creates a typical user environment
RUN useradd -m user             
RUN echo 'user:sudo' | chpasswd
RUN usermod -aG wheel user

WORKDIR /home/user
ENV USER=user
ENV HOME=/home/user
ENV PATH=/usr/local/bin:$PATH
ENV FEDORAFIG_CFG_PATH=/home/user/.config/fedorafig
ENV FEDORAFIG_PROG_PATH=/home/user/.local/lib/fedorafig

# Install fedorafig
# TODO: Build binary on system
RUN pip install json5
RUN rm -rf /var/cache/dnf/*
COPY . $HOME/fedorafig
RUN export PATH="/usr/local/bin:$PATH"
RUN cd fedorafig && chmod u+x install.sh && ./install.sh
RUN rm -rf fedorafig
COPY ./test/test-cfgs/. $FEDORAFIG_CFG_PATH

# Final environment setup
RUN echo 'ALL ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers
RUN chown -R $USER:$USER $HOME
USER user
CMD ["bash", "-c", "exit"]
