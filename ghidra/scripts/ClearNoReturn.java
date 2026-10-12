import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
public class ClearNoReturn extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    for (String s : a) {
      Function f = getFunctionAt(toAddr(Long.parseLong(s.replace("0x",""),16)));
      if (f == null) { println("no function " + s); continue; }
      f.setNoReturn(false);
      println("cleared noreturn " + f.getName());
    }
  }
}
