#!/bin/bash

sleep 10

curl -X POST http://coordinator:8081/v1/nes/query/execute-query \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{"userQuery": "Query::from(\"gps_position\").window(TumblingWindow::of(EventTime(Attribute(\"timestamp\")), Seconds(1))).byKey(Attribute(\"robot_id\")).apply(Count()).sink(MQTTSinkDescriptor::create(\"ws://mosquitto:9001\", \"window-results\"));", "placement": "BottomUp"}'
