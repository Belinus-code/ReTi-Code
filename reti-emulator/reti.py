# Quick and dirty ReTi instruction set Emulator
# Author: Sebastian Walker (https://sebastianwalker.org)
# Inspired by Vorlesung Technische Informatik, SoSe 21
# Prof. Dr. Christoph Scholl, Universität Freiburg

import sys
import argparse
import msvcrt
import os
import ctypes

s = dict()
acc = 0
ind = dict()
pc = 0
old_m2 = 0
input_buffer = []

# Variables to store the original console state
original_mode = None
handle = None
kernel32 = None

if os.name == "nt":
    kernel32 = ctypes.windll.kernel32
    STD_INPUT_HANDLE = -10
    ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200

    handle = kernel32.GetStdHandle(STD_INPUT_HANDLE)
    mode = ctypes.c_uint32()
    kernel32.GetConsoleMode(handle, ctypes.byref(mode))

    # Save the original mode so we can restore it later
    original_mode = mode.value

    # Tell Windows to stop filtering ANSI/VT sequences from the input buffer
    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_INPUT)


def LOAD(i):
    global acc, pc
    acc = s[i]
    pc += 1


def LOADI(i):
    global acc, pc
    acc = i
    pc += 1


def STORE(i):
    global pc
    s[i] = acc
    pc += 1


def ADD(i):
    global acc, pc
    acc += s[i]
    pc += 1


def SUB(i):
    global acc, pc
    acc -= s[i]
    pc += 1


def ADDI(i):
    global acc, pc
    acc += i
    pc += 1


def SUBI(i):
    global acc, pc
    acc -= i
    pc += 1


def LOADIN(j, i):
    global acc, pc
    acc = s[ind[j] + i]
    pc += 1


def STOREIN(j, i):
    global pc
    s[ind[j] + i] = acc
    pc += 1


def MOVE(st, d):
    global pc
    set_value_to(d, get_value_from(st))
    if d != "pc":
        pc += 1


def JUMP(i):
    global pc
    pc += i


def JUMPC(conditional, i):
    global pc
    pc = pc + i if should_jump(conditional) else pc + 1


def PRINT(i):
    global pc
    print(s[i])
    pc += 1


def PRINTC(i):
    global pc
    val = s[i]
    try:
        if 0 <= val <= 255:
            print(chr(val), end="", flush=True)
        else:
            print("?", end="", flush=True)
    except Exception:
        print("?", end="", flush=True)
    pc += 1


def READ(offset):
    global acc, pc, input_buffer

    # 1. Zuerst schauen, ob wir noch Zeichen im Puffer haben!
    if input_buffer:
        acc = input_buffer.pop(0)
        pc += 1
        return

    if msvcrt.kbhit():
        first_byte = msvcrt.getch()
        val = ord(first_byte)

        # 2. Klassische Windows-Sondertasten
        if first_byte in [b"\x00", b"\xe0"]:
            second_byte = msvcrt.getch()
            acc = (val << 8) | ord(second_byte)

        # 3. VT100 ANSI-Sequenzen (Surface / Windows Terminal)
        elif val == 27 and msvcrt.kbhit():
            second_byte = msvcrt.getch()
            if second_byte == b"[":
                third_byte = msvcrt.getch()
                if third_byte == b"D":
                    acc = 57419
                elif third_byte == b"C":
                    acc = 57421
                elif third_byte == b"A":
                    acc = 57416
                elif third_byte == b"B":
                    acc = 57424
                else:
                    # Es war keine Pfeiltaste! (z.B. ESC [ 2 4 ; 1 0 R)
                    # Wir geben ESC zurück und retten die zu viel gelesenen Zeichen in den Puffer
                    acc = 27
                    input_buffer.append(ord(second_byte))
                    input_buffer.append(ord(third_byte))
            else:
                # Es war ESC gefolgt von etwas anderem
                acc = 27
                input_buffer.append(ord(second_byte))

        # 4. Normale Zeichen & Backspace Fix
        else:
            acc = val
            if acc == 127:
                acc = 8

        pc += 1
    else:
        pc += offset


