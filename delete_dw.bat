@echo off
subst X: "D:\git\mulesoft\projects\api-cert-level-2\src\test\resources"
for /d %%i in (X:\embedded-dw_*) do (
    echo Deleting: %%i
    rmdir /s /q "%%i"
)
subst X: /d
echo Done.
