#!/usr/bin/env python3

# SPDX-FileCopyrightText: © 2022 Decompollaborate
# SPDX-License-Identifier: MIT

from __future__ import annotations

import bisect

from ... import common

from .. import symbols

from . import SectionBase


class SectionBss(SectionBase):
    def __init__(self, context: common.Context, bssVramStart: int, bssVramEnd: int, filename: str):
        super().__init__(context, bssVramStart, filename, bytearray(), common.FileSectionType.Bss)

        self.bssVramStart: int = bssVramStart
        self.bssVramEnd: int = bssVramEnd

        self.bssTotalSize: int = bssVramEnd - bssVramStart

        self.vram = bssVramStart


    def setVram(self, vram: int):
        super().setVram(vram)

        self.bssVramStart = vram
        self.bssVramEnd = vram + self.bssTotalSize

    def analyze(self):
        self.checkAndCreateFirstSymbol()

        # If something that could be a pointer found in data happens to be in the middle of this bss file's addresses space
        # Then consider it as a new bss variable
        for ptr in sorted(self.context.newPointersInData):
            if ptr < self.bssVramStart:
                continue
            if ptr >= self.bssVramEnd:
                break

            # Check if the symbol already exists, in case the user has provided size
            contextSym = self.context.getSymbol(ptr, tryPlusOffset=True)
            if contextSym is None:
                self.context.addSymbol(ptr, None, self.sectionType, isAutogenerated=True)


        offsetSymbolsInSection = self.context.offsetSymbols[common.FileSectionType.Bss]
        bssSymbolOffsets: dict[int, common.ContextSymbol] = {offset: sym for offset, sym in offsetSymbolsInSection.items()}

        for contextSym in self.context.getSymbolRangeIter(self.bssVramStart, self.bssVramEnd):
            # Mark every known symbol that happens to be in this address space as defined
            contextSym.isDefined = True
            contextSym.sectionType = common.FileSectionType.Bss

            # Needs to move this to a list because the algorithm requires to check the size of a bss variable based on the next bss variable' vram
            bssSymbolOffsets[contextSym.vram-self.bssVramStart] = contextSym


        sortedOffsets = sorted(bssSymbolOffsets.items())

        i = 0
        while i < len(sortedOffsets):
            symbolOffset, contextSym = sortedOffsets[i]
            symbolVram = self.bssVramStart + symbolOffset

            # Calculate the space of the bss variable
            space = self.bssTotalSize - symbolOffset
            if i + 1 < len(sortedOffsets):
                nextSymbolOffset, _ = sortedOffsets[i+1]
                if nextSymbolOffset <= self.bssTotalSize:
                    space = nextSymbolOffset - symbolOffset

            sym = symbols.SymbolBss(self.context, symbolOffset + self.inFileOffset, symbolVram, space)
            sym.setCommentOffset(self.commentOffset)
            sym.analyze()
            self.symbolList.append(sym)

            i += 1
