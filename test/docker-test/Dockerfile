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
ARG CACHE_BUST=0
RUN git clone https://github.com/amura-dev/fedorafig -b dev --verbose
RUN cd fedorafig && chmod u+x install.sh && ./install.sh
RUN rm -rf fedorafig

#COPY test/files .config/fedorafig
#COPY src bin/fedorafig-src
#RUN \
#  echo 'sudo' | sudo -S chown -R user:user "$HOME"                && \
#  chmod u+x bin/fedorafig-src/main.py                             && \
#  ln -s "$HOME"/bin/fedorafig-src/main.py "$HOME"/bin/fedorafig   && \
#  chmod u+x bin/fedorafig-src/test.sh

# Runs tests.
# CMD ["/home/user/bin/fedorafig-src/test.sh"]
CMD ["bash"]
