# LINOX
## Memory Architecture
 - 0000 - 0009: Working Registers (automatic copy to stack on function-call)
 - 0100 - 0227: Ascii Lookup Table (M(100+ord(X)) = ord(X))
 - 1000 - 1010: Multi-Tasking
 - 1024 - 2047: Calling a Method
 - 2048 - 4094: Global Stack
 - 4095 - XXXX: Heap

## Multi-Tasking
 - M(1000) cointains current PID (Process-ID)
 - M(1001) contains Pointer to current PCB on Heap (Process-Controll-Block)
 - M(1002) Amount of Processes 
 - M(1003) Pointer to Kernel-PCB
 - M(1004) Boot-Stack Pointer (Zero when Boot is done)

 - PID 0 does not exist
 - PID 1 is Kernel

 ### Boot
 - Boot-Stack of size 256
 - Prepares Process-Controll-Block of Kernel and starts it
 
 ### PCB
 - NEXT_PCB (Points to first if this is last PCB)
 - PREV_PCB (Points to last if this if first PCB)
 - PID
 - STATE
    - 0: Ready (Waiting for runtime)
    - 1: Running (currently running)
    - 2: Waiting ()
    - 3: Terminated (Process is closed, PCB wants to be cleared)
 - WAIT-REASON
    - 0: No Reason (In this Case, STATE cannot be Waiting)
    - 1: Waiting for Input  (Waiting that Key is available)
    - 2: Waiting for Output (Waiting for specific Mailbox to free)
    - 3: Waiting for Child-Process  (Waiting for specific Child-Process to terminate)
    - 4: Waiting for Mailbox    (Waiting for Message in Mailbox)
 - WAIT-Data:
    - Waiting for Input: No Data for now
    - Waiting for Output: PID to send Mail to
    - Waiting for Child-Process: Child-PID
    - Waiting for Mailbox: No Data for now
 - STACK-POINTER
 - STACK-BASE
 - PARENT-PID
    - Creator of this Process
    - Only Parent and Kernel can kill this Process
    - Only Parent and Kernel can wait & read Exit-Code
 - EXIT-CODE
    - If a Process exits itself, it can write a value in here
    - If a process gets Terminated, this gets set to -1
 - MAILBOX
    - Every Process can write a value here
 - MAILSENDER
    - When a Process is writing a Message into MAILBOX, write its PID into here!

 - Every Process can read it's own PCB to use its data. However, it is only allowed to Manipulate STATE, WAIT-REASON and WAIT-DATA.

 ### CREATE_TASK
 - Takes absolute Entry Point and Parent PID as Arguments
 - Followed by that comes Amount of Process Arguments
 - Place any Process-Arguments, then call.
 - Parent PID can be PID of Callee or PID of Kernel
 - PID gets automatically asigned by looking for smallest available PID

 ### YIELD
  - Is a callable Function without any Arguments
  - If current Process is STATE_RUNNING, its set to STATE_READY
  - Otherwise it stays untouched
  - Stores Stack Pointer on PCB
  - Looks for next Ready Process
  - Loads Stackpointer from next Process
  - If old Process Terminated:
    - Switch to kernel Mode
    - Remove old PCB out of linked List
    - Free old stack and PCB
  - Return to new Process
  - For now there is no rescue from a deadlock


## Stack
1. Scheduler-Stack starts at M(2048). Process-Specific Stacks are to be allocated on Heap
2. Stack Pointer is *always* at IN2
3. Stack Pointer always points to next free cell
4. Stack grows upwards (Pointer gets bigger)

## STACK_DUMP
 !! Currently not working due to switch to Multiple Stacks with Multi-Tasking !!
 - Not a Method, rather a last Resort Label
 - Loads Stack Pointer, Prints everything starting at stack top
 - Goes until 2048 for now, on multithread system for later not sure

## CALL
### Stack Build:
- M(IN2-1): Absolute Return Adress of Callee
- M(IN2-2): Amount of Arguments for this Method on Stack 
- M(IN2-3) to M(IN2-(2+n)): Arguments
- M(IN2-(3+n)) to M(IN2-(13+n)): Copy of M(0) to M(9) of Callee
- M(IN2-(14+n)): IN1 Register of Callee

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
- Heap Top Pointer is at M(4095) and points to beginn of last frame, not to real end (points to 4095 if heap is emtpy)
- Every Heap frame with n data cells consists of:
    - M(H): Length of Heap Frame (n+3)
    - M(H+1): Is Frame used? (0: not used, else: PID of Process allocating this Frame (PID is always != 0))
    - M(H+2) to M(H+2+n)
    - M(H+3+n): Length of Heap Frame (n+3)
