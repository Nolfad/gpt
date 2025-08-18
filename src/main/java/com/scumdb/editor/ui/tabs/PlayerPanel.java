package com.scumdb.editor.ui.tabs;

import com.scumdb.editor.model.Player;
import com.scumdb.editor.service.PlayerService;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.sql.SQLException;
import java.util.List;

/** Panel that lists players from the database. */
public class PlayerPanel extends JPanel {
    private final PlayerService playerService;
    private final DefaultTableModel tableModel;

    public PlayerPanel(PlayerService service) {
        this.playerService = service;
        setLayout(new BorderLayout());

        tableModel = new DefaultTableModel(new Object[]{"ID", "Name"}, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        JTable table = new JTable(tableModel);
        add(new JScrollPane(table), BorderLayout.CENTER);

        loadPlayers();
    }

    private void loadPlayers() {
        try {
            List<Player> players = playerService.listPlayers();
            for (Player p : players) {
                tableModel.addRow(new Object[]{p.getId(), p.getName()});
            }
        } catch (SQLException e) {
            JOptionPane.showMessageDialog(this, "Failed to load players: " + e.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}
