package com.scumdb.editor.service;

import com.scumdb.editor.dao.Database;
import com.scumdb.editor.model.Player;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/** Service layer for players. */
public class PlayerService {
    private final Database db;

    public PlayerService(Database db) {
        this.db = db;
    }

    /**
     * Fetches all players using the simple schema B (Characters table).
     * This is a minimal example and does not cover all spec details.
     */
    public List<Player> listPlayers() throws SQLException {
        List<Player> players = new ArrayList<>();
        try (Connection conn = db.getConnection();
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery("SELECT Id, Name FROM Characters")) {
            while (rs.next()) {
                Player p = new Player();
                p.setId(rs.getLong("Id"));
                p.setName(rs.getString("Name"));
                players.add(p);
            }
        }
        return players;
    }
}
