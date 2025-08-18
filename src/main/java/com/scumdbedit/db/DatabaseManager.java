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
import java.util.ArrayList;
import java.util.List;

import com.scumdbedit.model.Player;
import com.scumdbedit.model.PlayerData;
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
     * Loads all players from the database.
     *
     * @return list of {@link Player} entries
     * @throws SQLException if a database access error occurs
     */
    public List<Player> loadPlayers() throws SQLException {
        List<Player> players = new ArrayList<>();
        String sql = "SELECT name, steam_id FROM character_stats";
        try (Statement stmt = connect().createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            while (rs.next()) {
                Player player = new Player(
                        rs.getString("name"),
                        rs.getString("steam_id"));
                players.add(player);
            }
        }
        return players;
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

    private int queryForInt(String sql) throws SQLException {
        try (Statement stmt = connect().createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            return rs.next() ? rs.getInt(1) : 0;
        }
    }

    public PlayerData loadPlayerData(String steamId) throws SQLException {
        int famePoints = queryForInt(
                "SELECT fame_points FROM fame WHERE steam_id='" + steamId + "'");
        int money = queryForInt(
                "SELECT money FROM fame WHERE steam_id='" + steamId + "'");
        int gold = queryForInt(
                "SELECT gold FROM fame WHERE steam_id='" + steamId + "'");

        int baseStr = queryForInt(
                "SELECT strength_level FROM metabolism WHERE steam_id='" + steamId + "'");
        int muscle = queryForInt(
                "SELECT muscle_mass FROM body WHERE steam_id='" + steamId + "'");
        int baseCon = queryForInt(
                "SELECT constitution_level FROM metabolism WHERE steam_id='" + steamId + "'");
        int injury = queryForInt(
                "SELECT damage FROM injuries WHERE steam_id='" + steamId + "'");
        int baseDex = queryForInt(
                "SELECT dexterity_level FROM metabolism WHERE steam_id='" + steamId + "'");
        int rest = queryForInt(
                "SELECT rest_quality FROM sleep WHERE steam_id='" + steamId + "'");
        int baseInt = queryForInt(
                "SELECT intelligence_level FROM metabolism WHERE steam_id='" + steamId + "'");
        int headDamage = queryForInt(
                "SELECT head_damage FROM injuries WHERE steam_id='" + steamId + "'");

        int strength = baseStr + muscle;
        int constitution = baseCon - injury;
        int dexterity = baseDex + rest;
        int intelligence = baseInt - headDamage;

        return new PlayerData(famePoints, money, gold,
                strength, constitution, dexterity, intelligence);
    }

    public void savePlayerData(String steamId, PlayerData data)
            throws SQLException, IOException {
        backupDatabase();
        Connection conn = connect();
        try (Statement stmt = conn.createStatement()) {
            conn.setAutoCommit(false);
            stmt.executeUpdate("UPDATE fame SET fame_points=" + data.getFamePoints()
                    + ", money=" + data.getMoney()
                    + ", gold=" + data.getGold()
                    + " WHERE steam_id='" + steamId + "'");
            stmt.executeUpdate("UPDATE metabolism SET strength_level=" + data.getStrength()
                    + ", constitution_level=" + data.getConstitution()
                    + ", dexterity_level=" + data.getDexterity()
                    + ", intelligence_level=" + data.getIntelligence()
                    + " WHERE steam_id='" + steamId + "'");
            stmt.executeUpdate("UPDATE body SET muscle_mass=" + data.getStrength()
                    + " WHERE steam_id='" + steamId + "'");
            stmt.executeUpdate("UPDATE sleep SET rest_quality=" + data.getDexterity()
                    + " WHERE steam_id='" + steamId + "'");
            stmt.executeUpdate("UPDATE injuries SET damage=" + data.getConstitution()
                    + ", head_damage=" + data.getIntelligence()
                    + " WHERE steam_id='" + steamId + "'");
            conn.commit();
        } catch (SQLException e) {
            conn.rollback();
            throw e;
        } finally {
            conn.setAutoCommit(true);
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

