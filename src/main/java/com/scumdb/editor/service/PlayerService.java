package com.scumdb.editor.service;

import com.scumdb.editor.dao.Database;
import com.scumdb.editor.dao.PlayerDao;
import com.scumdb.editor.model.Player;

import java.sql.SQLException;
import java.util.List;

/** Service layer for players. */
public class PlayerService {
    private final PlayerDao dao;

    public PlayerService(Database db) {
        this.dao = new PlayerDao(db);
    }

    /** Lists all players from the Characters table. */
    public List<Player> listPlayers() throws SQLException {
        return dao.listAll();
    }

    /** Persists updates to a player. */
    public void updatePlayer(Player player) throws SQLException {
        dao.update(player);
    }
}
