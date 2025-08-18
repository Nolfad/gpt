package com.scumdb.editor.ui.tabs;

import com.scumdb.editor.model.Player;
import com.scumdb.editor.service.PlayerService;

import javax.swing.*;
import java.awt.*;
import java.sql.SQLException;

/** Minimal Player tab allowing list and edit of names and fame points. */
public class PlayerPanel extends JPanel {
    private final PlayerService service;
    private final DefaultListModel<Player> listModel = new DefaultListModel<>();
    private final JList<Player> playerList = new JList<>(listModel);
    private final JTextField nameField = new JTextField();
    private final JSpinner fameField = new JSpinner(new SpinnerNumberModel(0, 0, Integer.MAX_VALUE, 1));

    public PlayerPanel(PlayerService service) {
        this.service = service;
        setLayout(new BorderLayout());

        playerList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        playerList.addListSelectionListener(e -> {
            if (!e.getValueIsAdjusting()) {
                loadSelected();
            }
        });

        add(new JScrollPane(playerList), BorderLayout.WEST);

        JPanel form = new JPanel(new GridLayout(0, 2));
        form.add(new JLabel("Name:"));
        form.add(nameField);
        form.add(new JLabel("Fame Points:"));
        form.add(fameField);
        JButton save = new JButton("Save");
        save.addActionListener(e -> save());
        form.add(save);

        add(form, BorderLayout.CENTER);

        reload();
    }

    private void reload() {
        listModel.clear();
        try {
            for (Player p : service.listPlayers()) {
                listModel.addElement(p);
            }
        } catch (SQLException ex) {
            JOptionPane.showMessageDialog(this, "Failed to load players: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void loadSelected() {
        Player p = playerList.getSelectedValue();
        if (p == null) {
            nameField.setText("");
            fameField.setValue(0);
            return;
        }
        nameField.setText(p.getName());
        fameField.setValue(p.getFamePoints());
    }

    private void save() {
        Player p = playerList.getSelectedValue();
        if (p == null) {
            return;
        }
        p.setName(nameField.getText());
        p.setFamePoints((Integer) fameField.getValue());
        try {
            service.updatePlayer(p);
            playerList.repaint();
        } catch (SQLException ex) {
            JOptionPane.showMessageDialog(this, "Failed to save player: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}
