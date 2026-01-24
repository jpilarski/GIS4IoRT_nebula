docker compose pull
docker compose build

# GEOFENCE - 3 razy

docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up ros2_mqtt_leader -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up geofence_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up ros2_mqtt_leader -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up geofence_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up ros2_mqtt_leader -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up geofence_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


# HUMIDITY - 3 razy

docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up mosquitto_humidity -d
sleep 3
docker compose up ros2_mqtt_leader -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up nes_worker_humidity -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up humidity_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader -d
docker compose up humidity_producer -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up mosquitto_humidity -d
sleep 3
docker compose up ros2_mqtt_leader -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up nes_worker_humidity -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up humidity_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader -d
docker compose up humidity_producer -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up mosquitto_humidity -d
sleep 3
docker compose up ros2_mqtt_leader -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up nes_worker_humidity -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up humidity_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader -d
docker compose up humidity_producer -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


# COLLISION - 3 razy

docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader_inv -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up ros2_mqtt_leader_inv -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader_inv -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up collision_query -d
sleep 10
docker compose up collision_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader_inv -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader_inv -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up ros2_mqtt_leader_inv -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader_inv -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up collision_query -d
sleep 10
docker compose up collision_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader_inv -d
docker compose up ros2_play_follower
sleep 5
docker compose down
sleep 5


docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader_inv -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up ros2_mqtt_leader_inv -d
sleep 3
docker compose up ros2_mqtt_follower -d
sleep 3
docker compose up nes_worker_leader_inv -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up collision_query -d
sleep 10
docker compose up collision_query -d
sleep 3
docker compose up subscriber -d
sleep 3
docker compose up ros2_play_leader_inv -d
docker compose up ros2_play_follower
sleep 5
docker compose down