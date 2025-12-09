FROM gradle:8.5-jdk17 AS builder

WORKDIR /home/gradle/project

COPY settings.gradle.kts build.gradle.kts ./
COPY src ./src

RUN gradle clean jar --no-daemon

FROM openjdk:17-slim

WORKDIR /app

COPY --from=builder /home/gradle/project/build/libs/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
