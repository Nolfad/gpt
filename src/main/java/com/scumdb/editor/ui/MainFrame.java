package com.scumdb.editor.ui;

import com.scumdb.editor.dao.Database;
import com.scumdb.editor.dao.PlayerDao;
import com.scumdb.editor.service.PlayerService;
import com.scumdb.editor.ui.tabs.PlayerPanel;

import javax.swing.*;
import java.awt.*;

/** Main application window with tabbed panels. */
public class MainFrame extends JFrame {
    public MainFrame() {
        super("SCUM DB Editor");
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        setSize(800, 600);
        setLocationRelativeTo(null);

        Database db = new Database("scum.db");
        PlayerDao playerDao = new PlayerDao(db);
        PlayerService playerService = new PlayerService(playerDao);

        JTabbedPane tabs = new JTabbedPane();
        tabs.addTab("Player", new PlayerPanel(playerService));
        add(tabs, BorderLayout.CENTER);
    }
}
