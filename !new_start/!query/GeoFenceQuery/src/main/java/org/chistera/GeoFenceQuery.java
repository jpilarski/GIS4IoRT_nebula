package org.chistera;

import stream.nebula.exceptions.RESTException;
import stream.nebula.operators.sinks.MQTTSink;
import stream.nebula.operators.window.TumblingWindow;
import stream.nebula.runtime.NebulaStreamRuntime;
import stream.nebula.runtime.Query;
import stream.nebula.udf.MapFunction;

import java.awt.geom.Path2D;
import java.io.File;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

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
            
            // Uproszczona logika zgodnie z życzeniem
            output.exited = this.field.contains(input.position_x, input.position_y) ? 0 : 1;
            
            return output;
        }
    }

    // Metoda do sprawdzania zdrowia Koordynatora (REST)
    private static void checkCoordinatorHealth(String ip, int port) throws IOException {
        String urlString = "http://" + ip + ":" + port + "/v1/nes/connectivity/check";
        System.out.println("Checking NES Coordinator connectivity: " + urlString);
        
        URL url = new URL(urlString);
        HttpURLConnection con = (HttpURLConnection) url.openConnection();
        con.setRequestMethod("GET");
        con.setConnectTimeout(5000);
        con.setReadTimeout(5000);

        int status = con.getResponseCode();
        if (status != 200) {
            throw new IOException("Coordinator returned non-200 status: " + status);
        }
        System.out.println("NES Coordinator is reachable (200 OK).");
    }

    public static void main(String[] args) {
        try {
            // 1. Walidacja argumentów
            if (args.length < 3 || (!"continuous".equalsIgnoreCase(args[0]) && !"historical".equalsIgnoreCase(args[0]))) {
                throw new IllegalArgumentException("Usage: <continuous|historical> <path_to_csv> <query_name>");
            }

            String mode = args[0];
            String csvPath = args[1];
            String queryName = args[2];

            // 2. Walidacja pliku CSV
            File csvFile = new File(csvPath);
            if (!csvFile.exists() || !csvFile.canRead()) {
                throw new IOException("Cannot read CSV file at: " + csvPath);
            }

            // 3. Pobieranie ENV
            String nesIp = System.getenv("NES_COORDINATOR_IP");
            String nesPortStr = System.getenv("NES_COORDINATOR_REST_PORT");
            String mqttIp = System.getenv("QUERY_HOST_IP");
            String mqttPortStr = System.getenv("QUERY_HOST_MQTT_PORT");

            if (nesIp == null || nesPortStr == null || mqttIp == null || mqttPortStr == null) {
                throw new IllegalStateException("Missing required ENV variables. Check .env file.");
            }

            int nesPort = Integer.parseInt(nesPortStr);
            String mqttUrl = "ws://" + mqttIp + ":" + mqttPortStr;

            // 4. Sprawdzenie połączenia REST z NES Coordinator
            checkCoordinatorHealth(nesIp, nesPort);

            // 5. Wczytanie kształtu pola
            System.out.println("Loading field shape from: " + csvPath);
            Path2D.Double fieldShape = GeoUtils.loadFieldShape(csvPath);

            // 6. Budowanie zapytania
            NebulaStreamRuntime nebulaStreamRuntime = NebulaStreamRuntime.getRuntime(nesIp, nesPort);
            Query query = nebulaStreamRuntime.readFromSource("gps_position");
            
            query.map(new GeoFence(fieldShape));

            if ("continuous".equalsIgnoreCase(mode)) {
                query.window(TumblingWindow.of(eventTime("timestamp"), seconds(1)))
                     .byKey("robot_id")
                     .apply(sum("exited"));
            }
            
            query.filter(attribute("exited").greaterThan(0));
            
            query.sink(new MQTTSink(mqttUrl, queryName, "user", 1000, 
                        MQTTSink.TimeUnits.milliseconds, 0, 
                        MQTTSink.ServiceQualities.atLeastOnce, true));
            
            // 7. Uruchomienie zapytania
            int queryId = nebulaStreamRuntime.executeQuery(query, "BottomUp");
            System.out.println(">>> SUCCESS: Query started with ID: " + queryId);

            if ("historical".equalsIgnoreCase(mode)) {
                System.out.println("Waiting 60s for historical query...");
                Thread.sleep(60000);
                nebulaStreamRuntime.stopQuery(queryId);
                System.out.println("Historical query stopped.");
            }

        } catch (Throwable t) {
            System.err.println("!!! CRITICAL ERROR !!!");
            t.printStackTrace();
            System.exit(1); // Wyjście z kodem błędu, żeby Docker wiedział, że coś poszło nie tak
        }
    }
}