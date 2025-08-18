package com.scumdb.editor.service;

import com.scumdb.editor.dao.Database;
import com.scumdb.editor.model.Player;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

public class PlayerServiceTest {
    private Database db;

    @BeforeEach
    public void setup() throws Exception {
        db = new Database(":memory:");
        try (Connection conn = db.getConnection(); Statement st = conn.createStatement()) {
            st.execute("CREATE TABLE Characters(Id INTEGER PRIMARY KEY, characterName TEXT, FamePoints INTEGER)");
            st.execute("INSERT INTO Characters(Id, characterName, FamePoints) VALUES (1,'Foo',10)");
        }
    }

    @Test
    public void listAndUpdatePlayer() throws Exception {
        PlayerService svc = new PlayerService(db);
        List<Player> players = svc.listPlayers();
        assertEquals(1, players.size());
        Player p = players.get(0);
        assertEquals("Foo", p.getName());
        assertEquals(10, p.getFamePoints());

        p.setName("Bar");
        p.setFamePoints(20);
        svc.updatePlayer(p);

        try (Connection conn = db.getConnection();
             ResultSet rs = conn.createStatement().executeQuery("SELECT characterName, FamePoints FROM Characters WHERE Id=1")) {
            assertTrue(rs.next());
            assertEquals("Bar", rs.getString(1));
            assertEquals(20, rs.getInt(2));
        }
    }
}
