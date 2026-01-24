docker compose up nes_coordinator -d
sleep 3
docker compose up nes_ui -d
sleep 3
docker compose up mosquitto_leader -d
sleep 3
docker compose up mosquitto_follower -d
sleep 3
docker compose up nes_worker_leader -d
sleep 3
docker compose up nes_worker_follower -d
sleep 3
docker compose up mosquitto_results -d
sleep 3
docker compose up collision_query -d
sleep 10
docker compose up collision_query -d
sleep 3
docker compose up subscriber