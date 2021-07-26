from _typeshed import Self
import struct
import glob
from elftools.elf.elffile import ELFFile
from enum import Enum

#register file CPU is 32 bits
regfile = [0]*33
class Regfile:
    def __init__(self):
        self.regs = [0]*33
    
    def __getitem__(self, index):
        return self.regs[index]

    def __setitem__(self, index, value):
        if index == 0:
            return
        else:
            Self.regs[index] = value


regfile = Regfile()    
PC = 32

class Opcode(Enum):
    LUI = 0b0110111    #load upper immediate
    AUIPC = 0b0010111  #add upper immediate to PC
    JAL = 0b1101111    #jump
    BRANCH = 0b1100111
    LOAD = 0b0000011
    STORE = 0b0100011
    ALUI = 0b0010011 #IMM
    ALUR = 0b0110011 #OP
    MISC = 0b0001111 #FENCE instructions
    SYSTEM = 0b1110011


class Func3(Enum):
    ADDI = 0b000 #also ADD, SUB
    SLTI = 0b010  #also SLT
    SLTIU = 0b011 #also SLTU
    XORI = 0b100 #also XOR
    ORI = 0b110 #also OR
    ANDI = 0b111 #also AND
    SLLI = 0b001 #also SLL
    SRLI = 0b101 #also SRAI, SRL, SRA 



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
        #J-type instruction
        imm = decode(ins,31,12) #TO DO: change decode of the immediate, bits in JAL come not ordered!!!
        rd = decode(ins, 11,7)
        offset = decode(imm, 31,30) << 20 | decode(imm, 19,12) << 12 | decode(imm, 21, 20) << 11 | decode(imm, 30, 21) << 1 
        regfile[PC] += offset
        return True
    elif op == Opcode.AUIPC:
        rd = decode(ins, 11, 7)
        imm = decode(ins, 31, 12)
        regfile[rd] = regfile[PC] + imm
        return True
    elif op == Opcode.ALUI:
        #I-type instruction
        rd = decode(ins, 11, 7)
        rs1 = decode(ins, 19, 15)
        func3 = Func3(decode(ins, 14, 12))
        imm = decode(ins, 31, 20)
        if func3 == Func3.ADDI:
            regfile[rd] = regfile[rs1] + imm
        if func3 == Func3.SLLI:
            regfile[rd] = regfile[rs1] << imm
        else:
            dump()
            raise Exception("Func3 error - Unknown func3 field")
        regfile[PC] += 4
        return True
    elif op == Opcode.SYSTEM:
        pass
    else:
        dump()
        raise Exception("Opcode error - Unknown opcode")



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
    