def get_value_from(st):
    st = st.lower()

    if st == "acc":
        return acc

    if st == "in1":
        return ind[1]

    if st == "in2":
        return ind[2]

    if st == "pc":
        return pc


def set_value_to(d, value):
    d = d.lower()

    global acc, ind, pc
    if d == "acc":
        acc = value

    if d == "in1":
        ind[1] = value

    if d == "in2":
        ind[2] = value

    if d == "pc":
        pc = value


def should_jump(conditional):
    if conditional == "<":
        return acc < 0

    if conditional == "=":
        return acc == 0

    if conditional == ">":
        return acc > 0

    if conditional == "<=":
        return acc <= 0

    if conditional == "!=":
        return acc != 0

    if conditional == ">=":
        return acc >= 0

    raise NotImplementedError(
        f"conditional jump JUMPC {conditional} using invalid condition {conditional}"
    )


def read_instructions(path: str):
    with open(path, "r", encoding="utf-8") as file:
        return [
            ([token for token in line.split("#")[0].split() if token], line_num)
            for line_num, line in enumerate(file, start=1)
            if line.strip() and not line.strip().startswith("#")
        ]


def execute_instruction(instruction, instructions):
    pc_before = pc

    name = instruction[0]
    arg1 = prepare_argument(instruction[1])

    if len(instruction) > 2:
        arg2 = prepare_argument(instruction[2])
        globals()[name](arg1, arg2)
    else:
        globals()[name](arg1)

    return pc_before == pc and instruction[0] != "READ"


def prepare_argument(value):
    try:
        return int(value)
    except ValueError:
        return value


def run(args):
    instructions = read_instructions(args.path)
    verbose = args.verbose

    while True:
        if pc >= len(instructions):
            print("\nInstruction for PC = " + str(pc) + " does not exist, aborting")
            break

        instruction, line = instructions[pc]

        if verbose:
            print(instruction)

        try:
            looped = execute_instruction(instruction, instructions)
        except:
            print("Error in Line " + str(line) + ": " + str(instruction))
            raise

        if looped:
            break


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Emulator for Reti")
        parser.add_argument("path", help="Path to the code file")
        parser.add_argument(
            "-v", "--verbose", action="store_true", help="Enable Verbose Output"
        )
        parser.add_argument(
            "-i", "--input", help="Path to the memory input file", default=None
        )
        parser.add_argument(
            "-io", "--input_offset", help="Copy offset for memory input file", default=0
        )
        parser.add_argument(
            "-o",
            "--output",
            help="Path to the memory copy file after program end",
            default=None,
        )
        parser.add_argument(
            "-oo",
            "--output_offset",
            help="Offset to start copying memory to output file",
            default=0,
        )
        args = parser.parse_args()

        if args.input is not None:
            try:
                with open(args.input, "r", encoding="utf-8") as file:
                    for line in file:
                        index = int(line[0 : line.find(":")])
                        if index < args.input_offset:
                            continue
                        content = int(line[line.find(":") + 1 :])
                        s[index] = content
            except Exception as e:
                print(e)
        run(args)
        if args.output is not None:
            try:
                with open(args.output, "w", encoding="utf-8") as file:
                    index_list = s.keys()
                    index_list = sorted(index_list)
                    for index in index_list:
                        if index < args.output_offset:
                            continue
                        file.write(str(index) + ":" + str(s[index]) + "\n")
            except Exception as e:
                print("Error while writing output file:" + e)
    except KeyboardInterrupt:
        # Catch Ctrl+C and exit silently without throwing a traceback
        pass
    finally:
        # Ensure the console mode is restored even if the script crashes or is interrupted
        if os.name == "nt" and original_mode is not None:
            kernel32.SetConsoleMode(handle, original_mode)
