package com.scumdb.editor.dao;

import com.scumdb.editor.dao.adapter.SchemaDetector;
import com.scumdb.editor.model.Player;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/** DAO responsible for loading players independent of schema. */
public class PlayerDao {
    private final Database db;

    public PlayerDao(Database db) {
        this.db = db;
    }

    /**
     * Lists players depending on the detected schema.
     */
    public List<Player> listPlayers() throws SQLException {
        try (Connection conn = db.getConnection()) {
            SchemaDetector.AdapterType type = SchemaDetector.detect(conn);
            switch (type) {
                case ADAPTER_B:
                    return listPlayersSchemaB(conn);
                case ADAPTER_A:
                    return listPlayersSchemaA(conn);
                default:
                    throw new IllegalStateException("Unknown schema type: " + type);
            }
        }
    }

    /** Query for schema B (Characters table). */
    private List<Player> listPlayersSchemaB(Connection conn) throws SQLException {
        List<Player> players = new ArrayList<>();
        String sql = "SELECT Id, Name FROM Characters";
        try (PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                Player p = new Player();
                p.setId(rs.getLong("Id"));
                p.setName(rs.getString("Name"));
                players.add(p);
            }
        }
        return players;
    }

    /** Minimal stub for schema A. */
    private List<Player> listPlayersSchemaA(Connection conn) {
        // TODO: Implement entity/entity_component parsing.
        return new ArrayList<>();
    }
}
