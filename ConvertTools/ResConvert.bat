@echo off

set XLS_NAME=%1
set SHEET_NAME=%2



echo.
echo =========Compilation of %XLS_NAME%.xls=========


::---------------------------------------------------
::��һ������xls����xls_deploy_toolת��bin��proto
::---------------------------------------------------
set STEP1_XLS2PROTO_PATH=xls2proto

@echo on
cd %STEP1_XLS2PROTO_PATH%

@echo off
echo TRY TO DELETE TEMP FILES:
del *_pb2.py
del *_pb2.pyc
del *.proto
del *.bin
del *.log
del *.txt

@echo on
python ..\xls2protobuf_v3.py %SHEET_NAME% ..\xls\%XLS_NAME%.xls



::---------------------------------------------------
::�ڶ�������proto�����cs
::---------------------------------------------------
cd ..

set STEP2_PROTO2CS_PATH=.\proto2cs
set PROTO_DESC=proto.protodesc
set SRC_OUT=.\

cd %STEP2_PROTO2CS_PATH%

@echo off
echo TRY TO DELETE TEMP FILES:
del *.cs
del *.protodesc
del *.txt


@echo on
dir ..\%STEP1_XLS2PROTO_PATH%\*.proto /b  > protolist.txt

@echo on
for /f "delims=." %%i in (protolist.txt) do protoc --descriptor_set_out=%PROTO_DESC% --proto_path=..\%STEP1_XLS2PROTO_PATH% ..\%STEP1_XLS2PROTO_PATH%\%%i.proto
::for /f "delims=." %%i in (protolist.txt) do ProtoGen\protogen -i:%PROTO_DESC% -o:%%i.cs
for /f "delims=." %%i in (protolist.txt) do protoc --proto_path=..\%STEP1_XLS2PROTO_PATH% ..\%STEP1_XLS2PROTO_PATH%\%%i.proto --csharp_out=%SRC_OUT%

cd ..

::---------------------------------------------------
::����������bin��cs����Assets��
::---------------------------------------------------

@echo off
set OUT_PATH=E:\project\uframwork\client\Assets
set DATA_DEST=StreamingAssets\DataConfig
set CS_DEST=Scripts\ResData


@echo on
copy %STEP1_XLS2PROTO_PATH%\*.bin %OUT_PATH%\%DATA_DEST%
copy %STEP2_PROTO2CS_PATH%\*.cs %OUT_PATH%\%CS_DEST%

::---------------------------------------------------
::���Ĳ�������м��ļ�
::---------------------------------------------------
REM @echo off
REM echo TRY TO DELETE TEMP FILES:
REM cd %STEP1_XLS2PROTO_PATH%
REM del *_pb2.py
REM del *_pb2.pyc
REM del *.proto
REM del *.bin
REM del *.log
REM del *.txt
REM cd ..
REM cd %STEP2_PROTO2CS_PATH%
REM del *.cs
REM del *.protodesc
REM del *.txt
REM cd ..

::---------------------------------------------------
::���岽������
::---------------------------------------------------
REM cd ..

@echo on
