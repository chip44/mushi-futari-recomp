import bisect
import os

from ghidra.ghidra_builtins import currentProgram, println
from ghidra.program.model.symbol import RefType

listing = currentProgram.getListing()
func_man = currentProgram.getFunctionManager()
ref_man = currentProgram.getReferenceManager()
exec_set = currentProgram.getMemory().getExecuteSet()
space = currentProgram.getAddressFactory().getDefaultAddressSpace()

MAX_INSTRUCTIONS = 20000  # safety cap per function

func_entries: set[int] = set()
for f in func_man.getFunctions(True):
    func_entries.add(f.getEntryPoint().getOffset())

targets: list[int] = []

# collect every code address that has a plain data/pointer reference to it
addr_iter = ref_man.getReferenceDestinationIterator(exec_set, True)
while addr_iter.hasNext():
    address = addr_iter.next()
    has_ptr = False
    for ref in ref_man.getReferencesTo(address):
        if ref.getReferenceType() == RefType.DATA:
            has_ptr = True
            break
    if not has_ptr:
        continue

    offset = address.getOffset()
    if offset % 4 != 0:
        # not aligned to 4 bytes
        continue
    if listing.getInstructionAt(address) is None:
        # not disassembled
        continue
    container = func_man.getFunctionContaining(address)
    if container is not None and container.getEntryPoint().getOffset() != offset:
        # most likely a switch case from a jump table, rexglue handles those differently
        continue
    if offset in func_entries:
        # rexglue usually finds these on its own. overriding its boundaries with ours can break things
        continue

    targets.append(offset)


bounds = sorted(set(targets) | func_entries)


def find_end(start_offset: int) -> int:
    """
    walk the code from the target to find where it ends
    """
    # hard limit: the next function / pointer target after start
    i = bisect.bisect_right(bounds, start_offset)
    limit = bounds[i] if i < len(bounds) else 0xFFFFFFFF

    offset = start_offset
    furthest_offset = start_offset
    count = 0
    while count < MAX_INSTRUCTIONS:
        count += 1
        instruction = listing.getInstructionAt(space.getAddress(offset))
        if instruction is None:
            if offset < furthest_offset:
                # undisassembled bytes in the middle of a function (a branch jumps over them). PPC is fixed width, so just step over one word.
                offset += 4
                continue
            break

        if instruction.getFlowType().isJump():
            for address in instruction.getFlows():
                o = address.getOffset()
                if o > offset and o < limit and o > furthest_offset:
                    furthest_offset = o

        offset += instruction.getLength()
        if offset >= limit:
            offset = limit
            break

        # blr/bctr/b: done, unless a branch still jumps further down
        if instruction.getFallThrough() is None and offset > furthest_offset:
            break

    return offset


out_path = os.path.abspath("ghidra_indirect_functions.toml")
with open(out_path, "w") as out:
    out.write("[functions]\n")
    for offset in sorted(targets):
        end = find_end(offset)
        out.write(f"0x{offset:08X} = {{ end = 0x{end:08X} }}\n")

println(f"written to: {out_path}")
