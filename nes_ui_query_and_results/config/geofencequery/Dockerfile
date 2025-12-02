FROM gradle:8-jdk17 AS build
WORKDIR /home/gradle/project

COPY GeoFenceQuery/build.gradle.kts GeoFenceQuery/settings.gradle.kts ./
COPY GeoFenceQuery/src ./src

RUN gradle build --no-daemon -x test

FROM eclipse-temurin:17-jre
WORKDIR /app

COPY --from=build /home/gradle/project/build/libs/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
