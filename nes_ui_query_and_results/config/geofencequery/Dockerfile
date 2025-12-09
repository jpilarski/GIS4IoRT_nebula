FROM gradle:8.5-jdk17 AS builder

WORKDIR /home/gradle/project

COPY GeoFenceQuery/settings.gradle.kts GeoFenceQuery/build.gradle.kts ./
COPY GeoFenceQuery/src ./src

RUN gradle clean shadowJar --no-daemon

FROM eclipse-temurin:17-jre

WORKDIR /app

COPY --from=builder /home/gradle/project/build/libs/*-all.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
