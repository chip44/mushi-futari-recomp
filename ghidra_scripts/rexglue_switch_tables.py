import os
import re

from ghidra.ghidra_builtins import currentProgram, println
from ghidra.program.model.address import Address
from ghidra.program.model.listing import Instruction
from ghidra.program.model.mem import MemoryAccessException

listing = currentProgram.getListing()
func_man = currentProgram.getFunctionManager()
memory = currentProgram.getMemory()
exec_set = memory.getExecuteSet()
space = currentProgram.getAddressFactory().getDefaultAddressSpace()


def A(address: int) -> Address:
    return space.getAddress(address)


def is_code_addr(address: int) -> bool:
    return address % 4 == 0 and exec_set.contains(A(address))


def read_word(offset: int) -> int | None:
    try:
        return memory.getInt(A(offset)) & 0xFFFFFFFF
    except MemoryAccessException:
        return None


def reg_name(instruction: Instruction, operand_idx: int) -> int | None:
    reg = instruction.getRegister(operand_idx)
    if reg is not None and re.match(r"^r\d+$", reg.getName()):
        return int(reg.getName()[1:])
    return None


def find_bounds_check(bctr: Instruction) -> tuple[int, int | None] | tuple[None, None]:
    """
    walk back from the bctr to the cmplwi bounds check.
    returns (index register, entry count or None)
    """
    curr = bctr
    for _ in range(24):
        curr = listing.getInstructionBefore(curr.getAddress(0))
        if curr is None:
            break

        m = curr.getMnemonicString().lower()
        if not m.startswith("cmp"):
            continue

        reg = None
        imm = None
        for i in range(curr.getNumOperands()):
            r = reg_name(curr, i)
            if r is not None and reg is None:
                reg = r
            scalar = curr.getScalar(i)
            if scalar is not None:
                imm = scalar.getUnsignedValue()

        if reg is not None:
            count = (imm + 1) if imm is not None else None
            return reg, count

    return None, None


def find_table_bases(bctr: Instruction) -> list[int]:
    """
    find candidate table addresses: right after the bctr, and lis+addi (hi/lo) before it
    """
    bases = [bctr.getAddress(0).getOffset() + 4]
    window: list[Instruction] = []

    curr = bctr
    for _ in range(14):
        curr = listing.getInstructionBefore(curr.getAddress(0))
        if curr is None:
            break
        window.append(curr)

    window.reverse()

    hi = {}
    for ins in window:
        m = ins.getMnemonicString().lower()
        if m in ("lis", "addis"):
            rd = reg_name(ins, 0)
            scalar = ins.getScalar(ins.getNumOperands() - 1)
            if rd is not None and scalar is not None:
                hi[rd] = (scalar.getUnsignedValue() & 0xFFFF) << 16
        elif m == "addi":
            rd = reg_name(ins, 0)
            ra = reg_name(ins, 1)
            scalar = ins.getScalar(ins.getNumOperands() - 1)
            if rd is not None and ra in hi and scalar is not None:
                lo = scalar.getUnsignedValue() & 0xFFFF
                if lo >= 0x8000:
                    lo -= 0x10000
                bases.append((hi[ra] + lo) & 0xFFFFFFFF)

    return bases


def read_table(base: int, count: int | None) -> list[int]:
    words: list[int] = []

    if count is not None:
        for i in range(count):
            word = read_word(base + i * 4)
            if word is None or not is_code_addr(word):
                return []
            words.append(word)
        return words

    # no bounds check found, read while it still looks like table data
    while len(words) < 1024:
        slot = base + len(words) * 4
        word = read_word(slot)
        if word is None or not is_code_addr(word):
            break
        if listing.getInstructionAt(A(slot)) is not None:
            break
        words.append(word)

    return words


results = []

instruction_iter = listing.getInstructions(exec_set, True)
for instruction in instruction_iter:
    if instruction.getMnemonicString().lower() != "bctr":
        continue
    bctr_offset = instruction.getAddress(0).getOffset()

    targets: set[int] = set()
    for ref in instruction.getReferencesFrom():
        ref_type = ref.getReferenceType()
        if ref_type.isJump() and ref_type.isComputed():
            targets.add(ref.getToAddress().getOffset())
    if not targets:
        continue  # plain indirect tail call, not a switch

    func = func_man.getFunctionContaining(instruction.getAddress(0))

    reg, count = find_bounds_check(instruction)

    best = None
    best_score = -1
    for base in find_table_bases(instruction):
        words = read_table(base, count)
        if not words:
            continue
        score = len(targets & set(words))
        if score > best_score:
            best, best_score = words, score

    if best is None or best_score <= 0:
        # could not find the table
        continue

    words = best
    results.append((bctr_offset, reg, words))


out_path = os.path.abspath("ghidra_switch_tables.toml")
with open(out_path, "w") as out:
    for bctr_offset, reg, words in results:
        out.write("[[switch_tables]]\n")
        out.write(f"address = 0x{bctr_offset:08X}\n")
        if reg is None:
            reg = 11
        out.write(f"register = {reg}\n")
        out.write("labels = [\n")
        out.writelines(
            "    " + ", ".join(f"0x{v:08X}" for v in words[i : i + 4]) + ",\n"
            for i in range(0, len(words), 4)
        )
        out.write("]\n\n")

println(f"written to: {out_path}")
