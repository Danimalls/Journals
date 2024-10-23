import math
import os
import NXOpen
from NXOpen import *
from NXOpen.UF import *
from NXOpen.Assemblies import *
from NX_Lib import PanelCurvePointFinder

def main():
    theSession:Session = Session.GetSession()
    theUFSession:UFSession = UFSession.GetUFSession()
    session_part_collection:PartCollection = theSession.Parts
    workPart:Part = session_part_collection.Work
    displayPart:Part = session_part_collection.Display
    comp_assy:ComponentAssembly = workPart.ComponentAssembly
    dispManager:DisplayManager = theSession.DisplayManager
    theUI:UI = UI.GetUI()
    nxMessageBox:NXMessageBox = theUI.NXMessageBox
    updateManager:Update = theSession.UpdateManager
    theUFUi = NXOpen.UF.Ui()
    nx_exceptions = NXOpen.NXException
    lw:ListingWindow = theSession.ListingWindow

    mask_component:Selection.MaskTriple = Selection.MaskTriple()
    mask_component.Type = UFConstants.UF_component_type
    mask_component.Subtype = UFConstants.UF_component_subtype

    mask_solid_body:Selection.MaskTriple = Selection.MaskTriple()
    mask_solid_body.Type = UFConstants.UF_solid_type
    mask_solid_body.Subtype = UFConstants.UF_solid_body_subtype

    mask_sheet_body:Selection.MaskTriple = Selection.MaskTriple()
    mask_sheet_body.Type = UFConstants.UF_solid_type
    mask_sheet_body.Subtype = UFConstants.UF_solid_body_subtype
    mask_sheet_body.SolidBodySubtype = UFConstants.UF_UI_SEL_FEATURE_SHEET_BODY

    jobPath = os.path.dirname(workPart.FullPath)
    jobNum = jobPath[-4:]
    jobPath += "\\"

    basePoint1: Point3d = Point3d(0.0, 0.0, 0.0)
    orientation1: Matrix3x3 = Matrix3x3()
    orientation1.Xx = 1.0
    orientation1.Xy = 0.0
    orientation1.Xz = 0.0
    orientation1.Yx = 0.0
    orientation1.Yy = 1.0
    orientation1.Yz = 0.0
    orientation1.Zx = 0.0
    orientation1.Zy = 0.0
    orientation1.Zz = 1.0

    lw.Open()

    markId1 = theSession.SetUndoMark(Session.MarkVisibility.Visible, "Start")

    slide_position:list = [0,
    0.1524,
    0.5334,
    1.1176,
    1.905,
    2.921,
    4.191,
    5.6642,
    7.366,
    9.3218,
    11.5062,
    13.9192,
    16.6116,
    19.5326,
    22.7076,
    26.162,
    29.845,
    33.8074,
    38.0238,
    42.4942,
    47.244,
    52.2732,
    57.5564,
    63.119,
    68.9356,
    75.0316,
    81.407,
    88.0618,
    94.996,
    102.1842,
    109.6518,
    117.3988,
    125.4252,
    133.7056,
    142.2654,
    151.1046,
    160.1978,
    169.5704,
    179.197,
    189.103,
    199.263,
    209.677,
    220.345,
    231.2924,
    242.4684,
    253.8984,
    265.557,
    277.4696,
    289.6108,
    302.006,
    314.6044,
    327.4314,
    340.487,
    353.7458,
    367.2078,
    380.8984,
    394.7668,
    408.813,
    423.0624,
    437.4896,
    452.0946,
    466.852,
    481.7872,
    496.8494,
    512.064,
    527.431,
    542.8996,
    558.4952,
    574.2178,
    590.042,
    605.9424,
    621.9444,
    638.0226,
    654.1516,
    670.3568,
    686.6128,
    702.8942,
    719.201,
    735.5332,
    751.8654,
    768.1976,
    784.5298,
    800.8366,
    817.0926,
    833.2978,
    849.4522,
    865.5558,
    881.5578,
    897.4582,
    913.2824,
    928.9542,
    944.5244,
    959.9422,
    975.233,
    990.346,
    1005.2812,
    1020.0386,
    1034.5928,
    1048.9438,
    1063.0662,
    1076.9854,
    1090.6252,
    1104.0618,
    1117.1936,
    1130.0714,
    1142.6952,
    1154.9888,
    1167.0284,
    1178.7378,
    1190.117,
    1201.2168,
    1211.961,
    1222.375,
    1232.4588,
    1242.187,
    1251.585,
    1260.6274,
    1269.2888,
    1277.62,
    1285.5702,
    1293.1648,
    1300.4038,
    1307.2618,
    1313.7642,
    1319.911,
    1325.6768,
    1331.087,
    1336.1162,
    1340.8152,
    1345.1332,
    1349.121,
    1352.7532,
    1356.0298,
    1358.9762,
    1361.567,
    1363.853,
    1365.7834,
    1367.409,
    1368.7044,
    1369.695,
    1370.3808,
    1370.2538,
    1370.8634,
    1370.6602,
    1370.1776,
    1369.4156,
    1368.3996,
    1367.1042,
    1365.5294,
    1363.726,
    1361.6686,
    1359.3572,
    1356.8172,
    1354.0486,
    1351.0768,
    1347.851,
    1344.422,
    1340.7898,
    1336.675,
    1332.8904,
    1328.6486,
    1324.229,
    1319.6062,
    1314.8056,
    1309.8526,
    1304.6964,
    1299.3878,
    1293.9014,
    1288.288,
    1282.4968,
    1276.5532,
    1270.4572,
    1264.2342,
    1257.8588,
    1251.3564,
    1244.7016,
    1237.9452,
    1231.0364,
    1224.0006,
    1216.8632,
    1209.5988,
    1202.2328,
    1194.7398,
    1187.1452,
    1179.4236,
    1171.6258,
    1163.7264,
    1155.7,
    1147.5974,
    1139.4186,
    1131.1128,
    1122.7308,
    1114.2726,
    1105.7382,
    1097.1022,
    1088.39,
    1079.6016,
    1070.737,
    1061.8216,
    1052.8046,
    1043.7368,
    1034.5928,
    1025.398,
    1016.127,
    1006.8052,
    997.4326,
    987.9838,
    978.5096,
    968.9592,
    959.3834,
    949.7314,
    940.054,
    930.3258,
    920.5722,
    910.7678,
    900.938,
    891.0574,
    881.1768,
    871.2454,
    861.2886,
    851.3064,
    841.2988,
    831.2912,
    821.2582,
    811.1998,
    801.1414,
    791.0576,
    780.9992,
    770.9154,
    760.8316,
    750.7478,
    740.664,
    730.6056,
    720.5472,
    710.5142,
    700.4812,
    690.4736,
    680.466,
    670.5092,
    660.5778,
    650.6718,
    640.7912,
    630.9614,
    621.157,
    611.4034,
    601.7006,
    592.0486,
    582.4474,
    572.897,
    563.3974,
    553.974,
    544.6014,
    535.305,
    526.0594,
    516.9154,
    507.8222,
    498.8052,
    489.8898,
    481.0506,
    472.2876,
    463.6262,
    455.041,
    446.5574,
    438.1754,
    429.895,
    421.6908,
    413.5882,
    405.6126,
    397.7132,
    389.9408,
    382.2446,
    374.6754,
    367.2078,
    359.8672,
    352.6028,
    345.4654,
    338.4296,
    331.4954,
    324.6882,
    317.9572,
    311.3532,
    304.8508,
    298.45,
    292.1254,
    285.9278,
    279.8318,
    273.812,
    267.8938,
    262.0772,
    258.8768,
    250.6726,
    245.11,
    239.6236,
    234.2134,
    228.8794,
    223.6216,
    218.4146,
    213.2838,
    208.2292,
    203.2,
    198.247,
    193.3702,
    188.5188,
    183.7182,
    178.9684,
    174.244,
    169.5958,
    164.9476,
    160.3502,
    155.8036,
    151.2824,
    146.7866,
    142.3416,
    137.8966,
    133.477,
    129.1082,
    124.7648,
    120.4468,
    116.1542,
    111.887,
    107.6706,
    103.4542,
    99.2886,
    95.1738,
    91.0844,
    87.0204,
    83.0072,
    79.0448,
    75.1332,
    71.247,
    67.4116,
    63.6524,
    59.944,
    56.3118,
    52.7558,
    49.2506,
    45.8216,
    42.4942,
    39.243,
    36.0934,
    33.02,
    30.0482,
    27.2034,
    24.4602,
    21.844,
    19.3294,
    16.9418,
    14.7066,
    12.5984,
    10.6426,
    8.8138,
    7.1628,
    5.6642,
    4.318,
    3.1496,
    2.159,
    1.3462,
    0.7366,
    0.2794,
    0.0508,]

    first_180:list = []
    first_180_rotation:list = []
    last_180:list = []
    last_180_rotation:list = []

    xbar1_x_pts_first_180:list = []
    xbar1_y_pts_first_180:list = []
    xbar2_x_pts_first_180:list = []
    xbar2_y_pts_first_180:list = []
    xbar1_x_pts_last_180:list = []
    xbar1_y_pts_last_180:list = []
    xbar2_x_pts_last_180:list = []
    xbar2_y_pts_last_180:list = []

    xbar_air_box_3d_distance:float = 157.634833159
    xbar_air_box_init_angle_left:float = -71.200114841
    xbar_air_box_init_angle_right:float = 71.200114841

    # Acquire full 360 press degree and rotation of xbar at degrees lists
    myCompAttr:str = ""
    curve_version:str = ""
    try:
        myCompAttr = workPart.GetStringAttribute("Current Curve File")
        curve_version = "V" + myCompAttr.split("/")[-1][-5]
    except:
        pass

    try:
        ou1:str = myCompAttr
        ou2:str = myCompAttr.replace("OU1", "OU2")
        with open(ou1, 'r') as file:
            line_num = 1
            full_cycle = False
            full_cycle_end = False
            for line in file.readlines():
                if line_num == 29:
                    park_info = line.strip()
                    cell_park_position:float = float(park_info)
                if not full_cycle:
                    if line.strip().startswith("0"):
                        full_cycle = True
                if full_cycle:
                    if len(line.strip()) > 1:
                        if not full_cycle_end:
                            if line.strip().startswith("NOTES"):
                                full_cycle_end = True
                        if not full_cycle_end and "DEG" not in line and "IN" not in line and "SPM" not in line:
                            info = line.split()
                            press_deg = int(info[0])
                            rotation = float(info[-1])
                            if press_deg < 180:
                                first_180.append(press_deg)
                                first_180_rotation.append(rotation)
                            else:
                                last_180.append(press_deg)
                                last_180_rotation.append(rotation)
                line_num += 1

        # Acquire Bar 1 and 2 X and Y location lists
        # Park position found on line 29, only item in line
        with open(ou2, 'r') as file:
            full_cycle = False
            full_cycle_end = False
            for line in file.readlines():
                if not full_cycle:
                    if line.strip().startswith("0"):
                        full_cycle = True
                if full_cycle:
                    if len(line.strip()) > 1:
                        if not full_cycle_end:
                            if line.strip().startswith("NOTES"):
                                full_cycle_end = True
                        if not full_cycle_end and "DEG" not in line and "IN" not in line and "SPM" not in line:
                            info = line.split()
                            press_deg = int(info[0])
                            xbar1_x_pt = (float(info[5]) - cell_park_position) * 25.4
                            xbar1_y_pt = (float(info[6]) + 35.75) * 25.4
                            xbar2_x_pt = (float(info[7]) - cell_park_position) * 25.4
                            xbar2_y_pt = (float(info[8]) + 35.75) * 25.4
                            if press_deg < 180:
                                xbar1_x_pts_first_180.append(xbar1_x_pt)
                                xbar1_y_pts_first_180.append(xbar1_y_pt)
                                xbar2_x_pts_first_180.append(xbar2_x_pt)
                                xbar2_y_pts_first_180.append(xbar2_y_pt)
                            else:
                                xbar1_x_pts_last_180.append(xbar1_x_pt)
                                xbar1_y_pts_last_180.append(xbar1_y_pt)
                                xbar2_x_pts_last_180.append(xbar2_x_pt)
                                xbar2_y_pts_last_180.append(xbar2_y_pt)

        full_360 = last_180 + first_180
        full_360_rotation = last_180_rotation + first_180_rotation
        # unique_rotation_degrees = set(full_360_rotation)
        # rotate = True
        # if len(unique_rotation_degrees) < 3:
        #     rotate = False

        xbar1_x_pts_full_360 = xbar1_x_pts_last_180 + xbar1_x_pts_first_180
        xbar1_y_pts_full_360 = xbar1_y_pts_last_180 + xbar1_y_pts_first_180
        xbar2_x_pts_full_360 = xbar2_x_pts_last_180 + xbar2_x_pts_first_180
        xbar2_y_pts_full_360 = xbar2_y_pts_last_180 + xbar2_y_pts_first_180
    except:
        nxMessageBox.Show("Error", NXOpen.NXMessageBox.DialogType.Error, ["Error processing vDos program curve output", "Make sure to run vDos and V180 Curve Draw programs before running this one"])
        lw.Close()
        return

    # Finds motion start/stop degrees for panel curve drawing
    for i in range(358):
        if round(xbar1_x_pts_full_360[i], 4) == round(xbar1_x_pts_full_360[i+1], 4) and round(xbar1_y_pts_full_360[i], 4) == round(xbar1_y_pts_full_360[i+1], 4):
            pass
        else:
            approach_start = i
            break
    for i in range(approach_start, 358):
        if round(xbar1_x_pts_full_360[i], 4) == round(xbar1_x_pts_full_360[i+1], 4) and round(xbar1_y_pts_full_360[i], 4) == round(xbar1_y_pts_full_360[i+1], 4):
            approach_stop = i
            break
    for i in range(approach_stop, 358):
        if round(xbar1_x_pts_full_360[i], 4) == round(xbar1_x_pts_full_360[i+1], 4) and round(xbar1_y_pts_full_360[i], 4) == round(xbar1_y_pts_full_360[i+1], 4):
            pass
        else:
            transfer_start = i
            break
    for i in range(transfer_start, 358):
        if round(xbar1_x_pts_full_360[i], 4) == round(xbar1_x_pts_full_360[i+1], 4) and round(xbar1_y_pts_full_360[i], 4) == round(xbar1_y_pts_full_360[i+1], 4):
            transfer_stop = i
            break
    all_return_degrees = []
    for i in range(transfer_stop, 358):
        if round(xbar1_x_pts_full_360[i], 4) == round(xbar1_x_pts_full_360[i+1], 4) and round(xbar1_y_pts_full_360[i], 4) == round(xbar1_y_pts_full_360[i+1], 4):
            pass
        else:
            all_return_degrees.append(i)
            
    all_approach_degrees = [i for i in range(approach_start, approach_stop+1)]
    all_transfer_degrees = [i for i in range(transfer_start, transfer_stop+1)]

    white = 1
    magenta = 181
    green = 36
    orange = 78

    theSession.FreezePartNavigator()

    def create_360_and_curve(wrkPrt, x, y, cross_flow_value, xbar_num, xbar_curve_count, panel):
        def get_initial_values(x, y):
            if xbar_num == 1:
                x_dif = x - xbar1_x_pts_full_360[0]
                y_dif = y - xbar1_y_pts_full_360[0]
            else:
                x_dif = x - xbar2_x_pts_full_360[0]
                y_dif = y - xbar2_y_pts_full_360[0]
            dist_3d = round(math.sqrt((x_dif * x_dif) + (y_dif * y_dif)), 10)
            start_angle = math.degrees(math.atan(y_dif / x_dif))
            return dist_3d, start_angle

        def get_new_coordinates(dist, angle, xbar_x_point, xbar_y_point):
            angle_radians = math.radians(angle)
            if pt_location == "trailing":
                x = xbar_x_point - (dist * math.cos(angle_radians))
                y = xbar_y_point - (dist * math.sin(angle_radians))
            else:
                x = xbar_x_point + (dist * math.cos(angle_radians))
                y = xbar_y_point + (dist * math.sin(angle_radians))
            return x, y

        # Setup for xbar curves
        if x != 0.0 and y != 0.0:
            dist_3d, initial_angle = get_initial_values(x, y)
            new_x = x
            new_y = y
        else:
            dist_3d = xbar_air_box_3d_distance
            if xbar_curve_count == 1:
                initial_angle = xbar_air_box_init_angle_left
                # Fake number to set intital leading/trailing value
                new_x = -10000.0
            elif xbar_curve_count == 2:
                initial_angle = xbar_air_box_init_angle_right
                # Fake number to set intital leading/trailing value
                new_x = 10000.0

        pt_location = "leading"
        if xbar_num == 1:
            if new_x < xbar1_x_pts_full_360[0]:
                pt_location = "trailing"
        elif xbar_num == 2:
            if new_x < xbar2_x_pts_full_360[0]:
                pt_location = "trailing"

        angle = initial_angle
        comp_locations_full_360 = []
        comp_locations_full_360_theo = []
        # Acquire new PATH X, Y, Z coords
        
        if xbar_curve_count > 0:
            angle += full_360_rotation[0]
        for i, p in enumerate(full_360):
            r = 0
            rot = full_360_rotation[i]
            if i < 359:
                next_rot = full_360_rotation[i+1]
            if i == 359:
                next_rot = full_360_rotation[0]
            r = next_rot - rot
            if xbar_num == 1:
                xbar_x_pt = xbar1_x_pts_full_360[i]
                xbar_y_pt = xbar1_y_pts_full_360[i]
            else:
                xbar_x_pt = xbar2_x_pts_full_360[i]
                xbar_y_pt = xbar2_y_pts_full_360[i]
            new_x, new_y = get_new_coordinates(dist_3d, angle, xbar_x_pt, xbar_y_pt)
            angle += r
            comp_locations_full_360.append([round(new_x, 4), round(cross_flow_value, 4), round(new_y, 4)])

        # Acquire new THEO X, Y, Z coords
        for i, p in enumerate(full_360):
            theo_locations = [c for c in comp_locations_full_360[i][:-1]]
            path_y = comp_locations_full_360[i][-1]
            theo_y = round(path_y - slide_position[i], 4)
            theo_locations.append(theo_y)
            comp_locations_full_360_theo.append(theo_locations)

        all_lines = []
        approach_lines = []
        return_lines = []
        i = 0
        # Draw PATH
        while i < 360:
            start_point = Point3d(round(float(comp_locations_full_360[i][1]), 4), round(float(comp_locations_full_360[i][0]), 4), round(float(comp_locations_full_360[i][2]), 4))
            if i < 359:
                end_point = Point3d(round(float(comp_locations_full_360[i+1][1]), 4), round(float(comp_locations_full_360[i+1][0]), 4), round(float(comp_locations_full_360[i+1][2]), 4))
            else:
                end_point = Point3d(round(float(comp_locations_full_360[0][1]), 4), round(float(comp_locations_full_360[0][0]), 4), round(float(comp_locations_full_360[0][2]), 4))

            if start_point.X != end_point.X or start_point.Y != end_point.Y or start_point.Z != end_point.Z:
                if panel:
                    if i in all_transfer_degrees:
                        line = wrkPrt.Curves.CreateLine(start_point, end_point)
                        if i == 359:
                            line.SetName(f"Press Degree 179-180")
                        else:
                            line.SetName(f"Press Degree {full_360[i]}-{full_360[i+1]}")
                        all_lines.append(line)
                else:
                    line = wrkPrt.Curves.CreateLine(start_point, end_point)
                    if i == 359:
                        line.SetName(f"Press Degree 179-180")
                    else:
                        line.SetName(f"Press Degree {full_360[i]}-{full_360[i+1]}")
                    all_lines.append(line)
                    if i in all_approach_degrees:
                        approach_lines.append(line)
                    if i in all_return_degrees:
                        return_lines.append(line)
            i += 1

        i = 0
        # Draw THEO
        if not panel:
            while i < 360:
                start_point = Point3d(round(float(comp_locations_full_360_theo[i][1]), 4), round(float(comp_locations_full_360_theo[i][0]), 4), round(float(comp_locations_full_360_theo[i][2]), 4))
                if i < 359:
                    end_point = Point3d(round(float(comp_locations_full_360_theo[i+1][1]), 4), round(float(comp_locations_full_360_theo[i+1][0]), 4), round(float(comp_locations_full_360_theo[i+1][2]), 4))
                else:
                    end_point = Point3d(round(float(comp_locations_full_360_theo[0][1]), 4), round(float(comp_locations_full_360_theo[0][0]), 4), round(float(comp_locations_full_360_theo[0][2]), 4))

                if start_point.X != end_point.X or start_point.Y != end_point.Y or start_point.Z != end_point.Z:
                    line = wrkPrt.Curves.CreateLine(start_point, end_point)
                    if i == 359:
                        line.SetName(f"Theo Press Degree 179-180")
                    else:
                        line.SetName(f"Theo Press Degree {full_360[i]}-{full_360[i+1]}")
                    all_lines.append(line)
                i += 1

        display_modification_manager = dispManager.NewDisplayModification()
        display_modification_manager.ApplyToOwningParts = False

        if xbar_num == 1:
            display_modification_manager.NewColor = green
            if panel:
                display_modification_manager.NewColor = magenta
        elif xbar_num == 2:
            display_modification_manager.NewColor = orange

        display_modification_manager.Apply(all_lines)
        display_modification_manager.Dispose()

        if not panel:
            try:
                ref_set_approach.AddObjectsToReferenceSet(approach_lines)
                ref_set_return.AddObjectsToReferenceSet(return_lines)
            except nx_exceptions as ex:
                if ex.ErrorCode == 650002: # Non-existent reference set (main curve file owning components)
                    pass
                else:
                    lw.WriteFullline(ex.ErrorMessage)

    def select_objects(title:str, selType):
        scope = Selection.SelectionScope.AnyInAssembly
        action = Selection.SelectionAction.ClearAndEnableSpecific
        includeFeatures = False
        keepHighlighted = False
        selection:Selection = theUI.SelectionManager
        maskArray = []
        for sel in selType:
            maskArray.append(sel)
        resp:Selection.Response = selection.SelectTaggedObjects("Select Components", title, scope, action, includeFeatures, keepHighlighted, maskArray)
        selected_obj_list:list = resp[1]
        return selected_obj_list

    def create_curve_comp(fname:str):
        fileNew1:FileNew = theSession.Parts.FileNew()
        fileNew1.TemplateFileName = "model-plain-1-mm-template.prt"
        fileNew1.Units = NXOpen.Part.Units.Millimeters
        fileNew1.TemplateType = FileNewTemplateType.Item
        fileNew1.MakeDisplayedPart = False
        fileNew1.NewFileName = fname + ".prt"
        nXObject1:NXObject = fileNew1.Commit()
        properties_manager:PreviewPropertiesBuilder = nXObject1.PropertiesManager.CreatePreviewPropertiesBuilder([nXObject1])
        properties_manager.ModelViewCreation = NXOpen.PreviewPropertiesBuilder.ModelViewCreationOptions.OnDemand
        properties_manager.StorePartPreview = False
        properties_manager.StoreModelViewPreview = False
        properties_manager.Commit()
        properties_manager.Destroy()
        nXObject1.Save(BasePart.SaveComponents.TrueValue, BasePart.CloseAfterSave.FalseValue)

    def ask_panel_curves():
        message_buttons = theUFUi.MessageButtons()
        message_buttons.Button1 = True
        message_buttons.Button2 = False
        message_buttons.Button3 = True
        message_buttons.Label1 = "Yes"
        message_buttons.Label2 = None
        message_buttons.Label3 = "No"
        message_buttons.Response1 = 1
        message_buttons.Response2 = 0
        message_buttons.Response3 = 2

        title:str = "Panel Curves"
        message_type = theUFUi.MessageDialogType.MESSAGE_QUESTION
        message:list[str] = ["Create Panel Curves?"]
        num_msgs:int = 1
        translate:bool = True

        resp = theUFUi.MessageDialog(title, message_type, message, num_msgs, translate, message_buttons)

        if resp == 1:
            return True
        else:
            return False
        
    def create_panel_curves():
        # Run panel curve pt finder
        myPanelPtFinder = PanelCurvePointFinder()
        panel_curve_pts = myPanelPtFinder.RunPanelCurves(False)

        panel_curve_path = f"{jobPath}Curve Data\\{workPart.Leaf[:6]}\\Panel Curves\\"
        if not os.path.exists(panel_curve_path):
            os.mkdir(panel_curve_path)
        panel_filename = f"AS-{jobNum}_{workPart.Leaf[:6]}_Panel Curves_{curve_version}"
        panel_original_filename = panel_filename
        panel_file_full_path = panel_curve_path + panel_filename
        panel_original_file_full_path = panel_file_full_path

        panel_file_made = False
        panel_file_count = 1
        while not panel_file_made:
            if not os.path.exists(panel_file_full_path + ".prt"):
                create_curve_comp(panel_file_full_path)
                panel_file_made = True
            else:
                panel_file_full_path = f"{panel_original_file_full_path}.{panel_file_count}"
                panel_filename = f"{panel_original_filename}.{panel_file_count}"
                panel_file_count += 1

        addPanelComp1:Component = comp_assy.AddComponent(panel_file_full_path, "ENTIRE PART", panel_filename + ".prt", basePoint1, orientation1, -1, True)
        session_part_collection.SetWorkComponent(addPanelComp1[0], PartCollection.RefsetOption.Entire, PartCollection.WorkComponentOption.Visible)
        newWorkPart = session_part_collection.Work

        display_mod_manager = dispManager.NewDisplayModification()
        display_mod_manager.ApplyToOwningParts = False
        display_mod_manager.NewColor = magenta

        for pnl_curve_pts_list in panel_curve_pts:
            for pt in pnl_curve_pts_list:
                panel_curve_comp_made = False
                panel_curve_comp_count = 1
                panel_curve_name = f"AS-{jobNum}_{workPart.Leaf[:6]}_{curve_version}_Panel Curve_"
                panel_curve_file_full_path = panel_curve_path + panel_curve_name

                while not panel_curve_comp_made:
                    if not os.path.exists(panel_curve_file_full_path + str(panel_curve_comp_count) + ".prt"):
                        panel_curve_file_full_path += str(panel_curve_comp_count)
                        create_curve_comp(panel_curve_file_full_path)
                        panel_curve_comp_made = True
                    else:
                        panel_curve_comp_count += 1

                panel_curve_file_name_for_adding_comp = panel_curve_name + str(panel_curve_comp_count) + ".prt"
                panel_owning_curve_comp_assy:ComponentAssembly = newWorkPart.ComponentAssembly
                panel_curve_comp = panel_owning_curve_comp_assy.AddComponent(panel_curve_file_full_path, "ENTIRE PART", panel_curve_file_name_for_adding_comp, basePoint1, orientation1, -1, True)
                new_panel_curve_comp = displayPart.ComponentAssembly.MapComponentsFromSubassembly(panel_curve_comp[0])
                session_part_collection.SetWorkComponent(new_panel_curve_comp[0], PartCollection.RefsetOption.Entire, PartCollection.WorkComponentOption.Visible)
                individualPanelCurveWorkPart = session_part_collection.Work

                newPt:Point = individualPanelCurveWorkPart.Points.CreatePoint(Point3d(pt[0], pt[1], pt[2]))

                display_mod_manager.Apply([newPt])

                newPt.SetVisibility(SmartObject.VisibilityOption.Visible)
                create_360_and_curve(individualPanelCurveWorkPart, pt[1], pt[2], pt[0], 1, 0, True)
        newWorkPart.Save(BasePart.SaveComponents.TrueValue, BasePart.CloseAfterSave.FalseValue)

        display_mod_manager.Dispose()

        session_part_collection.SetActiveDisplay(displayPart, DisplayPartOption.AllowAdditional, PartDisplayPartWorkPartOption.SameAsDisplay)

    # Arrangement testing
    rest:Arrangement = None
    rest_start = False
    c:ComponentAssembly = workPart.ComponentAssembly
    initial_arrangement:Arrangement = c.ActiveArrangement
    for ar in c.Arrangements:
        if ar.Name.lower() == "rest":
            rest = ar
    if rest:
        if rest.Name != initial_arrangement.Name:
            c.ActiveArrangement = rest
        else:
            rest_start = True
    else:
        lw.WriteFullline(f"Cannot find 'Rest' Arrangement. Make sure Rest arrangemnt exists and is setup properly before running this program.")
        return

    point_names = ["CURVE_PT_1", "CURVE_PT_2", "CURVE_PT_3", "CURVE_PT_4"]
    for xbar_num in range(1, 3):
        xbar_desc = "DEF"
        if xbar_num == 1:
            xbar_desc = "ABC"
        comps = select_objects(f"Select all cups for Xbar {xbar_num} ({xbar_desc})", [mask_component])
        if comps:
            cup_count = 1
            curve_path = f"{jobPath}Curve Data\\{workPart.Leaf[:6]}\\Xbar {xbar_num}\\"
            if not os.path.exists(curve_path):
                os.mkdir(curve_path)
            filename = f"AS-{jobNum}_{workPart.Leaf[:6]}_Xbar {xbar_num}_Cup Curves_{curve_version}"
            original_filename = filename
            file_full_path = curve_path + filename
            original_file_full_path = file_full_path

            file_made = False
            file_count = 1
            while not file_made:
                if not os.path.exists(file_full_path + ".prt"):
                    create_curve_comp(file_full_path)
                    file_made = True
                else:
                    file_full_path = f"{original_file_full_path}.{file_count}"
                    filename = f"{original_filename}.{file_count}"
                    file_count += 1

            addcomp1:Component = comp_assy.AddComponent(file_full_path, "ENTIRE PART", filename + ".prt", basePoint1, orientation1, -1, True)
            session_part_collection.SetWorkComponent(addcomp1[0], PartCollection.RefsetOption.Entire, PartCollection.WorkComponentOption.Visible)
            newWorkPart = session_part_collection.Work
            for comp in comps:
                cup_pts_for_curves = []
                initial_ref_set = comp.ReferenceSet
                if initial_ref_set != "Entire Part":
                    comp.DirectOwner.ReplaceReferenceSet(comp, "Entire Part")
                comp_part = comp.Prototype
                for pt_name in point_names:
                    for pt in comp_part.Points:
                        if pt.Name == pt_name:
                            pt_for_curve = comp.FindOccurrence(pt).Coordinates
                            cup_pts_for_curves.append(pt_for_curve)
                if cup_pts_for_curves:
                    curve_comp_made = False
                    curve_comp_count = 1
                    curve_name = f"AS-{jobNum}_{workPart.Leaf[:6]}_Xbar {xbar_num}_{curve_version}_Cup Curve_"
                    curve_file_full_path = curve_path + curve_name

                    while not curve_comp_made:
                        if not os.path.exists(curve_file_full_path + str(curve_comp_count) + ".prt"):
                            curve_file_full_path += str(curve_comp_count)
                            create_curve_comp(curve_file_full_path)
                            curve_comp_made = True
                        else:
                            curve_comp_count += 1

                    curve_file_name_for_adding_comp = curve_name + str(curve_comp_count) + ".prt"
                    owning_curve_comp_assy:ComponentAssembly = newWorkPart.ComponentAssembly
                    curve_comp = owning_curve_comp_assy.AddComponent(curve_file_full_path, "ENTIRE PART", curve_file_name_for_adding_comp, basePoint1, orientation1, -1, True)
                    new_curve_comp = displayPart.ComponentAssembly.MapComponentsFromSubassembly(curve_comp[0])
                    session_part_collection.SetWorkComponent(new_curve_comp[0], PartCollection.RefsetOption.Entire, PartCollection.WorkComponentOption.Visible)
                    individualCurveWorkPart = session_part_collection.Work
                    ref_set_approach = individualCurveWorkPart.CreateReferenceSet()
                    ref_set_approach.SetName("Approach")
                    ref_set_return = individualCurveWorkPart.CreateReferenceSet()
                    ref_set_return.SetName("Return")

                    for i, pt in enumerate(cup_pts_for_curves):
                        create_360_and_curve(individualCurveWorkPart, pt.Y, pt.Z, pt.X, xbar_num, 0, False)
                    cup_count += 1

            create_360_and_curve(newWorkPart, 0.0, 0.0, -2163.711000000, xbar_num, 1, False)
            create_360_and_curve(newWorkPart, 0.0, 0.0, -2163.711000000, xbar_num, 2, False)
            newWorkPart.Save(BasePart.SaveComponents.TrueValue, BasePart.CloseAfterSave.FalseValue)

            session_part_collection.SetActiveDisplay(displayPart, DisplayPartOption.AllowAdditional, PartDisplayPartWorkPartOption.SameAsDisplay)

    if ask_panel_curves():
        create_panel_curves()

    theSession.UnfreezePartNavigator()
    updateManager.DoUpdate(markId1)

    if not rest_start:
        c.ActiveArrangement = initial_arrangement

    lw.Close()

if __name__ == "__main__":
    main()

