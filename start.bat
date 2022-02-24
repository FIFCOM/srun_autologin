@ECHO OFF
REM  QBFC Project Options Begin
REM  HasVersionInfo: Yes
REM  Companyname: Fifcom Technology Atelier
REM  Productname: Srun Autologin Launcher
REM  Filedescription: Srun Autologin Launcher
REM  Copyrights: Fifcom Technology Atelier
REM  Trademarks: Fifcom Technology Atelier
REM  Originalname: 
REM  Comments: 
REM  Productversion:  1. 0. 0. 0
REM  Fileversion:  1. 0. 0. 0
REM  Internalname: 
REM  Appicon: favicon.ico
REM  AdministratorManifest: No
REM  QBFC Project Options End
@ECHO ON
@echo off
title Srun AutoLogin
mode con: cols=65 lines=25
color 8b
:: srun_firefox.exe
python srun_firefox.py
ping -n 2 localhost > nul