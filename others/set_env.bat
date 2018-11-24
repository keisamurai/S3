@echo off
REM ///////////////////////////////////////////////////
REM // name        : set_env.bat
REM // description : Set Username and Password for Watson
REM //             : Discovery Service on Env Variables
REM ///////////////////////////////////////////////////

set ACCOUNT=a0766d60-1d62-4cbc-abb9-1542a790bdca
set PASS=Sfi1P1AhZFGk
set CHROMEPATH="E:\pj\AI\2018年度\3.開発\s3pj\lib\chromedriver.exe"
set DLDATAPATH="E:\pj\AI\2018年度\3.開発\s3pj\"

echo set_env start...
setx DISCOVERY_USER_NAME %ACCOUNT% -m
setx DISCOVERY_PASS %PASS% -m
setx CHROME_DRIVER %CHROMEPATH% -m
setx DLDATAPATH %DLDATAPATH% -m
echo set_env end...
pause
