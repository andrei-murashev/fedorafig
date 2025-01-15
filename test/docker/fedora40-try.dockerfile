FROM fedora40-setup
COPY ./test/demo-cfg/. $HOME/.config/fedorafig
CMD ["bash"]
