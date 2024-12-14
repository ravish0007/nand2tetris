
// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
(RESTART)

@8192
D=A

@R1
M=D

@n
M=0

// compare key
@KBD
D=M

@WHITE
D;JEQ

(BLACK)

@n
D=M

@R1
D=D-M

@RESTART
D;JEQ

@SCREEN
D=A

@n
A=D+M
M=-1

D=A
@2
M=D

@n
M=M+1

@BLACK
0;JMP

(WHITE)
@n
D=M
@R1
D=D-M
@RESTART
D;JEQ

@SCREEN
D=A

@n
A=D+M
M=0

@n
M=M+1

@WHITE
0;JMP


