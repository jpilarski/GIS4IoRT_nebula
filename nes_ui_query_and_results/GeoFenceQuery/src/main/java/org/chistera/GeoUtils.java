package org.chistera;

import java.awt.geom.Path2D;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class GeoUtils {
    public static Path2D.Double loadFieldShape(String filePath) throws IOException {
        Path2D.Double path = new Path2D.Double();
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            String line;
            boolean first = true;
            while ((line = br.readLine()) != null) {
                String[] parts = line.split(",");
                if (parts.length >= 2) {
                    double x = Double.parseDouble(parts[0].trim());
                    double y = Double.parseDouble(parts[1].trim());
                    if (first) {
                        path.moveTo(x, y);
                        first = false;
                    } else {
                        path.lineTo(x, y);
                    }
                }
            }
            path.closePath();
        }
        return path;
    }
}