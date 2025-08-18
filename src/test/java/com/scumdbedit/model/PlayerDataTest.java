package com.scumdbedit.model;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class PlayerDataTest {

    @Test
    public void gettersReturnValues() {
        PlayerData data = new PlayerData(10, 20, 30, 40, 50, 60, 70);
        assertEquals(10, data.getFamePoints());
        assertEquals(20, data.getMoney());
        assertEquals(30, data.getGold());
        assertEquals(40, data.getStrength());
        assertEquals(50, data.getConstitution());
        assertEquals(60, data.getDexterity());
        assertEquals(70, data.getIntelligence());
    }
}
