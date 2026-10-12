// MemBlocks.java [ro <blockname>] [add <name> <start> <len>]: list memory blocks; "ro" clears the write flag of a block
// (the decompiler then folds literal-pool loads into constants); "add" creates an uninitialized RAM block.
//@category Amok
import ghidra.app.script.GhidraScript;
import ghidra.program.model.mem.*;
public class MemBlocks extends GhidraScript {
  public void run() throws Exception {
    String[] a = getScriptArgs();
    Memory m = currentProgram.getMemory();
    if (a.length >= 2 && a[0].equals("ro")) m.getBlock(a[1]).setWrite(false);
    if (a.length >= 4 && a[0].equals("add")) {
      MemoryBlock b = m.createUninitializedBlock(a[1], toAddr(Long.decode(a[2])), Long.decode(a[3]), false);
      b.setRead(true); b.setWrite(true);
    }
    for (MemoryBlock b : m.getBlocks())
      println(String.format("block %s %s-%s r%s w%s x%s init %s", b.getName(), b.getStart(), b.getEnd(), b.isRead(), b.isWrite(), b.isExecute(), b.isInitialized()));
  }
}
