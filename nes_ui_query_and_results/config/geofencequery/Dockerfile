# Build stage
FROM gradle:8-jdk17 AS build
WORKDIR /home/gradle/project

# Kopiujemy pliki gradle'a i kod źródłowy
# Zakładamy, że kontekst budowania to główny folder projektu
COPY GeoFenceQuery/build.gradle.kts GeoFenceQuery/settings.gradle.kts ./
COPY GeoFenceQuery/src ./src

# Budujemy fat jar lub zwykły jar (zależy od konfiguracji gradle, tu standard)
RUN gradle build --no-daemon -x test

# Run stage
FROM eclipse-temurin:17-jre
WORKDIR /app

# Kopiujemy zbudowany jar
COPY --from=build /home/gradle/project/build/libs/*.jar app.jar

# ENTRYPOINT ustawiamy, ale argumenty poda docker-compose
ENTRYPOINT ["java", "-jar", "app.jar"]