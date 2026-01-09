package org.chistera;

import org.locationtech.jts.io.ParseException;
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
import static stream.nebula.operators.Aggregation.sum;
import static stream.nebula.operators.window.Duration.seconds;
import static stream.nebula.operators.window.EventTime.eventTime;

public class HumidityQuery {

    // static class GPS_PositionInput {
    //     long timestamp;
    //     String robot_name;
    //     double position_x;
    //     double position_y;
    // }

    // static class GPS_PositionOutput {
    //     long timestamp;
    //     int robot_id;
    //     double position_x;
    //     double position_y;
    //     int exited;
    // }

    // static class GeoFence implements MapFunction<GPS_PositionInput, GPS_PositionOutput> {
    //     private final Path2D.Double field;

    //     public GeoFence(Path2D.Double field) {
    //         this.field = field;
    //     }

    //     @Override
    //     public GPS_PositionOutput map(final GPS_PositionInput input) {
    //         GPS_PositionOutput output = new GPS_PositionOutput();
    //         output.timestamp = input.timestamp;
    //         if (input.robot_name.equals("leader")) {
    //             output.robot_id = 0;
    //         } else {
    //             output.robot_id = 1;
    //         }
    //         output.position_x = input.position_x;
    //         output.position_y = input.position_y;
            
    //         output.exited = this.field.contains(input.position_x, input.position_y) ? 0 : 1;
    //         return output;
    //     }
    // }

    public static void main(String[] args) {
        try {
            String queryName = args[0];

            // File fieldFile = new File(filePath);

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

            // Path2D.Double fieldShape = GeoUtils.loadFieldShape(filePath);

            NebulaStreamRuntime nebulaStreamRuntime = NebulaStreamRuntime.getRuntime(nesIp, nesPort);
            Query query = nebulaStreamRuntime.readFromSource("gps_position")
                .map("joinKey", literal(1))
                .joinWith(nebulaStreamRuntime.readFromSource("soil_humidity")
                        .map("joinKey", literal(1)))
                .where(attribute("joinKey").equalTo(attribute("joinKey")));
            
            // query.map(new GeoFence(fieldShape));
            
            // query.window(TumblingWindow.of(eventTime("timestamp"), seconds(1)))
            //      .byKey("robot_id")
            //      .apply(sum("exited"));
            
            // query.filter(attribute("exited").greaterThan(0));
            
            query.sink(new MQTTSink(mqttUrl, queryName, "user", 1000, 
                        MQTTSink.TimeUnits.milliseconds, 0, 
                        MQTTSink.ServiceQualities.atLeastOnce, true));
            
            int queryId = nebulaStreamRuntime.executeQuery(query, "BottomUp");
            System.out.println("Query started with ID: " + queryId);

        } catch (IOException e) {
            e.printStackTrace();
            System.exit(1);
        } catch (ParseException e) {
            e.printStackTrace();
            System.exit(1);
        } catch (Throwable t) {
            t.printStackTrace();
            System.exit(1);
        }
    }
}
