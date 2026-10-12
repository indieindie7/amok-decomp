import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
// ForceCallReturn.java <addr...>: for every call to the given functions set a CALL_RETURN
// flow override and disassemble the fall-through, so a false noreturn flag cannot cut bodies.
public class ForceCallReturn extends GhidraScript {
  public void run() throws Exception {
    Listing lst = currentProgram.getListing();
    FunctionManager fm = currentProgram.getFunctionManager();
    int ovr = 0, dis = 0;
    for (String s : getScriptArgs()) {
      Address t = toAddr(Long.parseLong(s.replace("0x",""),16));
      Function f = fm.getFunctionAt(t);
      if (f == null) { println("no function " + s); continue; }
      f.setNoReturn(false);
      for (Reference r : currentProgram.getReferenceManager().getReferencesTo(t)) {
        if (!r.getReferenceType().isCall()) continue;
        Instruction ins = lst.getInstructionAt(r.getFromAddress());
        if (ins == null) continue;
        if (ins.getFlowOverride() != FlowOverride.CALL_RETURN) { ins.setFlowOverride(FlowOverride.CALL_RETURN); ovr++; }
        Address ft = ins.getAddress().add(ins.getLength());
        if (lst.getInstructionAt(ft) == null && lst.getDefinedDataContaining(ft) == null && currentProgram.getMemory().contains(ft)) {
          DisassembleCommand dc = new DisassembleCommand(ft, null, true); if (dc.applyTo(currentProgram, monitor)) dis++;
        }
      }
      println("done " + f.getName() + " noreturn=" + f.hasNoReturn());
    }
    println("overrides set " + ovr + ", disassembled " + dis);
  }
}
