# LINOX
## Stack
1. Stack starts at M(2048)
2. Stack Pointer is *always* at IN2
3. Stack Pointer always points to next free cell

## CALL
### Stack Build:
- M(IN2-1): Absolute Return Adress of Callee
- M(IN2-2): Amount of Arguments for this Method on Stack
- M(IN2-3) to M(IN2-(2+n)): Arguments
- M(IN2-(3+n)) to M(IN2-(8+n)): Copy of M(0) to M(4) of Callee
- M(IN2-(9+n)): IN1 Register of Callee


## HEAP
### HEAP
- Heap startes at M(4096)
- No Heap end right now?
- Heap Top Pointer is at M(4095) and points to beginn of last frame, not to real end
- Every Heap frame with n data cells consists of:
    - M(H): Length of Heap Frame (n+3)
    - M(H+1): Is Frame used? (0: not used, 1: used)
    - M(H+2) to M(H+2+n)
    - M(H+3+n): Length of Heap Frame (n+3)
- Last Block of Heap cannot be unused. Lower Heap-Top Pointer in this case

### MALLOC(n)
- Starts at M(4096)
- Checks every Frame if usable:
    - resize if needed/possible. If between new frame and next frame is less than 4 cells, no need to resize because every Frame needs at least 4 cells
    - if resize usefull, resize this frame, create new unused frame between new and next frame
- If no free space found (Pointer >= Heap Top Pointer), create new frame at end


### FREE(n)
- Sets Block to unused
- Updates Top Heap Pointer if this is last Block
- Checks if Block after this Block is used, if not, fuse (add block lengths together)
- Checks if Block before this Block is used, if not, fuse with this