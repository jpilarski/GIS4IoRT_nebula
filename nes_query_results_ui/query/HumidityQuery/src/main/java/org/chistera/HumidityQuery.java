package org.chistera;

import stream.nebula.operators.sinks.MQTTSink;
import stream.nebula.operators.window.TumblingWindow;
import stream.nebula.runtime.NebulaStreamRuntime;
import stream.nebula.runtime.Query;
import stream.nebula.udf.MapFunction;

import java.io.File;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

import static stream.nebula.expression.Expressions.attribute;
import static stream.nebula.expression.Expressions.literal;
import static stream.nebula.operators.Aggregation.average;
import static stream.nebula.operators.Aggregation.max;
import static stream.nebula.operators.Aggregation.sum;
import static stream.nebula.operators.window.Duration.seconds;
import static stream.nebula.operators.window.EventTime.eventTime;

public class HumidityQuery {

    static class GPS_PositionInput {
        long timestamp;
        String robot_name;
        double position_x;
        double position_y;
    }

    static class GPS_PositionOutput {
        long timestamp;
        long robot_id;
        double position_x;
        double position_y;
    }

    static class NameToId implements MapFunction<GPS_PositionInput, GPS_PositionOutput> {

        @Override
        public GPS_PositionOutput map(final GPS_PositionInput input) {
            GPS_PositionOutput output = new GPS_PositionOutput();
            output.timestamp = input.timestamp;
            if (input.robot_name.equals("leader")) {
                output.robot_id = 0;
            } else {
                output.robot_id = 1;
            }
            output.position_x = input.position_x;
            output.position_y = input.position_y;
            return output;
        }
    }

    static class JoinInput {
        long gps_position$end;
        long gps_position$joinKey;
        double gps_position$position_x;
        double gps_position$position_y;
        long gps_position$robot_id;
        long gps_position$start;
        long gps_positionsoil_humidity$end;
        long gps_positionsoil_humidity$start;
        long soil_humidity$end;
        double soil_humidity$humidity;
        long soil_humidity$joinKey;
        double soil_humidity$position_x;
        double soil_humidity$position_y;
        long soil_humidity$sensor_id;
        long soil_humidity$start;
    }

    static class JoinOutput {
        long start;
        long end;
        long robot_id;
        double robot_position_x;
        double robot_position_y;
        long sensor_id;
        double sensor_position_x;
        double sensor_position_y;
        double humidity;
        double distance;
    }

    static class CalculateDistance implements MapFunction<JoinInput, JoinOutput> {

        private double calculateDistanceInMeters(double lat1, double lon1, double lat2, double lon2) {
            final int R = 6371000;
            double latDistance = Math.toRadians(lat2 - lat1);
            double lonDistance = Math.toRadians(lon2 - lon1);
            double a = Math.sin(latDistance / 2) * Math.sin(latDistance / 2)
                    + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                    * Math.sin(lonDistance / 2) * Math.sin(lonDistance / 2);
            double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c;
        }

        @Override
        public JoinOutput map(final JoinInput input) {
            JoinOutput output = new JoinOutput();
            output.start = input.gps_position$start;
            output.end = input.gps_position$end;
            output.robot_id = input.gps_position$robot_id;
            output.robot_position_x = input.gps_position$position_x;
            output.robot_position_y = input.gps_position$position_y;
            output.sensor_id = input.soil_humidity$sensor_id;
            output.sensor_position_x = input.soil_humidity$position_x;
            output.sensor_position_y = input.soil_humidity$position_y;
            output.humidity = input.soil_humidity$humidity;
            output.distance = calculateDistanceInMeters(
                input.gps_position$position_y, input.gps_position$position_x,
                input.soil_humidity$position_y, input.soil_humidity$position_x
            );
            return output;
        }
    }


    public static void main(String[] args) {
        try {
            String queryName = args[0];

            String nesIp = System.getenv("NES_COORDINATOR_IP");
            String nesPortStr = System.getenv("NES_COORDINATOR_REST_PORT");
            String mqttIp = System.getenv("QUERY_HOST_IP");
            String mqttPortStr = System.getenv("QUERY_HOST_MQTT_PORT");
            String humThresholdStr = System.getenv("HUMIDITY_THRESHOLD");
            String bufferRadiusStr = System.getenv("BUFFER_RADIUS");

            int nesPort = Integer.parseInt(nesPortStr);
            double humThreshold = Double.parseDouble(humThresholdStr);
            double bufferRadius = Double.parseDouble(bufferRadiusStr);
            String mqttUrl = "ws://" + mqttIp + ":" + mqttPortStr;

            NebulaStreamRuntime nebulaStreamRuntime = NebulaStreamRuntime.getRuntime(nesIp, nesPort);
            Query q1 = nebulaStreamRuntime.readFromSource("gps_position")
                .map(new NameToId())
                .window(TumblingWindow.of(eventTime("timestamp"), seconds(1)))
                .byKey("robot_id")
                .apply(average("position_x"), average("position_y"))
                .map("joinKey", literal(1));
            Query q2 = nebulaStreamRuntime.readFromSource("soil_humidity")
                .window(TumblingWindow.of(eventTime("timestamp"), seconds(1)))
                .byKey("sensor_id")
                .apply(average("position_x"), average("position_y"), max("humidity"))
                .map("joinKey", literal(1));
            Query finalQuery = q1.joinWith(q2)
                .where(attribute("joinKey").equalTo(attribute("joinKey")))
                .window(TumblingWindow.of(eventTime("start"), seconds(1)))
                .map(new CalculateDistance())
                .filter(attribute("distance").lessThanOrEqual(bufferRadius))
                .filter(attribute("humidity").greaterThan(humThreshold));
            
            
            finalQuery.sink(new MQTTSink(mqttUrl, queryName, "user", 1000, 
                        MQTTSink.TimeUnits.milliseconds, 0, 
                        MQTTSink.ServiceQualities.atLeastOnce, true));
            
            int queryId = nebulaStreamRuntime.executeQuery(finalQuery, "BottomUp");
            System.out.println("Query started with ID: " + queryId);

        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        } catch (Throwable t) {
            t.printStackTrace();
            System.exit(1);
        }
    }
}
