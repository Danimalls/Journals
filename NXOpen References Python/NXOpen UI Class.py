from NXOpen import *
import NXOpen
import NXOpen.Preferences
import NXOpen

'''All info found here: <https://docs.sw.siemens.com/documentation/external/PL20221117716122093/en-US/nx_api/nx/2306/nx_api/en-US/nxopen_python_ref/a04207.html>'''

theSession:Session = NXOpen.Session.GetSession()
partCollection:PartCollection = theSession.Parts
workPart:BasePart = partCollection.Work
theUI:UI = NXOpen.UI.GetUI()
nx_exceptions = NXOpen.NXException
lw:ListingWindow = theSession.ListingWindow

def main():
    lw.Open()

    '''Unsure how to use popupmenu handler'''
    # custom_popup_menu = theUI.CreateCustomPopupMenuHandler()

    '''CreateDialog requires BlockStyler license'''
    # dialog = theUI.CreateDialog("Dialog")
    
    '''Display notification in notification tab'''
    # notification = theUI.DisplayNotification("Test Notification Display", "description", "secondary text", "U:\\dhalonen\\PICS\\A&S LOGO.png")
    
    '''Unsure how to use MenuBarManager'''
    # menu_bar_mngr:MenuBar.MenuBarManager = theUI.MenuBarManager
    # menu_bar_mngr_properties = menu_bar_mngr.NewApplicationProperties()

    '''Can record movie, but cant watch due to codec fourcc MSVC'''
    # movie_manager = theUI.MovieManager
    # movie_settings = movie_manager.CreateMovieSettingsBuilder()
    # lw.WriteFullline(f"{movie_settings.CodecFourcc}")
    # movie_manager.Start("U:\\dhalonen\\PICS\\movie_test.avi", True)
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.CaptureFrame()
    # movie_manager.End()

    '''Shows a message box with one or multiple messages'''
    # nx_msg_box:NXMessageBox = theUI.NXMessageBox
    # nx_msg_box.Show("Message Box", NXMessageBox.DialogType.Information, ["Msg 1", "Msg 2", "Msg3"])

    '''Sets object preference translucency'''
    # obj_prefs = theUI.ObjectPreferences
    # obj_prefs.SetSessionTranslucency(NXOpen.Preferences.ObjectPreferences.Translucency.Enabled)

    '''Product Demo, not sure exactly what this is'''
    # demo = theUI.ProductDemo
    # lw.WriteFullline(f"{demo.__doc__}")
    # link = demo.GetDemoLink(True)
    # msg = demo.Message
    # lw.WriteFullline(f"{msg.__doc__}")
    # lw.WriteFullline(f"{demo.Show}")

    '''Not sure what this is'''
    # styler = theUI.Styler
    # styler.CreateStylerDialog("Test Dialog")

    '''Sets user interface preferences'''
    # user_interface_prefs = theUI.UserInterfacePreferences

    '''No clue how View UI manager works.'''
    # view_ui_mngr = theUI.ViewUIManager
    # view_ui_mngr.CreatePreview(NXOpen.View.Fit, True)

    # attr_and_methods = dir(NXOpen.View)
    # lw.WriteFullline(f"{attr_and_methods}")

    lw.Close()

if __name__ == "__main__":
    main()