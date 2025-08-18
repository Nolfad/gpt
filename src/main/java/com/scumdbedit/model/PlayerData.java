package com.scumdbedit.model;

/**
 * Holds economic and attribute values for a player.
 */
public class PlayerData {
    private final int famePoints;
    private final int money;
    private final int gold;
    private final int strength;
    private final int constitution;
    private final int dexterity;
    private final int intelligence;

    public PlayerData(int famePoints, int money, int gold,
                      int strength, int constitution,
                      int dexterity, int intelligence) {
        this.famePoints = famePoints;
        this.money = money;
        this.gold = gold;
        this.strength = strength;
        this.constitution = constitution;
        this.dexterity = dexterity;
        this.intelligence = intelligence;
    }

    public int getFamePoints() {
        return famePoints;
    }

    public int getMoney() {
        return money;
    }

    public int getGold() {
        return gold;
    }

    public int getStrength() {
        return strength;
    }

    public int getConstitution() {
        return constitution;
    }

    public int getDexterity() {
        return dexterity;
    }

    public int getIntelligence() {
        return intelligence;
    }
}
