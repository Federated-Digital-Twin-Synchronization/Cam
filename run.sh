#!/bin/bash

# Pull the Docker image
echo "=> Pull image..."
docker pull hyeongjunjoo/pose3d-orin-realsense:v4

# Run the Docker container
echo "=> Run image..."
docker run --privileged --runtime nvidia -itd --network host --name pose3d-orin-realsense --volume /tmp/argus_socket:/tmp/argus_socket --volume /etc/enctune.conf:/etc/enctune.conf --volume /etc/nv_tegra_release:/etc/nv_tegra_release -v /dev:/dev -e DISPLAY=$DISPLAY -v /tmp/.X11-unix/:/tmp/.X11-unix -e XAUTHORITY=/tmp/.docker.xauth hyeongjunjoo/pose3d-orin-realsense:v4
