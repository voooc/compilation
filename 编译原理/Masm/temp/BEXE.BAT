@echo off

set include=G:\E\WINASM\wasm\include
set lib=G:\E\WINASM\wasm\lib
set path=G:\E\WINASM\wasm\bin;

if exist %1.exe del %1.exe

ml /c /coff /Zi %1.asm 
if not exist %1.obj goto mlerr

if exist %1.res goto LinkWithRc
if not exist %1.rc goto LinkWithoutRc
rc %1.rc
if not exist %1.res goto rcerr
:LinkWithRc
Link /SUBSYSTEM:WINDOWS /DEBUG /DEBUGTYPE:CV %1.obj %1.res 
echo     link with the resource file.
goto pos2

:LinkWithoutRc
Link /SUBSYSTEM:WINDOWS /DEBUG /DEBUGTYPE:CV %1.obj 
echo     without the resource file.

:pos2
del %1.obj %1.ilk %1.res
goto over

:rcerr
echo Resource file error!
goto over

:mlerr
echo assemble error!

:over
echo on