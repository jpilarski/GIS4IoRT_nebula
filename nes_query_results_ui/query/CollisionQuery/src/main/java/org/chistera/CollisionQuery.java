package org.chistera;

import stream.nebula.operators.sinks.MQTTSink;
import stream.nebula.operators.window.TumblingWindow;
import stream.nebula.runtime.NebulaStreamRuntime;
import stream.nebula.runtime.Query;
import stream.nebula.udf.MapFunction;

import java.io.IOException;

import static stream.nebula.expression.Expressions.attribute;
import static stream.nebula.expression.Expressions.literal;
import static stream.nebula.operators.Aggregation.average;
import static stream.nebula.operators.window.Duration.seconds;
import static stream.nebula.operators.window.EventTime.eventTime;

public class CollisionQuery {

    static class Name2IdInput {
        long timestamp;
        String robot_name;
        double position_x;
        double position_y;
    }

    static class Name2IdR1Output {
        long timestampR1;
        int robot_idR1;
        double position_xR1;
        double position_yR1;
    }

    static class Name2IdR2Output {
        long timestampR2;
        int robot_idR2;
        double position_xR2;
        double position_yR2;
    }

    static class Name2IdR1 implements MapFunction<Name2IdInput, Name2IdR1Output> {
        @Override
        public Name2IdR1Output map(final Name2IdInput input) {
            Name2IdR1Output output = new Name2IdR1Output();
            output.timestampR1 = input.timestamp;
            switch (input.robot_name) {
                case "leader":
                    output.robot_idR1 = 0;
                    break;
                case "follower":
                    output.robot_idR1 = 1;
                    break;
                case "leader_inv":
                    output.robot_idR1 = 2;
                    break;
                default:
                    output.robot_idR1 = 10;
                    break;
            }
            output.position_xR1 = input.position_x;
            output.position_yR1 = input.position_y;
            return output;
        }
    }

    static class Name2IdR2 implements MapFunction<Name2IdInput, Name2IdR2Output> {
        @Override
        public Name2IdR2Output map(final Name2IdInput input) {
            Name2IdR2Output output = new Name2IdR2Output();
            output.timestampR2 = input.timestamp;
            switch (input.robot_name) {
                case "leader":
                    output.robot_idR2 = 0;
                    break;
                case "follower":
                    output.robot_idR2 = 1;
                    break;
                case "leader_inv":
                    output.robot_idR2 = 2;
                    break;
                default:
                    output.robot_idR2 = 10;
                    break;
            }
            output.position_xR2 = input.position_x;
            output.position_yR2 = input.position_y;
            return output;
        }
    }

    static class Id2NameInput {
        long start;
        long end;
        int robot_idR1;
        double position_xR1;
        double position_yR1;
        int robot_idR2;
        double position_xR2;
        double position_yR2;
        double distance;
    }

    static class Id2NameOutput {
        long start;
        long end;
        String robot_nameR1;
        double position_xR1;
        double position_yR1;
        String robot_nameR2;
        double position_xR2;
        double position_yR2;
        double distance;
    }

    static class Id2Name implements MapFunction<Id2NameInput, Id2NameOutput> {
        @Override
        public Id2NameOutput map(final Id2NameInput input) {
            Id2NameOutput output = new Id2NameOutput();
            output.start = input.start;
            output.end = input.end;
            switch (input.robot_idR1) {
                case 0:
                    output.robot_nameR1 = "leader";
                    break;
                case 1:
                    output.robot_nameR1 = "follower";
                    break;
                case 2:
                    output.robot_nameR1 = "leader_inv";
                    break;
                default:
                    output.robot_nameR1 = "default";
                    break;
            }
            output.position_xR1 = input.position_xR1;
            output.position_yR1 = input.position_yR1;
            switch (input.robot_idR2) {
                case 0:
                    output.robot_nameR2 = "leader";
                    break;
                case 1:
                    output.robot_nameR2 = "follower";
                    break;
                case 2:
                    output.robot_nameR2 = "leader_inv";
                    break;
                default:
                    output.robot_nameR2 = "default";
                    break;
            }
            output.position_xR2 = input.position_xR2;
            output.position_yR2 = input.position_yR2;
            output.distance = input.distance;
            return output;
        }
    }

