// Clears a stale listing range and creates a function at the real entry.
// args: <clearStart> <clearEnd> <entry> <name>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
public class FixEntry extends GhidraScript {
    public void run() throws Exception {
        String[] a = getScriptArgs();
        Address s = toAddr(Long.decode(a[0])), e = toAddr(Long.decode(a[1])), en = toAddr(Long.decode(a[2]));
        clearListing(s, e);
        disassemble(en);
        Function f = createFunction(en, a[3]);
        if (f == null) { printerr("FixEntry: create failed at " + en); return; }
        f.setName(a[3], SourceType.USER_DEFINED);
        println("FixEntry: " + a[3] + " at " + en + " body " + f.getBody().getNumAddresses());
    }
}
