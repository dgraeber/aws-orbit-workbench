FROM ${jupyter_user_base}
#FROM 495869084367.dkr.ecr.us-west-2.amazonaws.com/orbit-test-env-public-jupyter-user:latest

USER root
######################################
# Apps installation
######################################
RUN mkdir -p /home/jovyan/.orbit
COPY apps /home/jovyan/.orbit/apps
RUN ls -R /home/jovyan/.orbit/apps
RUN chmod -R a+xr /home/jovyan/.orbit/apps/*.sh
RUN /home/jovyan/.orbit/apps/install-all.sh
RUN chown -R jovyan /home/jovyan


USER $NB_UID

#RUN fix-permissions /opt/install

# apt-get may result in root-owned directories/files under $HOME
RUN chown -R $NB_UID:$NB_GID $HOME
RUN fix-permissions /home/jovyan/