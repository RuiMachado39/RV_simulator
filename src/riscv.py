from _typeshed import Self
from os import truncate
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
            Self.regs[index] = value & 0xFFFFFFFF


regfile = Regfile()    
PC = 32

class Opcode(Enum):
    LUI = 0b0110111    #load upper immediate
    AUIPC = 0b0010111  #add upper immediate to PC
    JAL = 0b1101111    #jump
    JALR = 0b1100111    #jump register
    BRANCH = 0b1100011 #beq, bne, blt, bge, bltu, bgeu
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

    BEQ = 0b000
    BNE = 0b001
    BLT = 0b100
    BGE = 0b101
    BLTU = 0b110
    BGEU = 0b111


def decode(ins, msb, lsb):
    return (ins >> lsb) & ((1 << (msb - lsb + 1))-1)

#4k memory
mem = '\x00'*0x1000

def r32(addr):
    assert addr >= 0 and addr < len(mem)
    return struct.unpack("I",mem[addr:addr+4])[0]


def sign_extend(value, bits):
    if value >> (bits-1) == 1:
        return (1 << bits) - value
    else:
        return value 

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
    if op == Opcode.JAL:
        #J-type instruction
        imm = decode(ins,31,12)
        rd = decode(ins, 11,7)
        offset = decode(imm, 32,31) << 20 | decode(imm, 19,12) << 12 | decode(imm, 21, 20) << 11 | decode(imm, 30, 21) << 1 
        regfile[rd] = regfile[PC] + 4
        regfile[PC] += offset
        return True
    elif op == Opcode.JALR:
        #I-type instruction
        rd = decode(ins, 11,7)
        func3 = Func3(decode(ins,14, 12))
        assert func3 == Func3.ADDI #Func3 field must be 0 on JALR instructions which is the ADDI/ADD code
        rs1 = decode(ins, 19, 15)
        imm = sign_extend(decode(ins, 31, 20), 12)
        regfile[rd] = regfile[PC] + 4
        regfile[PC] = regfile[rs1] + imm
        return True
    elif op == Opcode.AUIPC:
        #U-type instruction
        rd = decode(ins, 11, 7)
        imm = decode(ins, 31, 12)
        regfile[rd] = regfile[PC] + imm
        return True
    elif op == Opcode.ALUR:
        #R-type instruction
        rd = decode(ins, 11, 7)
        rs1 = decode(ins, 19, 15)
        rs2 = decode(ins, 24, 20)
        func7 = decode(ins, 31, 25)
        func3 = Func3(decode(ins,14, 12))
        if func3 == Func3.ADDI:
            regfile[rd] = regfile[rs1] + regfile [rs2]
        else:
            dump()
            raise Exception("Func3 error - Unknown func3 field")
        return True
    elif op == Opcode.ALUI:
        #I-type instruction
        rd = decode(ins, 11, 7)
        rs1 = decode(ins, 19, 15)
        func3 = Func3(decode(ins, 14, 12))
        imm = decode(ins, 31, 20)
        if func3 == Func3.ADDI:
            regfile[rd] = regfile[rs1] + imm
        elif func3 == Func3.SLLI:
            regfile[rd] = regfile[rs1] << imm
        elif func3 == Func3.SRLI:
            regfile[rd] = regfile[rs1] >> imm
        else:
            dump()
            raise Exception("Func3 error - Unknown func3 field")
        regfile[PC] += 4
        return True
    elif op == Opcode.BRANCH:
        #B-type instruction
        func3 = Func3(decode(ins, 14, 12))
        rs1 = decode(ins, 19, 15)
        rs2 = decode(ins, 24, 20)
        imm = decode(ins, 32,31) << 12 | decode(ins, 8, 7) << 11 | decode(ins, 30, 25) << 5 | decode(ins, 11, 8) << 1
        #offset = sign_extend(imm, 22)
        if func3 == Func3.BNE:
            if regfile[rs1] != regfile[rs2]:
                regfile[PC] += imm
                return True
        else:
            dump()
            raise Exception("Opcode error - Unknown opcode")

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
    

