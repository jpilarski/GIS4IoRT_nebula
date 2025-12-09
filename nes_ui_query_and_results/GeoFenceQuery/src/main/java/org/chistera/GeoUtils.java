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
            boolean hasPoints = false;

            while ((line = br.readLine()) != null) {
                if (line.trim().isEmpty()) continue; // Ignoruj puste linie
                
                String[] parts = line.split(",");
                if (parts.length >= 2) {
                    try {
                        double x = Double.parseDouble(parts[0].trim());
                        double y = Double.parseDouble(parts[1].trim());
                        if (first) {
                            path.moveTo(x, y);
                            first = false;
                        } else {
                            path.lineTo(x, y);
                        }
                        hasPoints = true;
                    } catch (NumberFormatException e) {
                        System.err.println("Skipping invalid line: " + line);
                    }
                }
            }
            if (!hasPoints) {
                throw new IOException("CSV file is valid but contains no valid points.");
            }
            path.closePath();
        }
        return path;
    }
}