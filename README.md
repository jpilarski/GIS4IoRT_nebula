# NebulaStream for GIS4IoRT Chist-Era project

### Usage:

1. Clone repository:
    ```
    git clone https://github.com/jpilarski/GIS4IoRT_nebula
    cd GIS4IoRT_nebula
    ```

2. In `/nes_coordinator` folder (on machine 1):
    * Update the `NES_COORDINATOR_IP` in the `.env` file
    * Run `docker compose pull` and `docker compose up`

3. In `/ros2_mqtt_bridge` folder (on machine 2):
    * _Change the `MQTT_IP` (not necessary)_
    * Change the `ROBOT_NAME`, `ROS2_TOPIC` and `MQTT_TOPIC`, select between `leader` and `follower`
    * Run `docker compose pull` and `docker compose build`
    * Run `docker compose up mosquitto -d` and `docker compose up ros2_mqtt -d`
    * Run `docker compose up ros2_play` (after setting the worker as in point 4. and preferrably after submitting the query as in point 6.)

4. In `/nes_worker` folder (on machine 2):
    * In `config\nes_worker_config.yml` update the `coordinatorHost` to match `NES_COORDINATOR_IP` from point 1., update the `localWorkerHost` and `workerId`, also update `physicalSourceName` and `topic` to match `ROBOT_NAME` and `MQTT_TOPIC` (point 3.) and uptade `url`, if changed `MQTT_IP` in point 3.
    * Run `docker compose pull` and `docker compose up`

5. Repeat steps 3-4 for each robot and worker on another machine

6. In folder `/nes_query_results_ui` (on machine 1 or another than with worker):
    * Update the `NES_COORDINATOR_IP` in the `.env` file to match `NES_COORDINATOR_IP` from point 2.
    * Update the `QUERY_HOST_IP` and `QUERY_NAME`
    * Run `docker compose pull` and `docker compose build`
    * Run `docker compose up mosquitto -d` and `docker compose up nes_ui -d` and `docker compose up subscriber`
    * Open NES UI (port 9000) and type in `NES_COORDINATOR_IP:8081`
