#!/bin/bash
# Jython launcher script for Ignition development

JYTHON_JAR="jython-standalone-2.7.3.jar"
JAVA_OPTS="-Xmx512m -Xms256m"

if [ ! -f "$JYTHON_JAR" ]; then
    echo "Error: $JYTHON_JAR not found. Please download Jython first."
    exit 1
fi

# Add Ignition libraries to classpath if available
IGNITION_LIBS=""
if [ -d "ignition-libs" ]; then
    IGNITION_LIBS=":$(find ignition-libs -name "*.jar" | tr '\n' ':')"
fi

java $JAVA_OPTS -cp "$JYTHON_JAR$IGNITION_LIBS" org.python.util.jython "$@"