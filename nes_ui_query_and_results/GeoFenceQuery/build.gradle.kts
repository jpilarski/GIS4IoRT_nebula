plugins {
    application
    id("java")
}

group = "org.chistera"
version = "1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("stream.nebula:nebulastream-java-client:0.0.93")
}

application {
    mainClass.set("org.chistera.GeoFenceQuery")
}
