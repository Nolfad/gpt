# SCUM DB Edit

Small Swing application to inspect and edit a SCUM server SQLite database.

## Building

The project uses Maven. To create an executable jar run:

```bash
mvn -Pprod clean package
```

The jar with dependencies will be generated as `scum-db-edit.jar` inside the
`target` directory.

## Running

On Linux/macOS:

```bash
./run-linux.sh
```

On Windows:

```bat
run-windows.bat
```

Both scripts expect the jar to be located in the same directory and will start
the graphical interface.
