package com.scumdb.editor.service;

import com.scumdb.editor.dao.PlayerDao;
import com.scumdb.editor.model.Player;

import java.sql.SQLException;
import java.util.List;

/** Service layer for players. */
public class PlayerService {
    private final PlayerDao playerDao;

    public PlayerService(PlayerDao playerDao) {
        this.playerDao = playerDao;
    }

    /**
     * Fetches all players from the DAO.
     */
    public List<Player> listPlayers() throws SQLException {
        return playerDao.listPlayers();
    }
}
