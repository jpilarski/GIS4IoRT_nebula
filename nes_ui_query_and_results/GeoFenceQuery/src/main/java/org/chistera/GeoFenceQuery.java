package org.chistera;

import stream.nebula.exceptions.RESTException;
import stream.nebula.operators.sinks.MQTTSink;
import stream.nebula.operators.window.TumblingWindow;
import stream.nebula.runtime.NebulaStreamRuntime;
import stream.nebula.runtime.Query;
import stream.nebula.udf.MapFunction;

import java.awt.geom.Path2D;
import java.io.IOException;

import static stream.nebula.expression.Expressions.attribute;
import static stream.nebula.operators.Aggregation.sum;
import static stream.nebula.operators.window.Duration.seconds;
import static stream.nebula.operators.window.EventTime.eventTime;

public class GeoFenceQuery {

    static class GPS_PositionInput {
        long timestamp;
        long robot_id;
        double position_x;
        double position_y;
    }

    static class GPS_PositionOutput {
        long timestamp;
        long robot_id;
        double position_x;
        double position_y;
        int exited;
    }

    static class GeoFence implements MapFunction<GPS_PositionInput, GPS_PositionOutput> {
        private final Path2D.Double field;

        public GeoFence(Path2D.Double field) {
            this.field = field;
        }

        @Override
        public GPS_PositionOutput map(final GPS_PositionInput input) {
            GPS_PositionOutput output = new GPS_PositionOutput();
            output.timestamp = input.timestamp;
            output.robot_id = input.robot_id;
            output.position_x = input.position_x;
            output.position_y = input.position_y;
            boolean isInside = this.field.contains(input.position_x, input.position_y);
            output.exited = (isInside) ? 0 : 1;
            return output;
        }
    }

    public static void main(String[] args) {
        if (args.length < 3 || (!"continuous".equalsIgnoreCase(args[0]) && !"historical".equalsIgnoreCase(args[0]))) {
            System.out.println("Skipping execution. First argument must be 'continuous' or 'historical'.");
            return;
        }

        String csvPath = args[1];
        String queryName = args[2];

        String nesIp = System.getenv("NES_COORDINATOR_IP");
        String nesPortStr = System.getenv("NES_COORDINATOR_REST_PORT");
        String mqttIp = System.getenv("QUERY_HOST_IP");
        String mqttPortStr = System.getenv("QUERY_HOST_MQTT_PORT");

        if (nesIp == null || nesPortStr == null || mqttIp == null || mqttPortStr == null) {
            System.err.println("Missing ENV variables. Check .env file.");
            System.exit(1);
        }

        int nesPort = Integer.parseInt(nesPortStr);
        String mqttUrl = "ws://" + mqttIp + ":" + mqttPortStr;

        try {
            System.out.println("Loading field shape from: " + csvPath);
            Path2D.Double fieldShape = GeoUtils.loadFieldShape(csvPath);

            NebulaStreamRuntime nebulaStreamRuntime = NebulaStreamRuntime.getRuntime(nesIp, nesPort);
            Query query = nebulaStreamRuntime.readFromSource("gps_position");
            
            query.map(new GeoFence(fieldShape));

            if("continuous".equalsIgnoreCase(args[0])) {
                query.window(TumblingWindow.of(eventTime("timestamp"), seconds(1)))
                     .byKey("robot_id")
                     .apply(sum("exited"));
            }
            
            query.filter(attribute("exited").greaterThan(0));
            
            query.sink(new MQTTSink(mqttUrl, queryName, "user", 1000, 
                       MQTTSink.TimeUnits.milliseconds, 0, 
                       MQTTSink.ServiceQualities.atLeastOnce, true));
            
            int queryId = nebulaStreamRuntime.executeQuery(query, "BottomUp");
            System.out.println("Query started with ID: " + queryId);
            if("historical".equalsIgnoreCase(args[0])) {
                Thread.sleep(60000);
                nebulaStreamRuntime.stopQuery(queryId);
            }

        } catch (IOException | RESTException | InterruptedException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}