package com.scumdb.editor.dao.adapter;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashSet;
import java.util.Set;

/** Detects which schema is present in a SCUM database. */
public class SchemaDetector {

    public enum AdapterType { ADAPTER_A, ADAPTER_B }

    public static AdapterType detect(Connection conn) throws SQLException {
        Set<String> tables = new HashSet<>();
        try (Statement st = conn.createStatement();
             ResultSet rs = st.executeQuery("SELECT name FROM sqlite_master WHERE type='table';")) {
            while (rs.next()) {
                tables.add(rs.getString(1));
            }
        }
        boolean hasEntity = tables.contains("entity");
        boolean hasComponent = tables.contains("entity_component");
        boolean hasCharacters = tables.contains("Characters");
        if (hasEntity && hasComponent) {
            return AdapterType.ADAPTER_A;
        } else if (hasCharacters) {
            return AdapterType.ADAPTER_B;
        }
        throw new IllegalStateException("Esquema não suportado");
    }
}
