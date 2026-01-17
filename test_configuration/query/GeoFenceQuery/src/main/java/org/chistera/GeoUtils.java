package org.chistera;

import org.locationtech.jts.geom.Coordinate;
import org.locationtech.jts.geom.Geometry;
import org.locationtech.jts.geom.Polygon;
import org.locationtech.jts.io.ParseException;
import org.locationtech.jts.io.WKBReader;

import java.awt.geom.Path2D;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class GeoUtils {

    private static byte[] hexStringToByteArray(String hex) {
        int len = hex.length();
        byte[] data = new byte[len / 2];
        for (int i = 0; i < len; i += 2) {
            data[i / 2] = (byte) ((Character.digit(hex.charAt(i), 16) << 4) + Character.digit(hex.charAt(i+1), 16));
        }
        return data;
    }

    public static Path2D.Double loadFieldShape(String filePath) throws IOException, ParseException {
        Path2D.Double path = new Path2D.Double();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String wkbHexString = br.readLine();
            if (wkbHexString == null || wkbHexString.trim().isEmpty()) {
                throw new IOException("WKB file is empty: " + filePath);
            }

            byte[] wkbBytes = hexStringToByteArray(wkbHexString.trim());
            WKBReader wkbReader = new WKBReader();
            Geometry geometry = wkbReader.read(wkbBytes);

            if (!(geometry instanceof Polygon)) {
                throw new ParseException("WKB data did not decode to a Polygon");
            }

            Polygon polygon = (Polygon) geometry;
            Coordinate[] coordinates = polygon.getExteriorRing().getCoordinates();

            if (coordinates.length == 0) {
                throw new IOException("Polygon has no coordinates.");
            }

            path.moveTo(coordinates[0].x, coordinates[0].y);
            for (int i = 1; i < coordinates.length; i++) {
                path.lineTo(coordinates[i].x, coordinates[i].y);
            }
            path.closePath();
        }
        return path;
    }
}
