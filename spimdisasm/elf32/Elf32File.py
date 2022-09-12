#!/usr/bin/env python3

# SPDX-FileCopyrightText: © 2022 Decompollaborate
# SPDX-License-Identifier: MIT

from __future__ import annotations

from .. import common

from .Elf32Constants import Elf32SectionHeaderType
from .Elf32Dyns import Elf32Dyns
from .Elf32Header import Elf32Header
from .Elf32SectionHeaders import Elf32SectionHeaders, Elf32SectionHeaderEntry
from .Elf32StringTable import Elf32StringTable
from .Elf32Syms import Elf32Syms
from .Elf32Rels import Elf32Rels


class Elf32File:
    def __init__(self, array_of_bytes: bytearray):
        self.header = Elf32Header.fromBytearray(array_of_bytes)
        # print(self.header)

        self.strtab: Elf32StringTable | None = None
        self.symtab: Elf32Syms | None = None

        self.dynamic: Elf32Dyns | None = None
        self.dynstr: Elf32StringTable | None = None
        self.dynsym: Elf32Syms | None = None

        self.progbits: dict[common.FileSectionType, Elf32SectionHeaderEntry] = dict()
        self.nobits: Elf32SectionHeaderEntry | None = None

        self.rel: dict[common.FileSectionType, Elf32Rels] = dict()

        self.sectionHeaders = Elf32SectionHeaders(array_of_bytes, self.header.shoff, self.header.shnum)

        shstrtabSectionEntry = self.sectionHeaders.sections[self.header.shstrndx]
        self.shstrtab = Elf32StringTable(array_of_bytes, shstrtabSectionEntry.offset, shstrtabSectionEntry.size)

        for entry in self.sectionHeaders.sections:
            sectionEntryName = self.shstrtab[entry.name]
            # print(sectionEntryName, end="\t ")
            # print(entry)
            if entry.type == Elf32SectionHeaderType.NULL.value:
                continue
            elif entry.type == Elf32SectionHeaderType.PROGBITS.value:
                fileSecType = common.FileSectionType.fromStr(sectionEntryName)
                if fileSecType != common.FileSectionType.Invalid:
                    self.progbits[fileSecType] = entry
                    if fileSecType == common.FileSectionType.Text:
                        self.sectionHeaders.mipsText = entry
                    elif fileSecType == common.FileSectionType.Data:
                        self.sectionHeaders.mipsData = entry
                    common.Utils.printVerbose(sectionEntryName, "size: ", entry.size)
                    common.Utils.printVerbose()
                else:
                    common.Utils.eprint("Unknown PROGBITS found: ", sectionEntryName, entry, "\n")
            elif entry.type == Elf32SectionHeaderType.SYMTAB.value:
                if sectionEntryName == ".symtab":
                    self.symtab = Elf32Syms(array_of_bytes, entry.offset, entry.size)
                    common.Utils.printVerbose()
                    common.Utils.printVerbose("SYMTAB:")
                    for i, sym in enumerate(self.symtab.symbols):
                        common.Utils.printVerbose(i, sym)
                    common.Utils.printVerbose()
                else:
                    common.Utils.eprint("Unknown SYMTAB found: ", sectionEntryName, entry, "\n")
            elif entry.type == Elf32SectionHeaderType.STRTAB.value:
                if sectionEntryName == ".strtab":
                    self.strtab = Elf32StringTable(array_of_bytes, entry.offset, entry.size)
                    common.Utils.printVerbose()
                    common.Utils.printVerbose("STRTAB:")
                    for i, string in enumerate(self.strtab):
                        common.Utils.printVerbose(i, string)
                    common.Utils.printVerbose()
                elif sectionEntryName == ".dynstr":
                    self.dynstr = Elf32StringTable(array_of_bytes, entry.offset, entry.size)
                    # common.GlobalConfig.VERBOSE = True
                    common.Utils.printVerbose()
                    common.Utils.printVerbose("STRTAB:")
                    for i, string in enumerate(self.dynstr):
                        common.Utils.printVerbose(i, string)
                    common.Utils.printVerbose()
                    # common.GlobalConfig.VERBOSE = False
                elif sectionEntryName == ".shstrtab":
                    pass
                else:
                    common.Utils.eprint("Unknown STRTAB found: ", sectionEntryName, entry, "\n")
            # elif entry.type == Elf32SectionHeaderType.RELA.value:
            #     pass
            elif entry.type == Elf32SectionHeaderType.HASH.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.DYNAMIC.value:
                if sectionEntryName == ".dynamic":
                    self.dynamic = Elf32Dyns(array_of_bytes, entry.offset, entry.size)
                    common.Utils.printVerbose()
                    common.Utils.printVerbose("DYNAMIC:")
                    for i, dyn in enumerate(self.dynamic.dyns):
                        common.Utils.printVerbose(i, dyn)
                    common.Utils.printVerbose()
                else:
                    common.Utils.eprint("Unknown NOBITS found: ", sectionEntryName, entry, "\n")
            # elif entry.type == Elf32SectionHeaderType.NOTE.value:
            #     pass
            elif entry.type == Elf32SectionHeaderType.NOBITS.value:
                if sectionEntryName == ".bss":
                    self.nobits = entry
                    common.Utils.printVerbose(sectionEntryName, "size: ", self.nobits.size)
                    common.Utils.printVerbose()
                else:
                    common.Utils.eprint("Unknown NOBITS found: ", sectionEntryName, entry, "\n")
            elif entry.type == Elf32SectionHeaderType.REL.value:
                if sectionEntryName.startswith(".rel."):
                    fileSecType = common.FileSectionType.fromStr(sectionEntryName[4:])
                    if fileSecType != common.FileSectionType.Invalid:
                        self.rel[fileSecType] = Elf32Rels(array_of_bytes, entry.offset, entry.size)
                        common.Utils.printVerbose()
                        common.Utils.printVerbose(f"REL: ({sectionEntryName})")
                        for i, rel in enumerate(self.rel[fileSecType]):
                            common.Utils.printVerbose(i, rel, rel.rType, rel.rSym)
                        common.Utils.printVerbose()
                    else:
                        common.Utils.eprint("Unknown REL subsection found: ", sectionEntryName, entry, "\n")
                else:
                    common.Utils.eprint("Unknown REL found: ", sectionEntryName, entry, "\n")
            elif entry.type == Elf32SectionHeaderType.DYNSYM.value:
                if sectionEntryName == ".dynsym":
                    self.dynsym = Elf32Syms(array_of_bytes, entry.offset, entry.size)
                    # common.GlobalConfig.VERBOSE = True
                    common.Utils.printVerbose()
                    common.Utils.printVerbose("DYNSYM:")
                    for i, sym in enumerate(self.dynsym.symbols):
                        common.Utils.printVerbose(i, sym)
                    common.Utils.printVerbose()
                    # common.GlobalConfig.VERBOSE = False
                else:
                    common.Utils.eprint("Unknown DYNSYM found: ", sectionEntryName, entry, "\n")
            elif entry.type == Elf32SectionHeaderType.MIPS_LIBLIST.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.MIPS_MSYM.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.MIPS_GPTAB.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.MIPS_DEBUG.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.MIPS_REGINFO.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.MIPS_OPTIONS.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.MIPS_SYMBOL_LIB.value:
                # ?
                pass
            elif entry.type == Elf32SectionHeaderType.MIPS_ABIFLAGS.value:
                # ?
                pass
            else:
                common.Utils.eprint("Unknown section header type found:", sectionEntryName, entry, "\n")
