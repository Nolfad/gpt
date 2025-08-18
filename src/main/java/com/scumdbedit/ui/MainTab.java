package com.scumdbedit.ui;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import java.io.IOException;
import java.sql.SQLException;

import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextField;

import com.scumdbedit.db.DatabaseManager;
import com.scumdbedit.model.PlayerData;

/**
 * Main player edition tab showing economy and attribute values.
 */
public class MainTab extends JPanel {

    private final DatabaseManager dbManager;
    private final String steamId;

    private final JTextField famePointsField = new JTextField(10);
    private final JTextField moneyField = new JTextField(10);
    private final JTextField goldField = new JTextField(10);
    private final JTextField strengthField = new JTextField(5);
    private final JTextField constitutionField = new JTextField(5);
    private final JTextField dexterityField = new JTextField(5);
    private final JTextField intelligenceField = new JTextField(5);

    public MainTab(DatabaseManager dbManager, String steamId) {
        this.dbManager = dbManager;
        this.steamId = steamId;
        setLayout(new BorderLayout());

        JPanel fields = new JPanel(new GridLayout(0, 2));
        fields.add(new JLabel("Fama"));
        fields.add(famePointsField);
        fields.add(new JLabel("Dinheiro"));
        fields.add(moneyField);
        fields.add(new JLabel("Gold"));
        fields.add(goldField);
        fields.add(new JLabel("Força"));
        fields.add(strengthField);
        fields.add(new JLabel("Constituição"));
        fields.add(constitutionField);
        fields.add(new JLabel("Destreza"));
        fields.add(dexterityField);
        fields.add(new JLabel("Inteligência"));
        fields.add(intelligenceField);
        add(fields, BorderLayout.CENTER);

        JButton saveButton = new JButton("Salvar");
        saveButton.addActionListener(e -> save());
        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        bottom.add(saveButton);
        add(bottom, BorderLayout.SOUTH);

        load();
    }

    private void load() {
        try {
            PlayerData data = dbManager.loadPlayerData(steamId);
            famePointsField.setText(Integer.toString(data.getFamePoints()));
            moneyField.setText(Integer.toString(data.getMoney()));
            goldField.setText(Integer.toString(data.getGold()));
            strengthField.setText(Integer.toString(data.getStrength()));
            constitutionField.setText(Integer.toString(data.getConstitution()));
            dexterityField.setText(Integer.toString(data.getDexterity()));
            intelligenceField.setText(Integer.toString(data.getIntelligence()));
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    private void save() {
        try {
            PlayerData data = new PlayerData(
                    Integer.parseInt(famePointsField.getText()),
                    Integer.parseInt(moneyField.getText()),
                    Integer.parseInt(goldField.getText()),
                    Integer.parseInt(strengthField.getText()),
                    Integer.parseInt(constitutionField.getText()),
                    Integer.parseInt(dexterityField.getText()),
                    Integer.parseInt(intelligenceField.getText()));
            dbManager.savePlayerData(steamId, data);
        } catch (SQLException | IOException ex) {
            ex.printStackTrace();
        }
    }
}
