# LINOX

A small cooperative multitasking kernel for the ReTI, written in ReTI assembly.
It runs on the classic ReTI (`IN2` is used as stack pointer) and provides processes, a scheduler, a heap
and message passing.
Right now, it contains a simple Process that reads every Key-Input with a system call and prints the ascii-Value of the key to the screen. Pressing ESC will shutdown the kernel and all other processes.

## Run

The main program is [`target/scheduler.txt`](target/scheduler.txt). Start it with the emulator:

```
python reti-emulator/reti.py target/scheduler.txt
```

## Build

`target/scheduler.txt` is generated from [`kernel/scheduler_labels.txt`](kernel/scheduler_labels.txt),
which includes all other source files, using the [ReTi-Label-Parser](https://github.com/Belinus-code/ReTi-Label-Parser):

```
python labels.py kernel/scheduler_labels.txt -c -i -o target/scheduler.txt
```

## Documentation

- [`kernel/doc.md`](kernel/doc.md): memory layout, PCB, process lifecycle (CREATE_TASK, EXIT, TERMINATE, WAIT, SEND, RECEIVE), YIELD, calling convention, heap
- [`kernel/ANSI.md`](kernel/ANSI.md): notes on ANSI escape sequences

## Source overview (`kernel/`)

| File | Content |
| --- | --- |
| `scheduler_labels.txt` | Entry point, scheduler, YIELD, WAIT / SEND / RECEIVE, process deletion |
| `kernel_labels.txt` | Kernel process, input buffer, CREATE_TASK |
| `stack_call_labels.txt` | CALL / RETURN convention, stack setup |
| `malloc_labels.txt`, `heap_labels.txt` | Heap (MALLOC, FREE, REALLOC, ...) |
| `string_*.txt`, `ascii_labels.txt`, `math_labels.txt` | String, ASCII and math helpers |
| `defines.txt` | Constants (PCB layout, states, error codes) |

## Emulator

[`reti-emulator/`](reti-emulator) is a modified copy of [sebwalk/reti-emulator](https://github.com/sebwalk/reti-emulator)
(MIT, see [`license.md`](reti-emulator/license.md)).
