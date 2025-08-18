package com.scumdb.editor.ui;

import com.scumdb.editor.dao.Database;
import com.scumdb.editor.service.PlayerService;

import javax.swing.SwingUtilities;

/** Entry point for the SCUM DB Editor application. */
public class App {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            Database db = new Database("scum.db");
            PlayerService playerService = new PlayerService(db);
            MainFrame frame = new MainFrame(playerService);
            frame.setVisible(true);
        });
    }
}
