#!/bin/bash
# Jython launcher script for Ignition development

JYTHON_HOME="jython2.7.4"
JYTHON_JAR="$JYTHON_HOME/jython.jar"
JAVA_OPTS="-Xmx512m -Xms256m"

if [ ! -f "$JYTHON_JAR" ]; then
    echo "Error: $JYTHON_JAR not found. Please install Jython first."
    exit 1
fi

# JDK 17+ emits native-access warnings for Jython's JFFI loader.
# Grant native access up front when the runtime supports the flag.
JAVA_VERSION=$(java -version 2>&1 | awk -F\" '/version/ {print $2; exit}')
JAVA_MAJOR=$(echo "$JAVA_VERSION" | awk -F. '{ if ($1 == "1") print $2; else print $1 }')
if [ -n "$JAVA_MAJOR" ] && [ "$JAVA_MAJOR" -ge 17 ] 2>/dev/null; then
    JAVA_OPTS="$JAVA_OPTS --enable-native-access=ALL-UNNAMED"
fi

# Add Ignition libraries to classpath if available
IGNITION_LIBS=""
if [ -d "ignition-libs" ]; then
    IGNITION_LIBS=":$(find ignition-libs -name "*.jar" | tr '\n' ':')"
fi

java $JAVA_OPTS -Dpython.home="$JYTHON_HOME" -cp "$JYTHON_JAR$IGNITION_LIBS" org.python.util.jython "$@"