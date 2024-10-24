from NXOpen import *
import NXOpen
from NXOpen.UF import *
import NXOpen.UF

'''All info found here: <https://docs.sw.siemens.com/documentation/external/PL20221117716122093/en-US/nx_api/nx/2306/nx_api/en-US/nxopen_python_ref/a68395.html#a982501125f7092d774ce9ce792692c7c>'''

theSession:Session = NXOpen.Session.GetSession()
partCollection:PartCollection = theSession.Parts
workPart:BasePart = partCollection.Work
theUI:UI = NXOpen.UI.GetUI()
theUFUi:NXOpen.UF.Ui = NXOpen.UF.Ui()
taggedObjManager:TaggedObjectManager = NXOpen.TaggedObjectManager
nx_exceptions:NXException = NXOpen.NXException
info_window:ListingWindow = theSession.ListingWindow

def main():
    info_window.Open()

    def lw(*args):
        for arg in args:
            info_window.WriteFullline(f"{arg}")

    def lwDict(**kwargs):
        for k, v in kwargs.items():
            info_window.WriteFullline(f"{k}: {v}")

    def lockUG():
        theUFUi.LockUgAccess(1)

    def unlockUG():
        theUFUi.UnlockUgAccess(1)

    '''Ask for a filename and register name, units, and type of response (Does not seem to actually make the file)'''
    # create_part_filename:tuple = theUFUi.AskCreatePartFilename("U:\\dhalonen\\test\\test_1234.prt", 0) # Tuple consists of filename, unit type, response
    # filename:str = create_part_filename[0]
    # units:int = create_part_filename[1] # 0 = "None", 1 = "Metric", 2 = "English"
    # response:int = create_part_filename[2] # 2 = "OK", 3 = "Cancel" or "Exit"

    # attr_and_methods = dir(create_part_filename)
    # lw(attr_and_methods, filename, units, response)

    '''Unsure of ask cursor view use, always returns 0 (any view). A return of 1 would mean work view but not sure how to acquire'''
    # cusrsor_view = theUFUi.AskCursorView()

    # attr_and_methods = dir(cusrsor_view)
    # lw(cusrsor_view)

    '''Reports all dialog directory paths. dialog_id_enum is a list of all options under <NXOpen.UF.Ui.DialogDirId>'''
    # dialog_id_enum = [attr for attr in dir(NXOpen.UF.Ui.DialogDirId) if not attr.startswith('__')]
    # for item in dialog_id_enum:
    #     try:
    #         dialog_id = getattr(NXOpen.UF.Ui.DialogDirId, item)
    #         try:
    #             dialog_dir = theUFUi.AskDialogDirectory(dialog_id)
    #         except TypeError as te:
    #             pass
    #         if dialog_dir:
    #             lwDict(dialog_type=item, dialog_directory=dialog_dir)
    #     except nx_exceptions as ex:
    #         pass

    '''Reports all dialog filters. dialog_filter_id_enum is a list of all options under <NXOpen.UF.Ui.DialogFilterId>'''
    # dialog_filter_id_enum = [attr for attr in dir(NXOpen.UF.Ui.DialogFilterId) if not attr.startswith('__')]
    # for item in dialog_filter_id_enum:
    #     try:
    #         dialog_filter_id = getattr(NXOpen.UF.Ui.DialogFilterId, item)
    #         try:
    #             dialog_filter = theUFUi.AskDialogFilter(dialog_filter_id)
    #         except TypeError as te:
    #             pass
    #         if dialog_filter:
    #             lwDict(filter_type=item, extension=dialog_filter)
    #     except nx_exceptions as ex:
    #         pass

    '''Reports number of selected objects as well as a list of tags of all selected objects'''
    # sel_obj_list:tuple = theUFUi.AskGlobalSelObjectList() # Tuple consists of number of objs selected, and list of obj tags selected
    # num_of_objects:int = sel_obj_list[0] # Number of selected objs
    # obj_tag_list:list[Tag] = sel_obj_list[1] # list of selected obj tags
    # for tag in obj_tag_list:
    #     obj = taggedObjManager.GetTaggedObject(tag) # Use tagged object manager to get object from tag. Then use obj methods/attributes.
    #     lw(obj.Name)

    '''Displays info units for all info displayed from 'info' commands'''
    # all_units = ['UF_UI_POUNDS_INCHES', 'UF_UI_POUNDS_FEET', 'UF_UI_GRAMS_MILLIMETERS', 'UF_UI_GRAMS_CENTIMETERS', 'UF_UI_KILOS_METERS', 'UF_UI_KILOS_MILLIMETERS', 'UF_UI_DEFAULT_UNITS']
    # info_units = all_units[theUFUi.AskInfoUnits()]
    # lw(info_units)

    '''Gets information window precision type and decimal places'''
    # decimal_info:tuple = theUFUi.AskIwDecimalPlaces() # Tuple consists of int, and int
    # precision_types = ['UF_UI_SYSTEM_DECIMAL_PLACES', 'UF_UI_USER_DECIMAL_PLACES']
    # precision_type = precision_types[decimal_info[0]]
    # decimal_places = decimal_info[1]
    # lw(precision_type, decimal_places)

    '''Finds last view type selected eg Trimetric, Top, etc.'''
    # last_picked_view = theUFUi.AskLastPickedView()
    # lw(last_picked_view)

    '''Asks or sets UG lock status. When asking, returns integer. 2 = Locked, 3 = Unlocked. Constants found in uf_ui_types.h'''
    # lock_status = theUFUi.AskLockStatus()
    # lw(lock_status)
    # theUFUi.LockUgAccess(1)
    # lock_status = theUFUi.AskLockStatus()
    # lw(lock_status)
    # theUFUi.UnlockUgAccess(1)
    # lock_status = theUFUi.AskLockStatus()
    # lw(lock_status)

    '''Returns True or False if NX graphics window special minimal mode is on or off'''
    # minimal_gfx_window = theUFUi.AskMinimalGraphicsWindow()
    # lw(minimal_gfx_window)

    '''Opens a file dialog for user to select a file to open. Returns a tuple of str, and int. str is full file path of file to open, int indicates whether ok or cancel was selected. 2 = OK, 3 = Cancel.'''
    # filename_and_resp:tuple = theUFUi.AskOpenPartFilename("", True)
    # file_to_open = filename_and_resp[0]
    # resp = filename_and_resp[1]
    # if resp == 2:
    #     partCollection.OpenBaseDisplay(file_to_open)
    # else:
    #     lw('Cancel was selected')

    '''Ribbon information, not sure where this would be useful'''
    # ribbon_vis = theUFUi.AskRibbonVis(arg) # Returns int. 1 = Show, 0 = Hide
    # lw(ribbon_vis)

    '''Cannot figure out what <select_, pointer wrapper, UF_UI_Selection_p_t, etc.> are. Need to pass this to function'''
    # sel_cursor_pos_tuple:tuple = theUFUi.AskSelCursorPos()
    # lw(sel_cursor_pos_tuple)

    # attr_and_methods = [attr for attr in dir(UFConstants) if "select" in attr.lower() and "uf_ui" in attr.lower()]
    # for at in attr_and_methods:
    #     lw(at)

    '''AskSelDescriptor is same issue as above ^^'''

    '''AskSelListCount is same issue as above ^^'''

    '''AskSelObjectList is same issue as above ^^'''

    '''AskSelRectanglePos is same issue as above ^^'''

    '''Opens dialog box and allows user to enter a string. Returns a tuple of information. MUST LOCK UG ACCESS BEFORE RUNNING THIS DIALOG'''
    # theUFUi.LockUgAccess(1)
    # str_input_result = theUFUi.AskStringInput('Enter Name of new prt file', 'Enter Name of new prt file')
    # str_input = str_input_result[0] # String that was entered
    # str_input_len = str_input_result[1] # Int length of string that was entered
    # return_options = ['', 'Back', 'Cancel', 'OK(Accept Default)', '', 'Data entered', '', '', 'Disallowed state, unable to bring up dialog']
    # str_input_return = str_input_result[2] # Int type of response.
    # if str_input_return == 8:
    #     lw(return_options[str_input_return], 'Must lock ug access with "NXOpen.UF.Ui().LockUgAccess(1)" before running this dialog')
    # else:
    #     lw(str_input)
    # theUFUi.UnlockUgAccess(1)

    '''Opens a file dialog that is customizable with filters, starting locations, prompts, and titles'''
    # file_box:tuple = theUFUi.CreateFilebox('standart prompt text', 'title text', 'T:\\Design\\*.prt', 'default name')
    # filter_dir_and_type = file_box[0] # str, also third argument in CreateFileBox if present
    # file_selected = file_box[1] # str, Full path of file that was selected
    # resp_type = file_box[2] #int, 2 = OK, 3 = Cancel
    # lw(file_box)

    '''Opens a custom menu dialog allowing the user to select one of multiple options. Maximum of 14 menu items, menu item index starts at 5 which is why we subtract 5 one acquiring the menu item'''
    # menu_items = ['item 1', 'item 2', 'item 3']
    # theUFUi.LockUgAccess(1)
    # disp_menu_response = theUFUi.DisplayMenu('Title', 1, menu_items, len(menu_items)) # Returns int
    # theUFUi.UnlockUgAccess(1)
    # if disp_menu_response == 1 or disp_menu_response == 2:
    #     pass
    # elif disp_menu_response == 19:
    #     lw('Disallowed state, unable to bring up dialog. Must lock ug access with "NXOpen.UF.Ui().LockUgAccess(1)" before running this dialog')
    # else:
    #     disp_menu_response -= 5
    #     lw(menu_items[disp_menu_response])

    '''Displays a message to the user'''
    # theUFUi.DisplayMessage('Message to display', 1) # No return. Change int to 0 to swap from message box to status line

    '''Displays dialog with multiple checkboxes the user can select'''
    # menu_items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']
    # theUFUi.LockUgAccess(1)
    # disp_multi_sel_menu:tuple = theUFUi.DisplayMultiSelectMenu('Menu Title', 0, menu_items, len(menu_items))
    # selected_options = []
    # resp = disp_multi_sel_menu[1] # Int, 1 = Back, 2 = Cancel, 3 = OK, 8 = Disallowed state
    # if resp == 3:
    #     for i, value in enumerate(disp_multi_sel_menu[0]): # list of binary 'yes' 'no' results from user selection dialog
    #         if value == 1:
    #             selected_options.append(menu_items[i])
    # theUFUi.UnlockUgAccess(1)
    # lw(selected_options)

    '''Displays a nonmodal msg to user that can be positioned in different parts of the screen'''
    # theUFUi.DisplayNonmodalMsg('Title string', 'Message string', 0) # No return, Pos = center of screen
    # theUFUi.DisplayNonmodalMsg('Title string', 'Message string', 1) # No return, Pos = top left of screen
    # theUFUi.DisplayNonmodalMsg('Title string', 'Message string', 2) # No return, Pos = bottom right of screen
    # theUFUi.DisplayNonmodalMsg('Title string', 'Message string', 3) # No return, Pos = top left of screen again?

    '''Opens a webpage in the NX web broswer tab'''
    # theUFUi.DisplayUrl(r'https://docs.sw.siemens.com/documentation/external/PL20221117716122093/en-US/nx_api/nx/2306/nx_api/en-US/ugopen_doc/uf_ui/global.html#UF_UI_display_url') # Returns 0

    '''Does the same as above but focuses/activates the web browser tab'''
    # theUFUi.DisplayUrlAndActivate(r'https://docs.sw.siemens.com/documentation/external/PL20221117716122093/en-US/nx_api/nx/2306/nx_api/en-US/ugopen_doc/uf_ui/global.html#UF_UI_display_url') # Returns 0

    '''Unsure what user tool is'''
    # test = theUFUi.DisplayUsertool(1, True)
    # lw(test)

    '''No errors, but unsure what quick access options are'''
    # theUFUi.DisableQuickAccess()
    # theUFUi.EnableQuickAccess()

    '''Not sure what these da windows are referencing'''
    # da1coords = theUFUi.GetDa1Coords()
    # lw(da1coords)
    # da2coords = theUFUi.GetDa2Coords()
    # lw(da2coords)

    '''Not sure what parent is/does'''
    # default_parent = theUFUi.GetDefaultParent()
    # lw(default_parent)

    '''Shows dialog menu to input and retrieve floats from user'''
    # menu_items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']
    # float_list = [1.0, 2.0, 3.0, 4.0, 5.0]
    # theUFUi.LockUgAccess(1)
    # input_doubles = theUFUi.GetInputDoubles('Title menu', menu_items, len(menu_items), float_list, 0)
    # theUFUi.UnlockUgAccess(1)
    # lw(input_doubles)

    '''Shows dialog menu to input and retrieve integers from user'''
    # menu_items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']
    # int_list = [1, 2, 3, 4, 5]
    # theUFUi.LockUgAccess(1)
    # input_ints = theUFUi.GetInputIntegers('Title menu', menu_items, len(menu_items), int_list, 0)
    # theUFUi.UnlockUgAccess(1)
    # lw(input_ints)

    '''Shows dialog menu to input and retrieve floats and integers from user'''
    # menu_items = ['item 1', 'item 2', 'item 3', 'item 4', 'item 5']
    # float_list = [1.0, 2.0, 3.0, 4.0, 5.0]
    # int_list = [1, 2, 3, 4, 5]
    # ip6 = [0, 1, 0, 1, 0]
    # theUFUi.LockUgAccess(1)
    # input_nums = theUFUi.GetInputNumbers('Title menu', menu_items, len(menu_items), int_list, float_list, ip6)
    # theUFUi.UnlockUgAccess(1)
    # lw(input_nums)

    '''No errors, but unsure how to use attachment and InitAttachments'''
    # attachment = NXOpen.UF.Ui.Attachment()
    # attachment.AttachTypeTop = NXOpen.UF.Ui.ATTACH_DIALOG
    # attachment.Center = 1
    # attachment.ItemIdTop = "Test"
    # theUFUi.LockUgAccess(1)
    # test = theUFUi.InitAttachments(attachment)
    # theUFUi.UnlockUgAccess(1)

    '''Returns if the listing window is visually open or not'''
    # is_lw_open = theUFUi.IsListingWindowOpen()
    # lw(is_lw_open)

    '''Displays a message box to user with one or more messages and multiple clickable buttons. Can be one of 4 types of dialog box'''
    # msgs = ['msg 1', 'msg 2', 'msg 3']
    # msg_buttons = NXOpen.UF.Ui.MessageButtons()
    # msg_buttons.Button1 = True # Determines if button is active
    # msg_buttons.Button2 = True
    # msg_buttons.Button3 = True
    # msg_buttons.Label1 = "Button 1" # Sets button's text
    # msg_buttons.Label2 = "Button 2"
    # msg_buttons.Label3 = "Button 3"
    # msg_buttons.Response1 = 1 # Value to return if specific button is clicked
    # msg_buttons.Response2 = 2
    # msg_buttons.Response3 = 3
    # msg_type = NXOpen.UF.Ui.MessageDialogType.MESSAGE_INFORMATION
    # # msg_type = NXOpen.UF.Ui.MessageDialogType.MESSAGE_ERROR
    # # msg_type = NXOpen.UF.Ui.MessageDialogType.MESSAGE_WARNING
    # # msg_type = NXOpen.UF.Ui.MessageDialogType.MESSAGE_QUESTION
    # msg_dialog = theUFUi.MessageDialog('Title', msg_type, msgs, len(msgs), False, msg_buttons) # Returns variable stored in button's response
    # lw(msg_dialog)

    '''Does not seem to work, not sure why you would use this when there is already a ListingWindow.Open() function anyways'''
    # theUFUi.OpenListingWindow()

    '''Allows user to select a Csys. 2nd argument is default csys type to load with'''
    # theUFUi.LockUgAccess(1)
    # selected_csys:tuple = theUFUi.PickCsys('Title', 3)
    # theUFUi.UnlockUgAccess(1)
    # type_of_csys_selection:int = selected_csys[0] # Types defined below
    # csys_matrix = selected_csys[1] # List of floats, representing a Matrix3x3
    # csys_location = selected_csys[2] # List of floats, representing a Point3d
    # response:int = selected_csys[3] # Response types defined below
    # lw(type_of_csys_selection, csys_matrix, csys_location, response)

    # Csys types:
    # 0 = Origin, X-pt, Y-pt
    # 1 = X-axis, Y-axis
    # 2 = X-pt, Z-axis
    # 3 = CSYS Of Arc/Conic
    # 4 = WCS
    # 5 = Offset CSYS
    # 6 = Absolute CSYS
    # 7 = Current View
    # 8 = Drafting Object
    # 9 = X-axis, Y-axis, Origin
    # 10 = Point, Perpendicular Curve
    # 11 = WCS
    # 12 = Plane and Vector
    # 13 = Three Planes
    # 14 = Origin, X-pt, Y-pt
    # 15 = Dynamic

    # Response types:
    # 1 = Back
    # 2 = Cancel
    # 3 = OK
    # 7 = No Active Part
    # 8 = Disallowed state, unable to bring up dialog

    # attr_and_methods = dir(selection)
    # lw(attr_and_methods)

    '''Allows user to pick a point on screen. Seems useless because you cannot filter point types and it simply just picks 3D space wherever your mouse is'''
    # lockUG()
    # selected_point = theUFUi.PickPoint('cue')
    # unlockUG()
    # lw(selected_point)

    '''Point construction dialog'''
    # lockUG()
    # pt_construct:tuple = theUFUi.PointConstruct("CUE", NXOpen.UF.Ui.PointBaseMethod.POINT_APPLICATION_METHOD)
    # unlockUG()
    # UiPointBaseMethodMemberType = pt_construct[0].value # Type used to create the point (.value gives int) All correspoding int values below
    # associative_SO_pt_tag = pt_construct[1] # Invisible pt tag
    # pt_location = pt_construct[2] # Pt location, represents Point3d
    # response = pt_construct[3] # Int, Cancel = 3, OK = 2
    # lw(UiPointBaseMethodMemberType.value, associative_SO_pt_tag, pt_location, response)

    # UiPointBaseMethodMemberType types
    # 1. UF_UI_POINT_INFERRED
    # 2. UF_UI_POINT_CURSOR_POS
    # 3. UF_UI_POINT_EXISTING_PT
    # 4. UF_UI_POINT_END_PT
    # 5. UF_UI_POINT_CONTROL_PT
    # 6. UF_UI_POINT_INTERSECT_PT
    # 7. UF_UI_POINT_CENTER_PT
    # 8. UF_UI_POINT_ANGLE_PT
    # 9. UF_UI_POINT_QUADRANT_PT
    # 10. UF_UI_POINT_ON_CURVE_PT
    # 11. UF_UI_POINT_ON_SURFACE_PT
    # 12. UF_UI_POINT_OFFSET_CSYS_PT
    # 13. UF_UI_POINT_DIALOG
    # 14. UF_UI_POINT_NO_METHOD
    # 15. UF_UI_POINT_APPLICATION_METHOD

    '''Another pt construction dialog with more customization options'''
    # sel_type = 0 # Described below
    # offset_mode = 0 # Described below
    # mode = [sel_type, offset_mode]
    # pt_display_mode = 0 # 0 = Display temp pts, 1 = Do not display temp pts
    # lockUG()
    # pt_subfunction = theUFUi.PointSubfunction("CUE", mode, pt_display_mode) # Returns mode, Point3d representation, and response int
    # unlockUG()
    # lw(pt_subfunction)

    # mode information
    # (list of int) On input the default selection type and offset mode. On output the selection type and offset mode used.
    # [0] Selection Type 0 = Show Menu For User Selection (Inferred) 1 = Cursor Location 2 = This value is ignored.
    # 3 = This value is ignored. 4 = Existing Point 5 = End Point 6 = Control Point 7 = Intersection Point
    # 8 = Arc/Ellipse/Sphere Center 9 = Pos On Arc/Ellipse 10 = This value is ignored. 11 = Intersection Point 12 = Quadrant Point
    # 13 = Point on curve/Edge 14 = Point on Surface 15 = Point Between Points 16 = Cursor Location 17 = This value is ignored.
    # [1] Offset Mode 0 = No Offset 1 = Rect Abs 2 = This value is ignored. 3 = Cylindrical 4 = Spherical 5 = 3D Vector 6 = 3D Vector

    '''Displays selectable 'coneheads', not sure why you would ever want to use this'''
    # number_of_coneheads = 3
    # origins = [0.0, 0.0, 0.0, 0.0, -500.0, 0.0, 0.0, 500.0, 0.0]
    # directions = [0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    # labels = ["CONEHEAD #1", "CONEHEAD #2", "CONEHEAD #3"]
    # attr_type = NXOpen.UF.Disp.ConeheadAttrbSTag()
    # attr_type.StaffLength = 0.6
    # attr_type.TotalLength = 1.0
    # attr_type.ConeRadius = 0.075
    # attr_type.Color = 0
    # attr_type.Font = 1
    # attr_type.Density = 0
    # attributes = [attr_type, attr_type, attr_type]
    # sel_point = 0.5
    # display_coneheads = 1
    # lockUG()
    # sel_coneheads:tuple = theUFUi.SelectConehead("CUE MESSAGE", number_of_coneheads, origins, directions, labels, attributes, sel_point, display_coneheads)
    # unlockUG()
    # selected_conehead = sel_coneheads[0]
    # response = sel_coneheads[1]
    # lw(sel_coneheads)

    ''''''
    

    # attr_and_methods = dir(UiPointBaseMethodMemberType)
    # attr_and_methods_filtered = [attr for attr in dir(UiPointBaseMethodMemberType) if not attr.startswith("__")]
    # lw(attr_and_methods, attr_and_methods_filtered)

    info_window.Close()

if __name__ == "__main__":
    main()