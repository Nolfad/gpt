package com.scumdb.editor.model;

/** Simple POJO representing a player. */
public class Player {
    private long id;
    private String name;
    private int famePoints;

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getFamePoints() {
        return famePoints;
    }

    public void setFamePoints(int famePoints) {
        this.famePoints = famePoints;
    }

    @Override
    public String toString() {
        return name != null ? name : ("Player " + id);
    }
}
