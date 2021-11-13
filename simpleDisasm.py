#!/usr/bin/python3

from __future__ import annotations

import argparse

from mips.Utils import *
from mips.GlobalConfig import GlobalConfig
from mips.MipsText import Text
from mips.MipsFileGeneric import FileGeneric
from mips.MipsFileOverlay import FileOverlay
from mips.MipsFileCode import FileCode
from mips.MipsFileBoot import FileBoot
from mips.MipsContext import Context
from mips.MipsSplitEntry import readSplitsFromCsv
from mips.ZeldaTables import DmaEntry, getDmaAddresses, OverlayTableEntry
from mips import ZeldaOffsets


def simpleDisasmFile(path: str, outputPath: str, offsetStart: int, offsetEnd: int, vram: int, context: Context):
    array_of_bytes = readFileAsBytearray(path)

    array_of_bytes = array_of_bytes
    if offsetEnd >= 0:
        print(f"Parsing until offset {toHex(offsetEnd, 2)}")
        array_of_bytes = array_of_bytes[:offsetEnd]
    if offsetStart >= 0:
        print(f"Parsing since offset {toHex(offsetStart, 2)}")
        array_of_bytes = array_of_bytes[offsetStart:]

    f = Text(array_of_bytes, "raw", "ver", context)

    if vram >= 0:
        print(f"Using VRAM {toHex(vram, 2)}")
        f.setVRamStart(vram)

    print("Analzing")
    f.analyze()

    print()
    print(f"Found {f.nFuncs} functions.")

    nBoundaries = len(f.fileBoundaries)
    if nBoundaries > 0:
        print(f"Found {nBoundaries} file boundaries.")

        for i in range(len(f.fileBoundaries)-1):
            start = f.fileBoundaries[i]
            end = f.fileBoundaries[i+1]

            functionsInBoundary = 0
            for func in f.functions:
                funcOffset = func.vram - vram
                if start <= funcOffset < end:
                    functionsInBoundary += 1
            print("\t", toHex(start, 6)[2:], toHex(end-start, 3)[2:], "\t functions:", functionsInBoundary)


        start = f.fileBoundaries[-1]
        end = f.size + f.offset

        functionsInBoundary = 0
        for func in f.functions:
            funcOffset = func.vram - vram
            if start <= funcOffset < end:
                functionsInBoundary += 1
        print("\t", toHex(start, 6)[2:], toHex(end-start, 3)[2:], "\t functions:", functionsInBoundary)

        print()

    print(f"Writing files to {outputPath}")
    f.saveToFile(outputPath)

    print()
    print("Disassembling complete!")
    print("Goodbye.")


def disassemblerMain():
    description = ""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("binary", help="Path to input binary")
    parser.add_argument("output", help="Path to output")
    parser.add_argument("--start", help="", default="0")
    parser.add_argument("--end", help="",  default="0xFFFFFF")
    parser.add_argument("--vram", help="Set the VRAM address", default="-1")
    parser.add_argument("--save-context", help="Saves the context to a file. The provided filename will be suffixed with the corresponding version.", metavar="FILENAME")
    parser.add_argument("--functions", help="Path to a functions csv")
    parser.add_argument("--variables", help="Path to a variables csv")
    args = parser.parse_args()

    GlobalConfig.REMOVE_POINTERS = False
    GlobalConfig.IGNORE_BRANCHES = False
    GlobalConfig.IGNORE_04 = False
    GlobalConfig.IGNORE_06 = False
    GlobalConfig.IGNORE_80 = False
    GlobalConfig.WRITE_BINARY = False
    GlobalConfig.ASM_COMMENT = True

    context = Context()
    if args.functions is not None:
        context.readFunctionsCsv(args.functions)
    if args.variables is not None:
        context.readVariablesCsv(args.variables)

    simpleDisasmFile(args.binary, args.output, int(args.start, 16), int(args.end, 16), int(args.vram, 16), context)

    if args.save_context is not None:
        head, tail = os.path.split(args.save_context)
        os.makedirs(head, exist_ok=True)
        name = tail
        extension = ""
        if "." in tail:
            *aux, extension = tail.split(".")
            name = ".".join(aux)
            extension = "." + extension
        name = os.path.join(head, name)
        context.saveContextToFile(f"{name}_{extension}")


if __name__ == "__main__":
    disassemblerMain()
