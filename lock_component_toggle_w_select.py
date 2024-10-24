import NXOpen
import NXOpen.UF
import NXOpen.Assemblies
import os

theSession = NXOpen.Session.GetSession()
workPart = theSession.Parts.Work
theUFSession = NXOpen.UF.UFSession.GetUFSession()
theUI = NXOpen.UI.GetUI()
msgbox = NXOpen.UF.UFSession.GetUFSession()
lw = theSession.ListingWindow

def main():
    lw.Open()

    def select_components(title:str):
        scope = NXOpen.Selection.SelectionScope.AnyInAssembly
        action = NXOpen.SelectionSelectionAction.ClearAndEnableSpecific
        includeFeatures = False
        keepHighlighted = False
        selection = theUI.SelectionManager
        mask = NXOpen.Selection.MaskTriple()
        mask.Type = NXOpen.UF.UFConstants.UF_component_type
        maskArray = [mask]
        components = selection.SelectTaggedObjects("Select Components", title, scope, action, includeFeatures, keepHighlighted, maskArray)
        components_list = components[1]
        return components_list
    
    def askMsg(title, message, button1, button2):
        message_buttons = NXOpen.UF.Ui.MessageButtons()
        message_buttons.Button1 = True
        message_buttons.Button2 = False
        message_buttons.Button3 = True
        message_buttons.Label1 = button1
        message_buttons.Label2 = None
        message_buttons.Label3 = button2
        message_buttons.Response1 = 1
        message_buttons.Response2 = 0
        message_buttons.Response3 = 2

        resp = theUFSession.Ui.MessageDialog(title, NXOpen.UF.Ui.MessageDialogType.MESSAGE_INFORMATION, message, 1, True, message_buttons)

        if resp == 1:
            return True
        else:
            return False
    
    comps_for_lock = select_components("Select Components")
    lock = askMsg("Component Lock", ["Lock or Unlock Components?"], "Lock", "Unlock")

    if lock:
        for comp in comps_for_lock:
            comp_path = comp.Prototype.FullPath
            os.chmod(comp_path, 0o444)
        msgbox.Ui.DisplayMessage("All selected files change to Read-Only!", 0)
    else:
        for comp in comps_for_lock:
            comp_path = comp.Prototype.FullPath
            os.chmod(comp_path, 0o666)
        msgbox.Ui.DisplayMessage("All selected files change to Writable!", 0)

if __name__ == "__main__":
    main()
