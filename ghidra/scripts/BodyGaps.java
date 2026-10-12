// BodyGaps.java: args are pairs <entry> <endExcl> (hex). Prints the ranges inside [entry,end) that the function at entry
// does not own, with the code unit and owner found there. Read-only check after GrowToRange.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class BodyGaps extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs(); FunctionManager fm = currentProgram.getFunctionManager(); Listing lst = currentProgram.getListing();
        for (int i = 0; i + 1 < a.length; i += 2) {
            Address s = toAddr(Long.parseLong(a[i].replace("0x", ""), 16)), e = toAddr(Long.parseLong(a[i + 1].replace("0x", ""), 16) - 1);
            Function f = fm.getFunctionAt(s);
            if (f == null) { println("BodyGaps: no function at " + s); continue; }
            AddressSetView gap = new AddressSet(s, e).subtract(f.getBody());
            for (AddressRange r : gap) {
                CodeUnit cu = lst.getCodeUnitContaining(r.getMinAddress()); Function o = fm.getFunctionContaining(r.getMinAddress());
                println("BodyGaps: " + f.getName() + " " + r + " cu=" + (cu == null ? "-" : cu.getMinAddress() + ":" + cu) + " owner=" + (o == null ? "-" : o.getName()));
            }
        }
    }
}
