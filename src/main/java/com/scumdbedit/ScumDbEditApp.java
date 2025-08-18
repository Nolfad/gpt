package com.scumdbedit;

import javax.swing.JFrame;
import javax.swing.SwingUtilities;

/**
 * Basic entry point for the SCUM DB Edit application.
 *
 * <p>Launches a minimal Swing window to verify the application
 * can start correctly.</p>
 */
public class ScumDbEditApp {

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("SCUM DB Edit");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setSize(400, 300);
            frame.setLocationRelativeTo(null);
            frame.setVisible(true);
        });
    }
}

