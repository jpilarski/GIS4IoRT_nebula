plugins {
    java
    application
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

tasks.jar {
    manifest {
        attributes["Main-Class"] = "org.chistera.GeoFenceQuery"
    }
    from(sourceSets.main.get().output)
    from(configurations.runtimeClasspath.get().map { if (it.isDirectory) it else zipTree(it) })
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}