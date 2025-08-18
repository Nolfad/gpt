package com.scumdb.editor.ui;

import com.scumdb.editor.service.PlayerService;

import javax.swing.*;
import java.awt.*;

/** Main application window with tabbed panels. */
public class MainFrame extends JFrame {
    public MainFrame(PlayerService playerService) {
        super("SCUM DB Editor");
        setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        setSize(800, 600);
        setLocationRelativeTo(null);

        JTabbedPane tabs = new JTabbedPane();
        tabs.addTab("Player", new com.scumdb.editor.ui.tabs.PlayerPanel(playerService));
        add(tabs, BorderLayout.CENTER);
    }
}
