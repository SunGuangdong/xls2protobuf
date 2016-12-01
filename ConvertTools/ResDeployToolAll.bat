@echo off

::-------------------------------------
:: ת����������
::-------------------------------------

echo.
echo =========Compilation  All xls=========


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

for /f "delims=" %%i in (..\ConvertList.txt) do   python ..\xls_deploy_tool.py %%i


::---------------------------------------------------
::�ڶ�������proto������cs
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

set textPath=%cd%\
for /f "delims=." %%i in (protolist.txt) do protoc --descriptor_set_out=%%i.protodesc --proto_path=..\%STEP1_XLS2PROTO_PATH% ..\%STEP1_XLS2PROTO_PATH%\%%i.proto
for /f "delims=." %%i in (protolist.txt) do ProtoGen.exe %textPath%%%~ni.protodesc -output_directory=%SRC_OUT%

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
::���Ĳ��������м��ļ�
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
