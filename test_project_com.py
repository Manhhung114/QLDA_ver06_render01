"""Kiểm tra riêng COM Automation của Microsoft Project trên Windows."""
import os
import sys
import platform

print("=" * 68)
print("QLDA - KIỂM TRA MICROSOFT PROJECT COM")
print("=" * 68)
print("Python :", sys.executable)
print("Version:", sys.version.replace("\n", " "))
print("OS     :", platform.platform())
print("64-bit :", platform.architecture()[0])

if os.name != "nt":
    print("\n[SKIP] Microsoft Project COM chỉ kiểm tra trên Windows.")
    raise SystemExit(0)

try:
    import pythoncom
    import win32com.client
    import pywintypes
    print("pywin32: OK")
except Exception as exc:
    print("\n[FAIL] Không import được pywin32:", repr(exc))
    print("Chạy: python -m pip install --upgrade pywin32")
    raise SystemExit(2)

pythoncom.CoInitialize()
try:
    try:
        app = win32com.client.GetActiveObject("MSProject.Application")
        print("[OK] GetActiveObject: kết nối được Microsoft Project đang mở")
        try:
            print("     Version:", app.Version)
        except Exception:
            pass
        try:
            print("     ActiveProject:", app.ActiveProject.FullName)
        except Exception:
            print("     ActiveProject: không có/không đọc được")
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as exc:
        print("[INFO] GetActiveObject không dùng được:", repr(exc))

    try:
        app = win32com.client.DispatchEx("MSProject.Application")
        print("[OK] DispatchEx: tạo được Microsoft Project COM instance")
        try:
            print("     Version:", app.Version)
        except Exception:
            pass
        try:
            app.Quit()
        except Exception:
            pass
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as exc:
        print("[INFO] DispatchEx không dùng được:", repr(exc))

    try:
        app = win32com.client.Dispatch("MSProject.Application")
        print("[OK] Dispatch: kết nối/tạo được Microsoft Project COM instance")
        try:
            print("     Version:", app.Version)
        except Exception:
            pass
        raise SystemExit(0)
    except SystemExit:
        raise
    except Exception as exc:
        print("[FAIL] Dispatch cũng lỗi:", repr(exc))
        hresult = getattr(exc, "hresult", None)
        if isinstance(hresult, int):
            print(f"HRESULT: 0x{(hresult & 0xffffffff):08X} ({hresult})")
        print("\nNếu HRESULT = 0x80040154: COM class chưa đăng ký -> Repair Microsoft Project/Office.")
        print("Nếu Project đang mở nhưng GetActiveObject vẫn lỗi: đóng hết Project, mở lại và chạy script lần nữa.")
        raise SystemExit(3)
finally:
    pythoncom.CoUninitialize()