    static class JoinInput {
        long gps_position$start;
        long gps_position$end;
        int gps_position$robot_idR1;
        double gps_position$position_xR1;
        double gps_position$position_yR1;
        int gps_position$robot_idR2;
        double gps_position$position_xR2;
        double gps_position$position_yR2;
    }

    static class JoinOutput {
        long start;
        long end;
        int robot_idR1;
        double position_xR1;
        double position_yR1;
        int robot_idR2;
        double position_xR2;
        double position_yR2;
        double distance;
    }

    static class CalculateDistance implements MapFunction<JoinInput, JoinOutput> {

        private double calculateDistanceInMeters(double lat1, double lon1, double lat2, double lon2) {
            final int R = 6371000;
            double latDistance = Math.toRadians(lat2 - lat1);
            double lonDistance = Math.toRadians(lon2 - lon1);
            double a = Math.sin(latDistance / 2) * Math.sin(latDistance / 2) + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) * Math.sin(lonDistance / 2) * Math.sin(lonDistance / 2);
            double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c;
        }

        @Override
        public JoinOutput map(final JoinInput input) {
            JoinOutput output = new JoinOutput();
            output.start = input.gps_position$start;
            output.end = input.gps_position$end;
            output.robot_idR1 = input.gps_position$robot_idR1;
            output.position_xR1 = input.gps_position$position_xR1;
            output.position_yR1 = input.gps_position$position_yR1;
            output.robot_idR2 = input.gps_position$robot_idR2;
            output.position_xR2 = input.gps_position$position_xR2;
            output.position_yR2 = input.gps_position$position_yR2;
            output.distance = calculateDistanceInMeters(input.gps_position$position_yR1, input.gps_position$position_xR1, input.gps_position$position_yR2, input.gps_position$position_xR2);
            return output;
        }
    }

    public static void main(String[] args) {
        try {

            String nesIp = System.getenv("NES_COORDINATOR_IP");
            String nesPortStr = System.getenv("NES_COORDINATOR_REST_PORT");
            String mqttIp = System.getenv("QUERY_HOST_IP");
            String mqttPortStr = System.getenv("QUERY_HOST_MQTT_PORT");
            String collisionQuery = System.getenv("COLLISION_QUERY");
            String collisionRadiusStr = System.getenv("COLLISION_RADIUS");

            int nesPort = Integer.parseInt(nesPortStr);
            double collisionRadius = Double.parseDouble(collisionRadiusStr);
            String mqttUrl = "ws://" + mqttIp + ":" + mqttPortStr;

            NebulaStreamRuntime nebulaStreamRuntime = NebulaStreamRuntime.getRuntime(nesIp, nesPort);
            Query q1 = nebulaStreamRuntime.readFromSource("gps_position");
            q1.map(new Name2IdR1());
            q1.window(TumblingWindow.of(eventTime("timestamp"), seconds(1))).byKey("robot_id").apply(average("position_x"), average("position_y"));
            q1.map("joinKey", literal(1));

            Query q2 = nebulaStreamRuntime.readFromSource("gps_position");
            q2.map(new Name2IdR2());
            q2.window(TumblingWindow.of(eventTime("timestamp"), seconds(1))).byKey("robot_id").apply(average("position_x"), average("position_y"));
            q2.map("joinKey", literal(1));

            Query finalQuery = q1.joinWith(q2).where(attribute("joinKey").equalTo(attribute("joinKey"))).window(TumblingWindow.of(eventTime("start"), seconds(1)));
            finalQuery.project(attribute("gps_position$start"), attribute("gps_position$end"), attribute("gps_position$robot_idR1"), attribute("gps_position$position_xR1"), attribute("gps_position$position_yR1"), attribute("gps_position$robot_idR2"), attribute("gps_position$position_xR2"), attribute("gps_position$position_yR2"));
            finalQuery.map(new CalculateDistance());
            finalQuery.filter(attribute("robot_idR1").lessThan(attribute("robot_idR2")));
            finalQuery.filter(attribute("distance").lessThanOrEqual(collisionRadius));
            finalQuery.map(new Id2Name());
            finalQuery.sink(new MQTTSink(mqttUrl, collisionQuery, "user", 1000, MQTTSink.TimeUnits.milliseconds, 0, MQTTSink.ServiceQualities.atLeastOnce, true));

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
