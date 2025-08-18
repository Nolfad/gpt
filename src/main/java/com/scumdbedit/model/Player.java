package com.scumdbedit.model;

public class Player {
    private final String name;
    private final String steamId;

    public Player(String name, String steamId) {
        this.name = name;
        this.steamId = steamId;
    }

    public String getName() {
        return name;
    }

    public String getSteamId() {
        return steamId;
    }
}
