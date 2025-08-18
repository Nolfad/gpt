package com.scumdb.editor.dao.adapter;

import org.junit.jupiter.api.Test;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;

import static org.junit.jupiter.api.Assertions.*;

public class SchemaDetectorTest {

    private Connection inMemory() throws SQLException {
        return DriverManager.getConnection("jdbc:sqlite::memory:");
    }

    @Test
    public void detectsAdapterA() throws Exception {
        try (Connection conn = inMemory(); Statement st = conn.createStatement()) {
            st.execute("CREATE TABLE entity(id INTEGER);");
            st.execute("CREATE TABLE entity_component(id INTEGER);");
            assertEquals(SchemaDetector.AdapterType.ADAPTER_A, SchemaDetector.detect(conn));
        }
    }

    @Test
    public void detectsAdapterB() throws Exception {
        try (Connection conn = inMemory(); Statement st = conn.createStatement()) {
            st.execute("CREATE TABLE Characters(Id INTEGER);");
            assertEquals(SchemaDetector.AdapterType.ADAPTER_B, SchemaDetector.detect(conn));
        }
    }

    @Test
    public void unsupportedThrows() throws Exception {
        try (Connection conn = inMemory()) {
            assertThrows(IllegalStateException.class, () -> SchemaDetector.detect(conn));
        }
    }
}
