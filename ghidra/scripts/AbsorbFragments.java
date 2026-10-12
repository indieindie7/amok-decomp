// AbsorbFragments.java: for each entry address given (hex, ascending), remove that function WITHOUT clearing its code
// and add its body (plus any unowned instructions between the owner and it) to the nearest preceding function.
// For switch case blocks Ghidra could not reach (unresolved jump tables) that RepairBodies turned into orphan FUN_s.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.util.*;

public class AbsorbFragments extends GhidraScript {
    @Override
    public void run() throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager(); Listing lst = currentProgram.getListing();
        List<Long> addrs = new ArrayList<>();
        for (String a : getScriptArgs()) addrs.add(Long.parseLong(a.startsWith("0x") ? a.substring(2) : a, 16));
        Collections.sort(addrs);
        int done = 0;
        for (long v : addrs) {
            Address e = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(v);
            Function f = fm.getFunctionAt(e);
            if (f == null) { println("AbsorbFragments: no function at " + e); continue; }
            AddressSetView b = f.getBody();
            Iterator<Function> back = fm.getFunctions(e.subtract(1), false);
            Function owner = back.hasNext() ? back.next() : null;
            if (owner == null || owner.isThunk()) { println("AbsorbFragments: no owner for " + e); continue; }
            AddressSet add = new AddressSet(b);
            // unowned instructions between the owner's last address and the fragment
            Address s = owner.getBody().getMaxAddress().add(1);
            if (s.compareTo(e) < 0) {
                for (Instruction ins : lst.getInstructions(new AddressSet(s, e.subtract(1)), true))
                    if (fm.getFunctionContaining(ins.getAddress()) == null) add.add(new AddressRangeImpl(ins.getMinAddress(), ins.getMaxAddress()));
            }
            String n = f.getName();
            fm.removeFunction(e);
            try { owner.setBody(owner.getBody().union(add)); done++; println("AbsorbFragments: " + n + " -> " + owner.getName() + " (" + add.getNumAddresses() + " bytes)"); }
            catch (Exception x) { println("AbsorbFragments: setBody failed " + owner.getName() + ": " + x); }
        }
        println("AbsorbFragments: absorbed " + done + " of " + addrs.size());
    }
}
