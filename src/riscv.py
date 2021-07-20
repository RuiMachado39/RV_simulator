import struct
import glob
from elftools.elf.elffile import ELFFile
from enum import Enum

#register file CPU is 32 bits
regfile = [0]*33
PC = 32

class Opcode(Enum):
    LUI = 0b0110111
    AUIPC = 0b0010111


#4k memory
mem = '\x00'*0x1000

def r32(addr):
    assert addr >= 0 and addr < len(mem)
    return struct.unpack("I",mem[addr:addr+4])[0]

def dump():
    pp = []
    for i in range(32):
        if i != 0 and i % 8 == 0:
            pp += "\n"
        pp += " x%3s: %08x" % ("x%d" % i, regfile[i])
    pp += "\n  PC: %08x" % regfile[PC]
    print(''.join(pp))

def step():
    #instruction fetch
    ins = r32(regfile[PC])
    #instruction decode
    dump()
    #instruction execute
    #memory access
    #write-back
    return False



if __name__ == "__main__":
    codefile = r"C:\Users\Rui\Projects\RV_simulator\src\program_code.elf"
    print("test", codefile)
    f = open(codefile, 'rb')
    elf = ELFFile(f)
    text = elf.get_section_by_name('.text.init').data()
    mem = text + mem[len(text):]
    regfile[PC] = 0x00
    while step():
        pass    
    

