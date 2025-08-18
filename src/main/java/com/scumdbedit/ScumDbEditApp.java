package com.scumdbedit;

import javax.swing.JFrame;
import javax.swing.SwingUtilities;

import com.scumdbedit.db.DatabaseManager;
import com.scumdbedit.model.Player;
import com.scumdbedit.ui.MainTab;
import com.scumdbedit.ui.PlayerListPanel;

/**
 * Entry point for the SCUM DB Edit application. Displays the list of players
 * and opens an editor window for the selected player.
 */
public class ScumDbEditApp {

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            DatabaseManager db = new DatabaseManager();
            try {
                db.verifySchema();
            } catch (Exception e) {
                e.printStackTrace();
            }

            JFrame frame = new JFrame("SCUM DB Edit");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setContentPane(new PlayerListPanel(db, ScumDbEditApp::openEditor));
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }

    private static void openEditor(Player player) {
        DatabaseManager db = new DatabaseManager();
        JFrame frame = new JFrame("Edit " + player.getName());
        frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        frame.setContentPane(new MainTab(db, player.getSteamId()));
        frame.pack();
        frame.setLocationRelativeTo(null);
        frame.setVisible(true);
    }
}
