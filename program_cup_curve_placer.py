import os
import NXOpen
import NXOpen.UF
import NXOpen.Features
import NXOpen.Assemblies
import NXOpen.Positioning

def main():
    # session variables
    theSession = NXOpen.Session.GetSession()
    theUFSession = NXOpen.UF.UFSession.GetUFSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    theUI = NXOpen.UI.GetUI()
    lw = theSession.ListingWindow
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
        components = selection.SelectTaggedObjects("Select components", title, scope, action, includeFeatures, keepHighlighted, maskArray)
        components_list = components[1]
        return components_list

    markId1 = theSession.SetUndoMark(NXOpen.Session.MarkVisibility.Visible, "Start")

    curve_directory = f"{os.path.dirname(workPart.FullPath)[:23]}\\Simulations\\Curves\\Design\\"
    try:
        all_curves = [curve for curve in os.listdir(curve_directory)]
    except FileNotFoundError:
        all_curves = []
    check_curves = []
    for curve in all_curves:
        if "front" in curve.lower() and "path" in curve.lower():
            front_path_curve = curve
            check_curves.append(front_path_curve)
        elif "front" in curve.lower() and "theo" in curve.lower():
            front_theo_curve = curve
            check_curves.append(front_theo_curve)
        elif "rear" in curve.lower() and "path" in curve.lower():
            rear_path_curve = curve
            check_curves.append(rear_path_curve)
        elif "rear" in curve.lower() and "theo" in curve.lower():
            rear_theo_curve = curve
            check_curves.append(rear_theo_curve)

    if len(check_curves) == 0:    
        curve_to_use = select_components("Select Cup Curve")[0]
        if "curve" in curve_to_use.Name.lower() or "f-line" in curve_to_use.Name.lower():
            comp_path = curve_to_use.Prototype.FullPath
            comp_name = curve_to_use.Name
            ref_set = curve_to_use.ReferenceSet
            matrix = curve_to_use.GetPosition()[1]

            comps = select_components("Select All Cups/Sensors")
            point_names = ["CURVE_PT_1", "CURVE_PT_2", "CURVE_PT_3", "CURVE_PT_4"]
            for comp in comps:
                initial_ref_set = comp.ReferenceSet
                if initial_ref_set != "Entire Part":
                    comp.DirectOwner.ReplaceReferenceSet(comp, "Entire Part")
                comp_part = comp.Prototype
                if comp_part.IsFullyLoaded == False:
                    comp_part.LoadThisPartFully()
                for pt_name in point_names:
                    for pt in comp_part.Points:
                        if pt.Name == pt_name:
                            pt_to_add = comp.FindOccurrence(pt).Coordinates
                            addcomp1 = workPart.ComponentAssembly.AddComponent(comp_path, ref_set, comp_name, pt_to_add, matrix, -1, True)
                comp.DirectOwner.ReplaceReferenceSet(comp, initial_ref_set)
        else:
            theUFSession.Ui.DisplayMessage("Invalid curve selected", 1)
            return

    else:
        default_matrix = NXOpen.Matrix3x3()
        default_matrix.Xx = 1.0
        default_matrix.Xy = 0.0
        default_matrix.Xz = 0.0
        default_matrix.Yx = 0.0
        default_matrix.Yy = 1.0
        default_matrix.Yz = 0.0
        default_matrix.Zx = 0.0
        default_matrix.Zy = 0.0
        default_matrix.Zz = 1.0
        ref_set = "Entire Part"
        comps = []
        comps_selection = select_components("Select All Grippers/Shovels")
        point_names = ["PATH_PT_1", "PATH_PT_2", "THEO_PT_1", "THEO_PT_2"]
        flange = False
        for comp in comps_selection:
            if "GRM2SF" in comp.DisplayName:
                flange = True
            else:
                comps.append(comp)
        if flange:
            theUFSession.Ui.DisplayMessage("This journal is not setup to work with flange-style grippers since they have multiple different possible orientations", 1)
        for comp in comps:
            upsidedown = False
            ref_point, ref_matrix = comp.GetPosition()
            front = False
            rear = False
            initial_ref_set = comp.ReferenceSet
            if initial_ref_set != "Entire Part":
                comp.DirectOwner.ReplaceReferenceSet(comp, "Entire Part")
            comp_part = comp.Prototype
            if comp_part.IsFullyLoaded == False:
                comp_part.LoadThisPartFully()
            for point in comp_part.Points:
                if point.Name in point_names:
                    pt_coords = comp.FindOccurrence(point).Coordinates
                    if pt_coords.X > 0:
                        front = True
                    else:
                        rear = True
                    if pt_coords.Z > ref_point.Z and "PATH" in point.Name:
                        upsidedown = True
                    if upsidedown:
                        if front and "path" in point.Name.lower():
                            comp_name = front_theo_curve[:-4]
                            comp_path = f"{curve_directory}{front_theo_curve}"
                        elif front and "theo" in point.Name.lower():
                            comp_name = front_path_curve[:-4]
                            comp_path = f"{curve_directory}{front_path_curve}"
                        elif rear and "path" in point.Name.lower():
                            comp_name = rear_theo_curve[:-4]
                            comp_path = f"{curve_directory}{rear_theo_curve}"
                        elif rear and "theo" in point.Name.lower():
                            comp_name = rear_path_curve[:-4]
                            comp_path = f"{curve_directory}{rear_path_curve}"
                    else:
                        if front and "path" in point.Name.lower():
                            comp_name = front_path_curve[:-4]
                            comp_path = f"{curve_directory}{front_path_curve}"
                        elif front and "theo" in point.Name.lower():
                            comp_name = front_theo_curve[:-4]
                            comp_path = f"{curve_directory}{front_theo_curve}"
                        elif rear and "path" in point.Name.lower():
                            comp_name = rear_path_curve[:-4]
                            comp_path = f"{curve_directory}{rear_path_curve}"
                        elif rear and "theo" in point.Name.lower():
                            comp_name = rear_theo_curve[:-4]
                            comp_path = f"{curve_directory}{rear_theo_curve}"
                    addcomp1 = workPart.ComponentAssembly.AddComponent(comp_path, ref_set, comp_name, pt_coords, default_matrix, -1, True)
            comp.DirectOwner.ReplaceReferenceSet(comp, initial_ref_set)

    lw.Close()

if __name__ == "__main__":
    main()

