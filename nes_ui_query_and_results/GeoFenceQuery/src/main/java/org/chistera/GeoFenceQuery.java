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
        int exited;
    }

    static class GeoFence implements MapFunction<GPS_PositionInput, GPS_PositionOutput> {

        private final Path2D.Double field;

        public GeoFence() {
            this.field = new Path2D.Double();
            field.moveTo(3.4336703724841016, 46.3394657872912);
            field.lineTo(3.4331587059786557, 46.339320865456926);
            field.lineTo(3.4332505435561984, 46.338890626499165);
            field.lineTo(3.4339852441797802, 46.33917141441313);
            field.closePath();
        }

        @Override
        public GPS_PositionOutput map(final GPS_PositionInput input) {
            GPS_PositionOutput output = new GPS_PositionOutput();
            output.timestamp = input.timestamp;
            output.robot_id = input.robot_id;
            boolean isInside = this.field.contains(input.position_x, input.position_y);
            output.exited = (isInside) ? 0 : 1;
            return output;
        }
    }

    public static void main(String[] args) throws IOException, RESTException, InterruptedException {

        NebulaStreamRuntime nebulaStreamRuntime = NebulaStreamRuntime.getRuntime("192.168.0.151", 8081);
        Query query = nebulaStreamRuntime.readFromSource("gps_position");
        query.map(new GeoFence());
        query.window(TumblingWindow.of(eventTime("timestamp"), seconds(1))).byKey("robot_id").apply(sum("exited"));
        query.filter(attribute("exited").greaterThan(0));
        query.sink(new MQTTSink("ws://192.168.0.151:9001", "query_1a", "user", 1000, MQTTSink.TimeUnits.milliseconds, 0, MQTTSink.ServiceQualities.atLeastOnce, true));
        int queryId = nebulaStreamRuntime.executeQuery(query, "BottomUp");
    }
}
