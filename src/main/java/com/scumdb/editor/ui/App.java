package com.scumdb.editor.ui;

import javax.swing.SwingUtilities;

/** Entry point for the SCUM DB Editor application. */
public class App {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            MainFrame frame = new MainFrame();
            frame.setVisible(true);
        });
    }
}
