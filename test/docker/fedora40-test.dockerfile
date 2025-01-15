FROM fedora40-setup
COPY ./test/docker/test.sh $HOME
RUN sudo chown $USER:$USER $HOME/test.sh
CMD ["bash", "-c", "chmod u+x test.sh; ./test.sh"]
