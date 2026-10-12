// DefineStructs.java <abs spec> <category>: create/replace structs from a text spec.
// Spec: "struct <Name> <size_hex>" then "<off_hex> <type> <field>" lines ('#' starts a comment, blank lines ok).
// Types: byte char short ushort int uint pointer float double, <Struct>* (pointer to a struct of the
// spec or category; forward references work), <type>[n]. Fields that would overlap are reported and skipped.
//@category Amok
import ghidra.app.script.GhidraScript;
import ghidra.program.model.data.*;
import java.nio.file.*;
import java.util.*;
public class DefineStructs extends GhidraScript {
  DataTypeManager dtm; CategoryPath cat;
  static int hex(String s) { return Integer.parseInt(s.startsWith("0x") ? s.substring(2) : s, 16); }  // spec numbers are hex
  DataType builtin(String t) {
    switch (t) {
      case "int": return IntegerDataType.dataType;
      case "uint": return UnsignedIntegerDataType.dataType;
      case "short": return ShortDataType.dataType;
      case "ushort": return UnsignedShortDataType.dataType;
      case "byte": return ByteDataType.dataType;
      case "char": return CharDataType.dataType;
      case "pointer": return PointerDataType.dataType;
      case "float": return FloatDataType.dataType;
      case "double": return DoubleDataType.dataType;
    }
    return null;
  }
  DataType resolve(String t) {
    int n = 0;
    if (t.endsWith("]")) { int i = t.lastIndexOf('['); n = Integer.decode(t.substring(i + 1, t.length() - 1)); t = t.substring(0, i); }
    boolean ptr = t.endsWith("*");
    if (ptr) t = t.substring(0, t.length() - 1);
    DataType dt = builtin(t);
    if (dt == null) dt = dtm.getDataType(cat, t);
    if (dt == null) return null;
    if (ptr) dt = new PointerDataType(dt, 4, dtm);
    if (n > 0) dt = new ArrayDataType(dt, n, dt.getLength(), dtm);
    return dt;
  }
  public void run() throws Exception {
    String[] a = getScriptArgs();
    dtm = currentProgram.getDataTypeManager(); cat = new CategoryPath(a[1]);
    List<String[]> heads = new ArrayList<>(); Map<String, List<String[]>> fields = new LinkedHashMap<>();
    String cur = null;
    for (String line : Files.readAllLines(Paths.get(a[0]))) {
      int h = line.indexOf('#'); if (h >= 0) line = line.substring(0, h);
      line = line.trim(); if (line.isEmpty()) continue;
      String[] p = line.split("\\s+");
      if (p[0].equals("struct")) { heads.add(p); cur = p[1]; fields.put(cur, new ArrayList<>()); }
      else if (cur != null && p.length >= 3) fields.get(cur).add(p);
    }
    // pass 1: empty shells of the right size (so pointers between them resolve)
    for (String[] p : heads) {
      StructureDataType s = new StructureDataType(cat, p[1], hex(p[2]), dtm);
      dtm.addDataType(s, DataTypeConflictHandler.REPLACE_HANDLER);
    }
    int nf = 0, bad = 0;
    for (String[] p : heads) {
      Structure s = (Structure) dtm.getDataType(cat, p[1]);
      for (String[] f : fields.get(p[1])) {
        DataType dt = resolve(f[1]);
        int off = hex(f[0]);
        if (dt == null) { println("unknown type " + f[1] + " in " + p[1]); bad++; continue; }
        if (off + dt.getLength() > s.getLength()) { println("field past end " + p[1] + "." + f[2]); bad++; continue; }
        try { s.replaceAtOffset(off, dt, dt.getLength(), f[2], null); nf++; }
        catch (Exception e) { println("field fail " + p[1] + "." + f[2] + ": " + e.getMessage()); bad++; }
      }
    }
    println("structs: " + heads.size() + ", fields " + nf + ", problems " + bad);
  }
}