- Heap Block size is currently limited to 1GB (=1.073.741.824) (to protect pyhton emulator and simulate a 32-Bit system)
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

### SIZEOF(n)
- Argument 1: Pointer to Heap Block Data (Heap Start +2)
- Checks if Pointer points to Heap Block via Boundry check, Block_used label and size comparision
- Returns usable Size
- Jumps to SEGMENTATION_FAULT on Error

# Strings
- For easy Print, every Ascii Character is stored in M(<char value> + 100)
    - E.g.: a = M(197) because ord(a) = 97 -> 97 + 100 = 197
- Every String ends with a Zero Terminator (=0)
- Following Functions are mostly not important for the os, rather written for a shell that might be implemented in the future.
## ATOI
    - 1. Argument: Pointer to String Buffer
    - 2. Argument (Optional): Offset to first Digit (Zero if not provided)
    - First char after aplying offset must be a digit or '-' value
    - If first digit is no digit, zero will be returned
    - Stops Parsing once a non-digit character has been found
    - Parsed Value will be at M(1030)
    - If Offset was provided, Offset from buffer-start to first character AFTER last digit is will be returned to M(1031)
## GET_LINE_WIDTH
    - Argument Count for Call Method: 4
    - 1. Argument: Pointer to String
    - 2. Argument: Pointer to eof String
    - 3. Argument: Pointer to any Character of specific line
    - 4. Argument: Set to Zero
    - Only whole Strings accecepted, no Gap-Strings (split string in two if needed)
    - If target character (third argument) points to newline, it is seen as the end of the current line
    - First Return Value is Amount of visable Characters in Line. -1 if Error
    - Second Return Value is the Location of the target Character in this Line. 
    - Third Return Value is 1 if Line is first Line of String, otherwise 0
    - Fourth Return Value is 1 if Line is last Line of String, otherwise 0
    - If first Value is -1, all the other Values cannot be trusted

## GET_CURSOR_POSITION
    - No input Arguments required, however three Return Arguments, so set amount to 3
    - First Return Value is y-coordinate, starting at 1 at the top of the screen
    - Second Return Value is x-coordinate, starting at 1 at the left side of the screen
    - Third Return Value is a Pointer to an Input-Buffer filled with Keyboard Input values which were
      read during parsing, zero terminated. If there werent any additional Inputs, Pointer will be NULL (0)
    - Warning! If Third Return Value is a real Pointer, you need to free it once dealed with the inputs!

## GET_SCREEN_SIZE
    - No input Arguments required, however three Return Arguments, so set amount to 3
    - First Return Value is the height of the screen
    - Second Return Value is the width of the screen
    - Third Return Value is a Pointer to an Input-Buffer filled with Keyboard Input values which were
      read during parsing. If there werent any additional Inputs, Pointer will be NULL (0)
    - Warning! If Third Return Value is a real Pointer (!=0), you need to free it once dealed with the inputs!

## MOVE_STRING_BUFFER_GAP:
    - Arg Count: 5
    - Arg 1: Pointer to String Buffer Start
    - Arg 2: Pointer to Gap Start (first empty field)
    - Arg 3: Pointer to Gap End (last empty field)
    - Arg 4: Pointer to String Buffer End (last usable field)
    - Arg 5: Amount of fields to move (positive->right, negativ->left)
    Return Arguments:
    - Arg 1: Is Move in Boundrys of Buffer? If Zero(=No), String will not be touched, return Args are correct
    - Arg 2: New Gap Start Pointer
    - Arg 3: New Gap End Pointer

## GET_LINE_COUNT
    - Arg Count: 3 (optional: 5)
    - Arg 1: Pointer to String Start
    - Arg 2: Pointer to String End
    - Arg 3: Target-Pointer to char in String (Optional, otherwise set to zero)
    - Arg 4 (opt): Gap-Start Pointer, points to first empty cell
    - Arg 5 (opt): Gap-End Pointer, points to last empty cell
    String must be complete String if Argcount is 3 (No Gap in String allowed)
    - Return Arguments
    - Arg 1: Amount of Total Lines in given String (starting at zero if string is empty, otherwise >= 1)
    - Arg 2: Number of Line Target-Char is in (starting at Line 1), 0 if Target-Pointer is zero

## GET_STRING_SIZE
    - Arg Count: 1 (Optional 2)
    - Arg 1: Pointer to String 
    - Optional: Arg 2: Max Size of String
    - Return Arg 1: Size of String without Zero-Terminator or Max Size
    - Optional: Flag if Zero-Terminator within Max-Bounds (1 if so, 0 otherwise)


