package com.scumdb.editor.dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/** Utility for obtaining SQLite connections. */
public class Database {
    private final String url;

    public Database(String path) {
        this.url = "jdbc:sqlite:" + path;
    }

    public Connection getConnection() throws SQLException {
        return DriverManager.getConnection(url);
    }
}
