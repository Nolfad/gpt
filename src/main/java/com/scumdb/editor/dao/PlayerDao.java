package com.scumdb.editor.dao;

import com.scumdb.editor.model.Player;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/** DAO for accessing players from Characters table (schema B). */
public class PlayerDao {
    private final Database db;

    public PlayerDao(Database db) {
        this.db = db;
    }

    public List<Player> listAll() throws SQLException {
        String sql = "SELECT Id, characterName, FamePoints FROM Characters ORDER BY characterName";
        List<Player> players = new ArrayList<>();
        try (Connection conn = db.getConnection();
             Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery(sql)) {
            while (rs.next()) {
                Player p = new Player();
                p.setId(rs.getLong("Id"));
                p.setName(rs.getString("characterName"));
                p.setFamePoints(rs.getInt("FamePoints"));
                players.add(p);
            }
        }
        return players;
    }

    public void update(Player player) throws SQLException {
        String sql = "UPDATE Characters SET characterName=?, FamePoints=? WHERE Id=?";
        try (Connection conn = db.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, player.getName());
            ps.setInt(2, player.getFamePoints());
            ps.setLong(3, player.getId());
            ps.executeUpdate();
        }
    }
}
