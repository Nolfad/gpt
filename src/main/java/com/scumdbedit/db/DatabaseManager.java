package com.scumdbedit.db;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Handles connections and operations against the SCUM SQLite database.
 */
public class DatabaseManager {

    private static final String DB_PATH = "scum.db";
    private static final String[] REQUIRED_TABLES = {
            "character_stats",
            "entity_component",
            "fame",
            "clan"
    };

    private Connection connection;

    /**
     * Opens a connection to the SCUM database if not already open.
     *
     * @return an active {@link Connection}
     * @throws SQLException if the connection cannot be established
     */
    public Connection connect() throws SQLException {
        if (connection == null || connection.isClosed()) {
            connection = DriverManager.getConnection("jdbc:sqlite:" + DB_PATH);
        }
        return connection;
    }

    /**
     * Verifies that all required tables exist in the database schema.
     *
     * @throws SQLException if a database access error occurs
     * @throws IllegalStateException if any required table is missing
     */
    public void verifySchema() throws SQLException {
        try (Statement stmt = connect().createStatement()) {
            for (String table : REQUIRED_TABLES) {
                try (ResultSet rs = stmt.executeQuery(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='" + table + "'")) {
                    if (!rs.next()) {
                        throw new IllegalStateException("Required table missing: " + table);
                    }
                }
            }
        }
    }

    /**
     * Executes an update statement against the database, creating a timestamped
     * backup of the database file before applying any changes.
     *
     * @param sql the SQL update statement to execute
     * @return the number of rows affected
     * @throws SQLException if a database access error occurs
     * @throws IOException if the backup cannot be created
     */
    public int executeUpdate(String sql) throws SQLException, IOException {
        backupDatabase();
        try (Statement stmt = connect().createStatement()) {
            return stmt.executeUpdate(sql);
        }
    }

    /**
     * Creates a timestamped backup of the database file in the same directory.
     *
     * @throws IOException if the file cannot be copied
     */
    private void backupDatabase() throws IOException {
        Path source = Paths.get(DB_PATH);
        if (Files.notExists(source)) {
            return;
        }
        String timestamp = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        Path target = Paths.get(DB_PATH + "." + timestamp + ".bak");
        Files.copy(source, target, StandardCopyOption.COPY_ATTRIBUTES);
    }
}

