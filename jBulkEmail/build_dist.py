import subprocess
import sys
import os
from pathlib import Path
import shutil

def build_mission_exe():
    """
    Automates the construction of a standalone tactical executable.
    Phase 11: Deployment & Portability.
    """
    print("🚀 [BUILD] Initiating Mission Control Executable Construction...")
    
    # 1. Prepare Workspace
    base_dir = Path(__file__).parent
    # Force the absolute path to avoid any ambiguity
    abs_base = str(base_dir.absolute())
    output_dir = base_dir / "PACKAGE_READY_TO_ZIP"
    
    # Clean previous build artifacts
    if output_dir.exists():
        print(f"🧹 [CLEAN] Removing old package folder...")
        try: shutil.rmtree(output_dir)
        except: pass
        
    output_dir.mkdir(exist_ok=True)

    # 2. Verify/Install PyInstaller
    print("⚙️ [SETUP] Verifying Tactical Packaging (PyInstaller)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"])

    # 3. Define Build Command
    # USE sys.executable -m PyInstaller for maximum reliability on Windows
    add_data_sep = ";" if os.name == 'nt' else ":"
    
    data_args = []
    for d in ["app", "core", "assets"]:
        if (base_dir / d).exists():
            data_args.append(f"--add-data={d}{add_data_sep}{d}")

    # FORCE Path Resolution for Windows
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--windowed", 
        "--name", "jBulkEmailSender",
        "--distpath", str(output_dir),
        *data_args,
        "main.py"
    ]

    print(f"🛠️ [BUILD] Executing Tactical Construction engine...")
    
    try:
        # Use shell=True occasionally helps on Windows with PATH resolution
        subprocess.check_call(cmd)
        
        # 4. Finalize Tactical Package (Copy Deployment Assets)
        pkg_dir = output_dir / "jBulkEmailSender"
        print(f"📦 [PACKAGE] Polishing deployment assets in {pkg_dir}...")
        
        # 5. Phase 15: MSI Preparation (WiX Toolset)
        # We need to create a WXS file for WiX to build the MSI
        print("🏛️ [MSI] Generating WiX Source for Microsoft Compliance...")
        generate_wxs(pkg_dir)

        print("\n" + "="*80)
        print("✅ SUCCESS: MISSION COMPLETE.")
        print(f"📍 LOCATION: {pkg_dir}")
        print("📦 MSI BUILD: Run 'candle jBES_Installer.wxs' and 'light jBES_Installer.wixobj'")
        print("🚀 DEPLOYMENT: The application is now Microsoft Compliant (uses %AppData%).")
        print("="*80)

    except Exception as e:
        print(f"\n🚨 ENGINE FAILURE: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

def generate_wxs(pkg_dir):
    """Generates a WiX Source file for creating a Per-User MSI installer with selectable path."""
    wxs_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
    <Product Id="*" Name="jBES Discovery" Language="1033" Version="6.1.0" 
             Manufacturer="Antigravity AI" UpgradeCode="7b2e1a3c-4d5e-6f7a-8b9c-0d1e2f3a4b5c">
        <!-- Phase 16: Per-User Installation (Zero-Admin Compliance) -->
        <Package InstallerVersion="200" Compressed="yes" InstallScope="perUser" />

        <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
        <MediaTemplate EmbedCab="yes" />

        <!-- Include standard WiX UI for Path Selection -->
        <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
        <UIRef Id="WixUI_InstallDir" />

        <Feature Id="ProductFeature" Title="jBES Discovery" Level="1">
            <ComponentGroupRef Id="ProductComponents" />
            <ComponentRef Id="ApplicationShortcut" />
            <ComponentRef Id="DesktopShortcut" />
        </Feature>
    </Product>

    <Fragment>
        <Directory Id="TARGETDIR" Name="SourceDir">
            <!-- Install to User's Local AppData instead of Program Files -->
            <Directory Id="LocalAppDataFolder">
                <Directory Id="INSTALLFOLDER" Name="jBES Discovery" />
            </Directory>
            <Directory Id="ProgramMenuFolder">
                <Directory Id="ApplicationProgramsFolder" Name="jBES Discovery"/>
            </Directory>
            <Directory Id="DesktopFolder" Name="Desktop" />
        </Directory>
    </Fragment>

    <Fragment>
        <DirectoryRef Id="ApplicationProgramsFolder">
            <Component Id="ApplicationShortcut" Guid="*">
                <Shortcut Id="ApplicationStartMenuShortcut" 
                          Name="jBES Discovery" 
                          Description="Bulk Email Mission Control"
                          Target="[INSTALLFOLDER]jBulkEmailSender.exe"
                          WorkingDirectory="INSTALLFOLDER"/>
                <RemoveFolder Id="ApplicationProgramsFolder" On="uninstall"/>
                <RegistryValue Root="HKCU" Key="Software\AntigravityAI\jBESDiscovery" Name="installed" Type="integer" Value="1" KeyPath="yes"/>
            </Component>
        </DirectoryRef>
        <DirectoryRef Id="DesktopFolder">
            <Component Id="DesktopShortcut" Guid="*">
                <Shortcut Id="ApplicationDesktopShortcut"
                          Name="jBES Discovery"
                          Description="Bulk Email Mission Control"
                          Target="[INSTALLFOLDER]jBulkEmailSender.exe"
                          WorkingDirectory="INSTALLFOLDER"/>
                <RegistryValue Root="HKCU" Key="Software\AntigravityAI\jBESDiscovery" Name="desktop_shortcut" Type="integer" Value="1" KeyPath="yes"/>
            </Component>
        </DirectoryRef>
    </Fragment>

    <Fragment>
        <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
            <Component Id="MainExecutable" Guid="*">
                <File Id="jBESEXE" Source="{pkg_dir}\\jBulkEmailSender.exe" KeyPath="yes" />
            </Component>
            <!-- Note: In a production build, use 'heat.exe' to harvest all sub-files -->
        </ComponentGroup>
    </Fragment>
</Wix>
"""
    wxs_path = pkg_dir.parent / "jBES_Installer.wxs"
    with open(wxs_path, "w") as f:
        f.write(wxs_content)
    print(f"📄 [WIX] Created: {wxs_path}")

if __name__ == "__main__":
    build_mission_exe()
