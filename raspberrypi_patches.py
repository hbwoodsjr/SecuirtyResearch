#!/usr/bin/python3
"""
WiSec 2021 tutorial example by Jiska Classen.
Hooks into LMP handler for Remote Feature Results and overwrites features.
"""
# imports for ADB and HCi core
from internalblue.adbcore import ADBCore
from internalblue.hcicore import HCICore
# imports for calling InternalBlue CLI
from internalblue.cli import InternalBlueCLI
from argparse import Namespace
import sys
# imports for our own script/hooks
from time import sleep
from pwnlib.asm import asm
from internalblue.utils.packing import u8, u32, p32
import binascii

internalblue = ADBCore()
try:
    internalblue.interface = internalblue.device_list()[0][1]  # just use the first Android device
except IndexError:
    internalblue = HCICore()
    try:
        internalblue.interface = internalblue.device_list()[0][1]  # ...or the first local HCI interface
    except IndexError:
        internalblue.logger.critical("Adapt the Python script to use an available Broadcom Bluetooth interface.")
        exit(-1)
# setup sockets
if not internalblue.connect():
    internalblue.logger.critical("No connection to target device.")
    exit(-1)
progress_log = internalblue.logger.info("Connected to first target, installing patches...")

LMP_PATCH_FEATURES_RES = 0x205e00  # free RAM to write our own patch
LMP_FUNCT_FEATURES_RES = 0x7d552  # lm_HandleLmpFeaturesResPdu implementation
#LMP_CMD_PTR            = 0x20AB74  # lm_curCmd
LMP_PATCH_ASM = """
    // restore first 4 bytes of lm_HandleLmpFeaturesResPdu
    push {r4, lr}
    strh.w r1, [r4,#0x42] ; Store to Memory
    // use r0-r1 locally
    push  {r1-r2, lr}
    ldr   r2, =0x205dfc   
    ldr   r2, [r2]
    cmp   r1, r2
    beq   0x35fbc
    pop  {r1-r2, lr}
    b    0x%x

""" % (LMP_FUNCT_FEATURES_RES + 4)
# assemble our snippet and install it in RAM
code = asm(LMP_PATCH_ASM, vma=LMP_PATCH_FEATURES_RES)  # branches are relative, we need to put the patches address here
if not internalblue.writeMem(address=LMP_PATCH_FEATURES_RES, data=code, progress_log=None):
    internalblue.logger.critical("Could not write pre-hook for features result to RAM!")
    exit(-1)
# patch the original function in ROM to branch to RAM
code = asm('b 0x%x' % LMP_PATCH_FEATURES_RES, vma=LMP_FUNCT_FEATURES_RES)
if not internalblue.patchRom(LMP_FUNCT_FEATURES_RES, code):
    internalblue.logger.critical("Could not install Patchram entry to verwrite existing function!")
    exit(-1)
# enter CLI so that we can still interact and see the connection request
cli = InternalBlueCLI(Namespace(data_directory=None, verbose=False, trace=None, save=None), internalblue)
sys.exit(cli.cmdloop())