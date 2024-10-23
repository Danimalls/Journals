import NXOpen
import NXOpen.UF
import os

def main():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    msgbox = NXOpen.UF.UFSession.GetUFSession()

    part = workPart.FullPath

    if os.access(part, os.W_OK):
        os.chmod(part, 0o444)
        msgbox.Ui.DisplayMessage("File changed to: Read Only", 0)
    else:
        os.chmod(part, 0o666)
        msgbox.Ui.DisplayMessage("File changed to: Writable", 0)

if __name__ == "__main__":
    main()
