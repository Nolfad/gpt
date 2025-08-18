package com.scumdbedit.ui;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.sql.SQLException;
import java.util.List;
import java.util.function.Consumer;

import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTable;
import javax.swing.table.AbstractTableModel;

import com.scumdbedit.db.DatabaseManager;
import com.scumdbedit.model.Player;

public class PlayerListPanel extends JPanel {

    private final DatabaseManager dbManager;
    private final PlayerTableModel tableModel = new PlayerTableModel();
    private final JTable table = new JTable(tableModel);
    private final Consumer<Player> playerConsumer;

    public PlayerListPanel(DatabaseManager dbManager, Consumer<Player> playerConsumer) {
        this.dbManager = dbManager;
        this.playerConsumer = playerConsumer;
        setLayout(new BorderLayout());

        add(new JScrollPane(table), BorderLayout.CENTER);

        JButton loadButton = new JButton("Carregar jogador");
        loadButton.addActionListener(e -> {
            int row = table.getSelectedRow();
            if (row >= 0 && playerConsumer != null) {
                Player player = tableModel.getPlayerAt(row);
                playerConsumer.accept(player);
            }
        });

        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        bottom.add(loadButton);
        add(bottom, BorderLayout.SOUTH);

        reloadPlayers();
    }

    private void reloadPlayers() {
        try {
            List<Player> players = dbManager.loadPlayers();
            tableModel.setPlayers(players);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private static class PlayerTableModel extends AbstractTableModel {
        private final String[] columns = {"Nome", "steam_id"};
        private List<Player> players = new java.util.ArrayList<>();

        @Override
        public int getRowCount() {
            return players.size();
        }

        @Override
        public int getColumnCount() {
            return columns.length;
        }

        @Override
        public String getColumnName(int column) {
            return columns[column];
        }

        @Override
        public Object getValueAt(int rowIndex, int columnIndex) {
            Player player = players.get(rowIndex);
            switch (columnIndex) {
                case 0:
                    return player.getName();
                case 1:
                    return player.getSteamId();
                default:
                    return null;
            }
        }

        public void setPlayers(List<Player> players) {
            this.players = players;
            fireTableDataChanged();
        }

        public Player getPlayerAt(int row) {
            return players.get(row);
        }
    }
}
