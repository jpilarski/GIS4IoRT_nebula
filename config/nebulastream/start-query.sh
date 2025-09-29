#!/bin/bash

sleep 10

# WINDOW DEMO
curl -X POST http://coordinator:8081/v1/nes/query/execute-query \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{"userQuery": "Query::from(\"gps_position\").window(TumblingWindow::of(EventTime(Attribute(\"timestamp\")), Seconds(1))).byKey(Attribute(\"robot_id\")).apply(Count()).sink(MQTTSinkDescriptor::create(\"ws://mosquitto:9001\", \"window-demo\"));", "placement": "BottomUp"}'

sleep 2

# SIMPLE COPY
curl -X POST http://coordinator:8081/v1/nes/query/execute-query \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{"userQuery": "Query::from(\"gps_position\").sink(MQTTSinkDescriptor::create(\"ws://mosquitto:9001\", \"simple-copy\"));", "placement": "BottomUp"}'

sleep 2

# CIRCLE FILTER
curl -X POST http://coordinator:8081/v1/nes/query/execute-query \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{"userQuery": "Query::from(\"gps_position\").filter(((Attribute(\"position_x\")-40)*(Attribute(\"position_x\")-40)+Attribute(\"position_y\")*Attribute(\"position_y\")) <= 1600).sink(MQTTSinkDescriptor::create(\"ws://mosquitto:9001\", \"circle-filter\"));", "placement": "BottomUp"}'
