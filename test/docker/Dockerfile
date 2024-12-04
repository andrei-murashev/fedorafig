FROM fedora:41

# Installing required packages.
RUN \
  dnf install -y \
  python3 \
  neovim \
  ncurses \
  git

# Creates a typical user scenario.
RUN \
  useradd -m user             && \
  echo 'user:sudo' | chpasswd && \
  usermod -aG wheel user
USER user
WORKDIR /home/user
ENV USER=user
ENV HOME=/home/user
# ENV FEDORAFIG_SRC_PATH=/home/user/bin/fedorafig-src
# ENV FEDORAFIG_CFG_PATH=/home/user/.config/fedorafig


# Install `fedorafig`
COPY . $HOME/fedorafig
RUN echo 'sudo' | sudo -S chown -R user:user $HOME
RUN cd fedorafig && chmod u+x install.sh && ./install.sh
RUN rm -rf fedorafig

# Runs tests.
# CMD ["/home/user/bin/fedorafig-src/test.sh"]
CMD ["bash"]
