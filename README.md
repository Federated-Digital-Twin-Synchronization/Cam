# Cam
Human_pose_estimation

# Docker pull and run
```
# ADD, --volume /your/path:/Realtime_3d_pose_estimation
./run.sh
```
```
xhost +local:docker
```
# run Camera RTSP server
## Realsense L515
### terminal 1 (docker container)
```
cd /pose3d
python stream.py --fps 30 --port 8554 --stream_uri /video_stream
```

# PoseNet demo
## terminal 2 (docker container)
```
cd /pose3d/Realtime_3d_pose_estimation/demo/
python demo_3dpose.py --gpu 0 --test_epoch 18 --test_epoch2 24
```

# Yolov8 tracking
## terminal 3 (docker container)
```
cd /pose3d/Realtime_3d_pose_estimation/yolov8_tracking
python track.py --source 'rtsp://127.0.0.1:8554/video_stream' --classes 0 --device 0 --tracking-method botsort
```
