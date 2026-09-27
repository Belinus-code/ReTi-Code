# LINOX
## Stack
1. Stack starts at M(2048)
2. Stack Pointer is *always* at IN2
3. Stack Pointer always points to next free cell
4. Stack grows upwards (Pointer gets bigger)

## CALL
### Stack Build:
- M(IN2-1): Absolute Return Adress of Callee
- M(IN2-2): Amount of Arguments for this Method on Stack 
- M(IN2-3) to M(IN2-(2+n)): Arguments
- M(IN2-(3+n)) to M(IN2-(8+n)): Copy of M(0) to M(4) of Callee
- M(IN2-(9+n)): IN1 Register of Callee

### Calling a Method
- Amount of Argument or Return Values (use bigger one) are to be stored at M(1026)
- Amount gets set to zero after every Method Call
- All arguments are to be stored at M(1030) and following
- Store relative offset to method in M(1024) (use label parser for offset)
- Last thing before call must always be: MOVE PC ACC; STORE 1025; JUMP CALL
- Call copys all arguments to stack automatically, Pointer to first Arg gets stored at M(0) and IN1
- Return Values are to placed at same Place at Arguments where copied to on stack
- Return Method will copy all Arguments (or Return values is placed there) from Stack to M(1030) and following


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
- Heap grows upwards

### MALLOC(n)
- Argument 1: Size of requested Block
- Checks every Frame if usable:
    - resize if needed/possible. If between new frame and next frame is less than 4 cells, no need to resize because every Frame needs at least 4 cells
    - if resize usefull, resize this frame, create new unused frame between new and next frame
- If no free space found (Pointer >= Heap Top Pointer), create new frame at end


### FREE(pointer)
- Argument 1: Heap-Pointer to Data (not header block!)
- Sets Block to unused
- Updates Top Heap Pointer if this is last Block
- Checks if Block after this Block is used, if not, fuse (add block lengths together)
- Checks if Block before this Block is used, if not, fuse with this

### REALLOC(pointer, n)
- Argument 1: Heap-Pointer to Data (not header block!)
- Argument 2: Wanted Data Size of new Heap Block
- Checks for Shrinking
    - Check is Splitt is possible, do so if possible
    - If not, dont change anything
    - return original Pointer
- Check if Orignal Frame is big enough
    - Dont change anything
    - Return original pointer
- Check for Expansion
    - Check if frame is last on heap
    - Check if next Frame is free
        - Check if next Frame is big enough
            - Fuse if possible
            - Check if Fused Frame could be Splitt, do so if possible
            - Return original pointer
- Get new Frame
    - Malloc new Frame
    - Copy old Frame
    - Return new Pointer

### CALLOC(n)
Same as Malloc(n) but filles complete Block with zeros.

# Strings
- For easy Print, every Ascii Character is stored in M(<char value> + 100)
    - E.g.: a = M(197) because ord(a) = 97 -> 97 + 100 = 197
- Every String ends with a Zero Terminator (=0)
## ATOI
    - 1. Argument: Pointer to String Buffer
    - 2. Argument (Optional): Offset to first Digit (Zero if not provided)
    - First char after aplying offset must be a digit or '-' value
    - If first digit is no digit, zero will be returned
    - Stops Parsing once a non-digit character has been found
    - Parsed Value will be at M(1030)
    - If Offset was provided, Offset from buffer-start to first character AFTER last digit is will be returned to M(1031)
## GET_LINE_WIDTH
    - 1. Argument: Pointer to String
    - 2. Argument: Pointer to eof String
    - 3. Argument: Pointer to any Character of specific line
    - Only whole Strings accecepted, no Gap-Strings (split string in two if needed)
    - If target character (third argument) points to newline, it is seen as the end of the current line
    - First Return Value is Amount of visable Characters in Line. -1 if Error
    - Second Return Value is 1 if Line is first Line of String, otherwise 0
    - Third Return Value is 1 if Line is last Line of String, otherwise 0
    - If first Value is -1, second and third Return Value cannot be trusted

## GET_CURSOR_POSITION
    - No input Arguments required, however three Return Arguments, so set amount to 3
    - First Return Value is y-coordinate, starting at 1 at the top of the screen
    - Second Return Value is x-coordinate, starting at 1 at the left side of the screen
    - Third Return Value is a Pointer to an Input-Buffer filled with Keyboard Input values which were
      read during parsing. If there werent any additional Inputs, Pointer will be NULL (0)
    - Warning! If Third Return Value is a real Pointer, you need to free it once dealed with the inputs!

## GET_SCREEN_SIZE
    - No input Arguments required, however three Return Arguments, so set amount to 3
    - First Return Value is the height of the screen
    - Second Return Value is the width of the screen
    - Third Return Value is a Pointer to an Input-Buffer filled with Keyboard Input values which were
      read during parsing. If there werent any additional Inputs, Pointer will be NULL (0)
    - Warning! If Third Return Value is a real Pointer (!=0), you need to free it once dealed with the inputs!


