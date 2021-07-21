import struct
import glob
from elftools.elf.elffile import ELFFile
from enum import Enum

#register file CPU is 32 bits
regfile = [0]*33
PC = 32

class Opcode(Enum):
    LUI = 0b0110111    #load upper immediate
    AUIPC = 0b0010111  #add upper immediate to PC
    JAL = 0b1101111    #jump
    BRANCH = 0b1100111
    LOAD = 0b0000011
    STORE = 0b0100011
    ALUI = 0b0010011
    ALUR = 0b0110011
    FENCE = 0b0001111
    SYSTEM = 0b1110011

def decode(ins, msb, lsb):
    return (ins >> lsb) & ((1 << (msb - lsb + 1))-1)

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
    op = Opcode(decode(ins,6,0))
    if Opcode.JAL == op:
        imm = decode(ins,31,12) #TO DO: change decode of the immediate, bits in JAL come not ordered!!!
        rd = decode(ins, 11,7)
        assert rd == 0

        pass

    print(hex(ins), op)
    dump()
    #instruction execute
    #memory access
    #write-back
    return False



if __name__ == "__main__":
    #read code from elf file
    codefile = r"C:\Users\Rui\Projects\RV_simulator\src\program_code.elf"
    print("test", codefile)
    f = open(codefile, 'rb')
    elf = ELFFile(f)
    text = elf.get_section_by_name('.text.init').data()
    mem = text + mem[len(text):]
    regfile[PC] = 0x00
    #TO DO: read code from hex file and give user the option to select the format
    while step():
        pass    
    

