#!/usr/bin/env python3

# SPDX-FileCopyrightText: © 2022 Decompollaborate
# SPDX-License-Identifier: MIT

from __future__ import annotations

import enum


# a.k.a. SHT (section header type)
@enum.unique
class Elf32SectionHeaderType(enum.Enum):
    NULL            =  0
    PROGBITS        =  1
    SYMTAB          =  2
    STRTAB          =  3
    RELA            =  4
    HASH            =  5
    DYNAMIC         =  6
    NOTE            =  7
    NOBITS          =  8
    REL             =  9
    DYNSYM          = 11

    MIPS_LIBLIST    = 0x70000000
    MIPS_MSYM       = 0x70000001
    MIPS_GPTAB      = 0x70000003
    MIPS_DEBUG      = 0x70000005
    MIPS_REGINFO    = 0x70000006
    MIPS_OPTIONS    = 0x7000000D
    MIPS_SYMBOL_LIB = 0x70000020
    MIPS_ABIFLAGS   = 0x7000002A


# a.k.a. STT (symbol table type)
@enum.unique
class Elf32SymbolTableType(enum.Enum):
    NOTYPE       =  0
    OBJECT       =  1
    FUNC         =  2
    SECTION      =  3
    FILE         =  4
    COMMON       =  5
    TLS          =  6
    NUM          =  7

# a.k.a. STB (symbol table binding)
@enum.unique
class Elf32SymbolTableBinding(enum.Enum):
    LOCAL       =  0
    GLOBAL      =  1
    WEAK        =  2
    LOOS        = 10
    HIOS        = 12
    LOPROC      = 13
    HIPROC      = 14


# a.k.a. SHN (section header number)
@enum.unique
class Elf32SectionHeaderNumber(enum.Enum):
    UNDEF           = 0
    COMMON          = 0xFFF2
    MIPS_ACOMMON    = 0xFF00
    MIPS_TEXT       = 0xFF01
    MIPS_DATA       = 0xFF02
