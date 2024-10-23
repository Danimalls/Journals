import NXOpen, NXOpen.UF, NXOpen.Assemblies
from NXOpen import *
from NXOpen.UF import *
from NXOpen.Assemblies import *

class PanelCurvePointFinder():
    """
    Methods:
        RunPanelCurves(add_curves=True)
    """
    def __init__(self):
        # Session/NX variables
        self.theSession:Session = Session.GetSession()
        self.theUFSession:UFSession = UFSession.GetUFSession()
        self.theUI:UI = UI.GetUI()

        self.partCollection:PartCollection = self.theSession.Parts
        self.workPart:Part = self.partCollection.Work
        self.displayPart:Part = self.partCollection.Display
        self.compAssy:ComponentAssembly = self.workPart.ComponentAssembly
        self.lw:ListingWindow = self.theSession.ListingWindow

        self.UFModeling = self.theUFSession.Modeling
        
        self.selManager:Selection = self.theUI.SelectionManager
        self.info_window:ListingWindow = self.theSession.ListingWindow
        
        # Global variables
        self.default_matrix:Matrix3x3 = Matrix3x3()
        self.default_matrix.Xx = 1
        self.default_matrix.Xy = 0
        self.default_matrix.Xz = 0
        self.default_matrix.Yx = 0
        self.default_matrix.Yy = 1
        self.default_matrix.Yz = 0
        self.default_matrix.Zx = 0
        self.default_matrix.Zy = 0
        self.default_matrix.Zz = 1

        self.curve_full_path = ""
        self.curve_name = ""
        self.curve_ref_set = None
        self.buffer_75 = 75
        self.flange_buffer_150 = 150
        self.secondary_buffer_150 = 150
        self.buffer_50 = 50
        self.buffer_inside_105 = 105
        self.buffer_outside_1000 = 1000
        self.x = 0
        self.y = 1
        self.z = 2

    # Selection functions
    def __SelectCurve(self, prompt:str):
        title:str = "Select Panel Curve"
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly

        selMask:Selection.MaskTriple = Selection.MaskTriple()
        selMask.Type = UFConstants.UF_component_type
        selMask.Subtype = 0
        selMaskArray:list[Selection.SelectionMaskTriple] = [selMask]

        selObj = self.selManager.SelectTaggedObject(prompt, title, scope, selAction, includeFeatures, keepHighlighted, selMaskArray)
        return selObj
    
    def __SelectPanelBody(self, prompt:str):
        title:str = "Select Panels"
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly
        resp:Selection.Response

        selMask:Selection.MaskTriple = Selection.MaskTriple()
        selMask.Type = UFConstants.UF_solid_type
        selMask.Subtype = UFConstants.UF_solid_body_subtype
        selMask.SolidBodySubtype = UFConstants.UF_UI_SEL_FEATURE_SHEET_BODY

        selMask2:Selection.MaskTriple = Selection.MaskTriple()
        selMask2.Type = UFConstants.UF_solid_type
        selMask2.Subtype = UFConstants.UF_solid_body_subtype

        selMaskArray:list[Selection.SelectionMaskTriple] = [selMask, selMask2]

        # selMask:Selection.MaskTriple = Selection.MaskTriple()
        # selMask.Type = UFConstants.UF_component_type
        # selMask.Subtype = 0
        # selMaskArray:list[Selection.SelectionMaskTriple] = [selMask]

        resp, selObj = self.selManager.SelectTaggedObjects(prompt, title, scope, selAction, includeFeatures, keepHighlighted, selMaskArray)
        return selObj
    
    # Function for adding curves onto found points
    def __AddCurves(self, pts_list):
        curves_added = []
        for pt in pts_list:
            point:Point3d = Point3d()
            point.X = pt[self.x]
            point.Y = pt[self.y]
            point.Z = pt[self.z]
            pt[self.x] = round(pt[self.x], 1)
            pt[self.y] = round(pt[self.y], 1)
            pt[self.z] = round(pt[self.z], 1)
            if pt not in curves_added:
                addComp = self.compAssy.AddComponent(self.curve_full_path, self.curve_ref_set, self.curve_name, point, self.default_matrix, -1, True)
                curves_added.append(pt)

    # Function to get list of pts for panel curves to be placed on
    def __GetPoints(self, panel):
        # for panel in selected_bodies:
        self.lw.Open()
        all_panel_pts = []
        mirror_part = False
        for body in panel:
            panel_edges = self.UFModeling.AskBodyEdges(body.Tag)
            for edge in panel_edges:
                edge_pts = self.UFModeling.AskEdgeVerts(edge)
                for pt in edge_pts[:2]:
                    if pt not in all_panel_pts:
                        if round(pt[self.z]) != 0.0:
                            all_panel_pts.append(pt)

        z_coords = [round(coord[self.z]) for coord in all_panel_pts]
        unique_z_coors = set(z_coords)
        blank = False
        if len(unique_z_coors) < 3:
            blank = True

        lowest_pt = min(all_panel_pts, key=lambda coord: coord[self.z])
        pts_for_curves = []
        if "rivian" not in self.workPart.FullPath.lower():
            far_left = min(all_panel_pts, key=lambda coord: coord[self.x])
            far_right = max(all_panel_pts, key=lambda coord: coord[self.x])
            far_leading = max(all_panel_pts, key=lambda coord: coord[self.y])
            far_trailing = min(all_panel_pts, key=lambda coord: coord[self.y])

            all_pts_left = [coord for coord in all_panel_pts if round(coord[self.x], 2) < (far_left[self.x] + self.buffer_75)]
            all_pts_right = [coord for coord in all_panel_pts if round(coord[self.x], 2) > (far_right[self.x] - self.buffer_75)]
            all_pts_leading = [coord for coord in all_panel_pts if round(coord[self.y], 2) > (far_leading[self.y] - self.buffer_75)]
            all_pts_trailing = [coord for coord in all_panel_pts if round(coord[self.y], 2) < (far_trailing[self.y] + self.buffer_75)]

# Checklist order:
# 1. Create two small sections on opposite ends of pts list you are checking (buffer lists/panel sections)
# 2. Find low point of these new sections, then check to see if that low pt is lower than your original far point.
# 3. If the pt is lower, that is the new pt for curve, otherwise, the original far out pt is pt for curve.
# 4. Check to see if your 2 points are either the same, or are too close to eachother (approx 50mm apart) for entire side of panel
# 5. If either scenario is true, keep the leading point and find a new trailing point by creating another new buffer list/panel section
# 6. If this new panel section contains any pts, take the lowest Z point and use that for your curve.
# 7. Otherwise, you will end up with 1 panel pt for this side of the panel.
# 8. Lastly, if any of these curve points you have found are more than 50mm from the farthest point of the respective side of the panel,
#    AND either point is near the same height, add the farthest point to curve list.

            if len(all_pts_left) > 1:
                pt_left_1 = min(all_pts_left, key=lambda coord: coord[self.y])
                pt_left_2 = max(all_pts_left, key=lambda coord: coord[self.y])
                sep = pt_left_2[self.y] - pt_left_1[self.y]

                # Step 1
                if sep < 200:
                    lead_buffer_list = [coord for coord in all_pts_left if coord[self.y] > (pt_left_2[self.y] - 30)]
                else:
                    lead_buffer_list = [coord for coord in all_pts_left if coord[self.y] > (pt_left_2[self.y] - self.buffer_inside_105)]
                lead_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] < (pt_left_2[self.y] + self.buffer_outside_1000)) and (coord[self.y] > pt_left_2[self.y])) and coord[self.x] < (pt_left_2[self.x] + self.buffer_75)]
                lead_buffer_list_final = lead_buffer_list + lead_buffer_list_2

                if sep < 200:
                    trail_buffer_list = [coord for coord in all_pts_left if coord[self.y] < (pt_left_1[self.y] + 30)]
                else:
                    trail_buffer_list = [coord for coord in all_pts_left if coord[self.y] < (pt_left_1[self.y] + self.buffer_inside_105)]
                trail_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] > (pt_left_1[self.y] - self.buffer_outside_1000)) and (coord[self.y] < pt_left_1[self.y])) and coord[self.x] < (pt_left_1[self.x] + self.buffer_75)]
                trail_buffer_list_final = trail_buffer_list + trail_buffer_list_2

                # Step 2-3
                low_pt_left_lead = pt_left_2
                low_pt_left_lead_test = min(lead_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_left_lead_test[self.z] < (pt_left_2[self.z] - 7):
                    low_pt_left_lead = low_pt_left_lead_test

                low_pt_left_trail = pt_left_1
                low_pt_left_trail_test = min(trail_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_left_trail_test[self.z] < (pt_left_1[self.z] - 7):
                    low_pt_left_trail = low_pt_left_trail_test

                # Step 4-7
                if low_pt_left_lead == low_pt_left_trail or low_pt_left_trail[self.y] > low_pt_left_lead[self.y] - 50:
                    trail_buffer_list_final_modified = [coord for coord in all_panel_pts if ((coord[self.y] > (pt_left_1[self.y] - self.buffer_outside_1000)) and (coord[self.y] < (pt_left_1[self.y] - 200))) and coord[self.x] < (pt_left_1[self.x] + self.secondary_buffer_150)]

                    if len(trail_buffer_list_final_modified) > 0:
                        low_pt_left_trail = min(trail_buffer_list_final_modified, key=lambda coord: coord[self.z])
                    else:
                        low_pt_left_trail = low_pt_left_lead

                # Step 8
                if (low_pt_left_lead[self.x] > (far_left[self.x] + self.buffer_50) or low_pt_left_trail[self.x] > (far_left[self.x] + self.buffer_50)) and far_left not in pts_for_curves:
                    if low_pt_left_lead[self.z] > (far_left[self.z] - 10) or low_pt_left_trail[self.z] > (far_left[self.z] - 10):
                        pts_for_curves.append(far_left)

                pts_for_curves.append(low_pt_left_lead)
                if low_pt_left_trail not in pts_for_curves:
                    pts_for_curves.append(low_pt_left_trail)
            elif len(all_pts_left) == 1:
                pts_for_curves.append(all_pts_left[self.x])

            if len(all_pts_right) > 1:
                pt_right_1 = min(all_pts_right, key=lambda coord: coord[self.y])
                pt_right_2 = max(all_pts_right, key=lambda coord: coord[self.y])
                sep = pt_right_2[self.y] - pt_right_1[self.y]

                # Takes right pts list and splits it into two small sections. Leading right side pts and Trailing right side pts
                # Leading right side pts (contains two lists)
                # List 1: All pts between leading-most right pt, and 100mm behind flow of leading-most right point (from all right pts list)
                if sep < 200:
                    lead_buffer_list = [coord for coord in all_pts_right if coord[self.y] > (pt_right_2[self.y] - 30)]
                else:
                    lead_buffer_list = [coord for coord in all_pts_right if coord[self.y] > (pt_right_2[self.y] - self.buffer_inside_105)]
                # List 2: All pts between leading-most right pt, 1000mm more in-flow of leading-most right pt, and still on right side of panel (from all panel pts list)
                lead_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] < (pt_right_2[self.y] + self.buffer_outside_1000)) and (coord[self.y] > pt_right_2[self.y])) and coord[self.x] > (pt_right_2[self.x] - self.buffer_75)]
                # Combined list 1 and 2
                lead_buffer_list_final = lead_buffer_list + lead_buffer_list_2

                # Trailing right side pts (contains two lists)
                # List 1: All pts between Trailing-most right pt, and 100mm more in-flow of Trailing-most right point (from all right pts list)
                if sep < 200:
                    trail_buffer_list = [coord for coord in all_pts_right if coord[self.y] < (pt_right_1[self.y] + 30)]
                else:
                    trail_buffer_list = [coord for coord in all_pts_right if coord[self.y] < (pt_right_1[self.y] + self.buffer_inside_105)]
                # List 2: All pts between Trailing-most right pt, 1000mm behind flow of Trailing-most right pt, and still on right side of panel (from all panel pts list)
                trail_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] > (pt_right_1[self.y] - self.buffer_outside_1000)) and (coord[self.y] < pt_right_1[self.y])) and coord[self.x] > (pt_right_1[self.x] - self.buffer_75)]
                trail_buffer_list_final = trail_buffer_list + trail_buffer_list_2

                low_pt_right_lead = pt_right_2
                # Check to see if lowest pt in new "panel section" is more than 7mm lower than the Leading, right-most post of all pts right list
                low_pt_right_lead_test = min(lead_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_right_lead_test[self.z] < (pt_right_2[self.z] - 7):
                    # If it is, that new low pt is the pt for the curve, otherwise, the initial farthest out pt is the pt for curve.
                    low_pt_right_lead = low_pt_right_lead_test

                low_pt_right_trail = pt_right_1
                # Check to see if lowest pt in new "panel section" is more than 7mm lower than the Trailing, right-most post of all pts right list
                low_pt_right_trail_test = min(trail_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_right_trail_test[self.z] < (pt_right_1[self.z] - 7):
                    # If it is, that new low pt is the pt for the curve, otherwise, the initial farthest out pt is the pt for curve.
                    low_pt_right_trail = low_pt_right_trail_test

                # If leading and trailing right side pts are the same, or too close to eachother, we make a new "panel section"
                if low_pt_right_lead == low_pt_right_trail or low_pt_right_trail[self.y] > low_pt_right_lead[self.y] - 50:
                    # "Panel section" now has a 200mm buffer in flow behind current trailing-most point, and a 150mm buffer for pts to the left of the trailing-most point
                    trail_buffer_list_final_modified = [coord for coord in all_panel_pts if ((coord[self.y] > (pt_right_1[self.y] - self.buffer_outside_1000)) and (coord[self.y] < (pt_right_1[self.y] - 200))) and coord[self.x] > (pt_right_1[self.x] - self.secondary_buffer_150)]

                    # If this new panel sections finds ANY pts, take the one with the lowest Z and add it to list of points for curves
                    if len(trail_buffer_list_final_modified) > 0:
                        low_pt_right_trail = min(trail_buffer_list_final_modified, key=lambda coord: coord[self.z])
                    else:
                        # Otherwise, set trail pt same as lead pt so it does not get added
                        low_pt_right_trail = low_pt_right_lead

                # If either leading or trailing low points are more than 50mm from far right side of panel, AND
                # either Z is higher than far right side pt Z - 10mm, also add curve to pt that is farthest right on the panel
                if (low_pt_right_lead[self.x] < (far_right[self.x] - self.buffer_50) or low_pt_right_trail[self.x] < (far_right[self.x] - self.buffer_50)) and far_right not in pts_for_curves:
                    if low_pt_right_lead[self.z] > (far_right[self.z] - 10) or low_pt_right_trail[self.z] > (far_right[self.z] - 10):
                        pts_for_curves.append(far_right)

                if low_pt_right_lead not in pts_for_curves:
                    pts_for_curves.append(low_pt_right_lead)
                if low_pt_right_trail not in pts_for_curves:
                    pts_for_curves.append(low_pt_right_trail)
            elif len(all_pts_right) == 1:
                pts_for_curves.append(all_pts_right[self.x])

            if len(all_pts_leading) > 1:
                pt_leading_1 = min(all_pts_leading, key=lambda coord: coord[self.x])
                pt_leading_2 = max(all_pts_leading, key=lambda coord: coord[self.x])
                sep = pt_leading_2[self.x] - pt_leading_1[self.x]

                # Step 1
                if sep < 200:
                    left_buffer_list = [coord for coord in all_pts_leading if coord[self.x] < (pt_leading_1[self.x] + 30)]
                else:
                    left_buffer_list = [coord for coord in all_pts_leading if coord[self.x] < (pt_leading_1[self.x] + self.buffer_inside_105)]
                left_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] > (pt_leading_1[self.x] - self.buffer_outside_1000)) and (coord[self.x] < pt_leading_1[self.x])) and coord[self.y] > (pt_leading_1[self.y] - self.buffer_75)]
                left_buffer_list_final = left_buffer_list + left_buffer_list_2

                if sep < 200:
                    right_buffer_list = [coord for coord in all_pts_leading if coord[self.x] > (pt_leading_2[self.x] - 30)]
                else:
                    right_buffer_list = [coord for coord in all_pts_leading if coord[self.x] > (pt_leading_2[self.x] - self.buffer_inside_105)]
                right_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] < (pt_leading_2[self.x] + self.buffer_outside_1000)) and (coord[self.x] > pt_leading_2[self.x])) and coord[self.y] > (pt_leading_2[self.y] - self.buffer_75)]
                right_buffer_list_final = right_buffer_list + right_buffer_list_2

                # Creating pts
                # for pt in all_pts_leading:
                    # newPt:Point = workPart.Points.CreatePoint(Point3d(pt[self.x], pt[self.y], pt[self.z]))
                    # newPt.SetVisibility(SmartObject.VisibilityOption.Visible)

                # Step 2-3
                low_pt_lead_left = pt_leading_1
                low_pt_lead_left_test = min(left_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_lead_left_test[self.z] < (pt_leading_1[self.z] - 7):
                    low_pt_lead_left = low_pt_lead_left_test

                low_pt_lead_right = pt_leading_2
                low_pt_lead_right_test = min(right_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_lead_right_test[self.z] < (pt_leading_2[self.z] - 7):
                    low_pt_lead_right = low_pt_lead_right_test

                # Step 8
                if (low_pt_lead_left[self.y] < (far_leading[self.y] - self.buffer_50) or low_pt_lead_right[self.y] < (far_leading[self.y] - self.buffer_50)) and (low_pt_left_lead[self.y] > (far_leading[self.y] + self.buffer_50) and low_pt_right_lead[self.y] > (far_leading[self.y] + self.buffer_50)) and far_leading not in pts_for_curves:
                    # if low_pt_lead_left[self.z] > (far_leading[self.z] - 10) or low_pt_lead_right[self.z] > (far_leading[self.z] - 10):
                    # self.lw.WriteFullline(f"Far leading pt added: {far_leading}")
                    pts_for_curves.append(far_leading)

                far_leading_mirror = []
                if (abs(round(low_pt_lead_left[self.x], 1)) == abs(round(low_pt_lead_right[self.x], 1)) and round(low_pt_lead_left[self.z], 1) == round(low_pt_lead_right[self.z], 1) and round(low_pt_lead_left[self.y], 1) == round(low_pt_lead_right[self.y], 1)) and far_leading in pts_for_curves:
                    mirror_part = True
                    far_leading_mirror = far_leading.copy()
                    if far_leading_mirror[self.x] > 0:
                        far_leading_mirror[self.x] = -far_leading_mirror[self.x]
                    elif far_leading_mirror[self.x] < 0:
                        far_leading_mirror[self.x] = abs(far_leading_mirror[self.x])
                    # self.lw.WriteFullline(f"Far leading mirror pt added: {far_leading_mirror}")
                    pts_for_curves.append(far_leading_mirror)

                if low_pt_lead_left not in pts_for_curves and low_pt_lead_left[self.y] < (far_leading[self.y] - self.buffer_50):
                    # self.lw.WriteFullline(f"Low lead left pt added: {low_pt_lead_left}"):
                    pts_for_curves.append(low_pt_lead_left)
                if low_pt_lead_right not in pts_for_curves and low_pt_lead_right[self.y] < (far_leading[self.y] - self.buffer_50):
                    # self.lw.WriteFullline(f"Low lead left pt added: {low_pt_lead_right}")::
                    pts_for_curves.append(low_pt_lead_right)

                # Flange check
                all_pts_leading_flange_check = [coord for coord in all_panel_pts if round(coord[self.y], 2) == round(far_leading[self.y], 2) or round(coord[self.y], 2) > (far_leading[self.y] - self.flange_buffer_150)]
                min_flange_pt = min(all_pts_leading_flange_check, key=lambda coord: coord[self.z])
                if min_flange_pt[self.z] < low_pt_lead_left[self.z] and min_flange_pt[self.z] < low_pt_lead_right[self.z] and not blank:
                    dif = pt_leading_2[self.x] - pt_leading_1[self.x]
                    half_dif = dif / 2

                    left_buffer_list = [coord for coord in all_pts_leading_flange_check if coord[self.x] < (pt_leading_1[self.x] + half_dif)]
                    left_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] > (pt_leading_1[self.x] - self.buffer_outside_1000)) and (coord[self.x] < pt_leading_1[self.x])) and coord[self.y] > (pt_leading_1[self.y] - self.buffer_75)]
                    left_buffer_list_final = left_buffer_list + left_buffer_list_2

                    right_buffer_list = [coord for coord in all_pts_leading_flange_check if coord[self.x] > (pt_leading_2[self.x] - half_dif)]
                    right_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] < (pt_leading_2[self.x] + self.buffer_outside_1000)) and (coord[self.x] > pt_leading_2[self.x])) and coord[self.y] > (pt_leading_2[self.y] - self.buffer_75)]
                    right_buffer_list_final = right_buffer_list + right_buffer_list_2
                    
                    if len(left_buffer_list_final) > 0:
                        low_pt_lead_left_flange = min(left_buffer_list_final, key=lambda coord: coord[self.z])
                        if low_pt_lead_left_flange not in pts_for_curves:
                            pts_for_curves.append(low_pt_lead_left_flange)
                    
                    if len(right_buffer_list_final) > 0:
                        low_pt_lead_right_flange = min(right_buffer_list_final, key=lambda coord: coord[self.z])
                        if low_pt_lead_right_flange not in pts_for_curves:
                            pts_for_curves.append(low_pt_lead_right_flange)
            elif len(all_pts_leading) == 1:
                pts_for_curves.append(all_pts_leading[self.x])

            if len(all_pts_trailing) > 1:
                pt_trailing_1 = min(all_pts_trailing, key=lambda coord: coord[self.x])
                pt_trailing_2 = max(all_pts_trailing, key=lambda coord: coord[self.x])
                sep = pt_trailing_2[self.x] - pt_trailing_1[self.x]

                # Step 1
                if sep < 200:
                    left_buffer_list = [coord for coord in all_pts_trailing if coord[self.x] < (pt_trailing_1[self.x] + 30)]
                else:
                    left_buffer_list = [coord for coord in all_pts_trailing if coord[self.x] < (pt_trailing_1[self.x] + self.buffer_inside_105)]
                left_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] > (pt_trailing_1[self.x] - self.buffer_outside_1000)) and (coord[self.x] < pt_trailing_1[self.x])) and coord[self.y] < (pt_trailing_1[self.y] + self.buffer_75)]
                left_buffer_list_final = left_buffer_list + left_buffer_list_2

                if sep < 200:
                    right_buffer_list = [coord for coord in all_pts_trailing if coord[self.x] > (pt_trailing_2[self.x] - 30)]
                else:
                    right_buffer_list = [coord for coord in all_pts_trailing if coord[self.x] > (pt_trailing_2[self.x] - self.buffer_inside_105)]
                right_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] < (pt_trailing_2[self.x] + self.buffer_outside_1000)) and (coord[self.x] > pt_trailing_2[self.x])) and coord[self.y] < (pt_trailing_2[self.y] + self.buffer_75)]
                right_buffer_list_final = right_buffer_list + right_buffer_list_2

                # Step 2-3
                low_pt_trail_left = pt_trailing_1
                low_pt_trail_left_test = min(left_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_trail_left_test[self.z] < (pt_trailing_1[self.z] - 7):
                    low_pt_trail_left = low_pt_trail_left_test

                low_pt_trail_right = pt_trailing_2
                low_pt_trail_right_test = min(right_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_trail_right_test[self.z] < (pt_trailing_2[self.z] - 7):
                    low_pt_trail_right = low_pt_trail_right_test

                # Step 8
                if (low_pt_trail_left[self.y] > (far_trailing[self.y] + self.buffer_50) or low_pt_trail_right[self.y] > (far_trailing[self.y] + self.buffer_50)) and (low_pt_left_trail[self.y] > (far_trailing[self.y] + self.buffer_50) and low_pt_right_trail[self.y] > (far_trailing[self.y] + self.buffer_50)) and far_trailing not in pts_for_curves:
                    # if low_pt_trail_left[self.z] > (far_trailing[self.z] - 10) or low_pt_trail_right[self.z] > (far_trailing[self.z] - 10):
                    # self.lw.WriteFullline(f"Far trailing pt added: {far_trailing}")
                    pts_for_curves.append(far_trailing)
                    
                far_trailing_mirror = []
                if mirror_part and far_trailing in pts_for_curves:
                    far_trailing_mirror = far_trailing.copy()
                    if far_trailing_mirror[self.x] > 0:
                        far_trailing_mirror[self.x] = -far_trailing_mirror[self.x]
                    elif far_trailing_mirror[self.x] < 0:
                        far_trailing_mirror[self.x] = abs(far_trailing_mirror[self.x])
                    # self.lw.WriteFullline(f"Far leading mirror pt added: {far_trailing_mirror}")
                    pts_for_curves.append(far_trailing_mirror)

                if low_pt_trail_left not in pts_for_curves and low_pt_trail_left[self.y] > (far_trailing[self.y] + self.buffer_50):
                    # self.lw.WriteFullline(f"Low trail left pt added: {low_pt_trail_left}")
                    pts_for_curves.append(low_pt_trail_left)
                if low_pt_trail_right not in pts_for_curves and low_pt_trail_right[self.y] > (far_trailing[self.y] + self.buffer_50):
                    # self.lw.WriteFullline(f"Low trail right pt added: {low_pt_trail_right}")
                    pts_for_curves.append(low_pt_trail_right)
            elif len(all_pts_trailing) == 1:
                pts_for_curves.append(all_pts_trailing[self.x])
            
            if lowest_pt not in pts_for_curves:
                pts_for_curves.append(lowest_pt)
                if mirror_part:
                    lowest_pt_mirror = lowest_pt.copy()
                    if lowest_pt_mirror[self.x] > 0:
                        lowest_pt_mirror[self.x] = -lowest_pt_mirror[self.x]
                    elif lowest_pt_mirror[self.x] < 0:
                        lowest_pt_mirror[self.x] = abs(lowest_pt_mirror[self.x])
                    # self.lw.WriteFullline(f"Far leading mirror added: {lowest_pt_mirror}")
                    pts_for_curves.append(lowest_pt_mirror)
        else:
            # Rivian Evaluation
            far_left = max(all_panel_pts, key=lambda coord: coord[self.y])
            far_right = min(all_panel_pts, key=lambda coord: coord[self.y])
            far_leading = max(all_panel_pts, key=lambda coord: coord[self.x])
            far_trailing = min(all_panel_pts, key=lambda coord: coord[self.x])

            all_pts_left = [coord for coord in all_panel_pts if round(coord[self.y], 2) > (far_left[self.y] - self.buffer_75)]
            all_pts_right = [coord for coord in all_panel_pts if round(coord[self.y], 2) < (far_right[self.y] + self.buffer_75)]
            all_pts_leading = [coord for coord in all_panel_pts if round(coord[self.x], 2) > (far_leading[self.x] - self.buffer_75)]
            all_pts_trailing = [coord for coord in all_panel_pts if round(coord[self.x], 2) < (far_trailing[self.x] + self.buffer_75)]

            if len(all_pts_left) > 1:
                pt_left_1 = min(all_pts_left, key=lambda coord: coord[self.x])
                pt_left_2 = max(all_pts_left, key=lambda coord: coord[self.x])
                sep = pt_left_2[self.x] - pt_left_1[self.x]
                # lw.WriteFullline(f"{sep}")

                # Step 1
                if sep < 200:
                    lead_buffer_list = [coord for coord in all_pts_left if coord[self.x] > (pt_left_2[self.x] - 30)]
                else:
                    lead_buffer_list = [coord for coord in all_pts_left if coord[self.x] > (pt_left_2[self.x] - self.buffer_inside_105)]
                lead_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] < (pt_left_2[self.x] + self.buffer_outside_1000)) and (coord[self.x] > pt_left_2[self.x])) and coord[self.y] > (pt_left_2[self.y] - self.buffer_75)]
                lead_buffer_list_final = lead_buffer_list + lead_buffer_list_2

                if sep < 200:
                    trail_buffer_list = [coord for coord in all_pts_left if coord[self.x] < (pt_left_1[self.x] + 30)]
                else:
                    trail_buffer_list = [coord for coord in all_pts_left if coord[self.x] < (pt_left_1[self.x] + self.buffer_inside_105)]
                trail_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] > (pt_left_1[self.x] - self.buffer_outside_1000)) and (coord[self.x] < pt_left_1[self.x])) and coord[self.y] > (pt_left_1[self.y] - self.buffer_75)]
                trail_buffer_list_final = trail_buffer_list + trail_buffer_list_2

                # for pt in lead_buffer_list_final:
                #     newPt:Point = workPart.Points.CreatePoint(Point3d(pt[self.x], pt[self.y], pt[self.z]))
                #     newPt.SetVisibility(SmartObject.VisibilityOption.Visible)

                # Step 2-3
                low_pt_left_lead = pt_left_2
                low_pt_left_lead_test = min(lead_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_left_lead_test[self.z] < (pt_left_2[self.z] - 7):
                    low_pt_left_lead = low_pt_left_lead_test

                low_pt_left_trail = pt_left_1
                low_pt_left_trail_test = min(trail_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_left_trail_test[self.z] < (pt_left_1[self.z] - 7):
                    low_pt_left_trail = low_pt_left_trail_test
                
                # Step 4-7
                if low_pt_left_lead == low_pt_left_trail or low_pt_left_trail[self.x] > (low_pt_left_lead[self.x] - 50):
                    trail_buffer_list_final_modified = [coord for coord in all_panel_pts if ((coord[self.x] > (pt_left_1[self.x] - self.buffer_outside_1000)) and (coord[self.x] < (pt_left_1[self.x] - 200))) and coord[self.y] > (pt_left_1[self.y] - self.secondary_buffer_150)]

                    if len(trail_buffer_list_final_modified) > 0:
                        low_pt_left_trail = min(trail_buffer_list_final_modified, key=lambda coord: coord[self.z])
                    else:
                        low_pt_left_trail = low_pt_left_lead

                # Step 8
                if (low_pt_left_lead[self.y] < (far_left[self.y] - self.buffer_50) or low_pt_left_trail[self.y] < (far_left[self.y] - self.buffer_50)) and far_left not in pts_for_curves:
                    if low_pt_left_lead[self.z] > (far_left[self.z] - 10) or low_pt_left_trail[self.z] > (far_left[self.z] - 10):
                        # self.lw.WriteFullline(f"Far left pt added: {far_left}")
                        pts_for_curves.append(far_left)

                if low_pt_left_lead not in pts_for_curves:
                    # self.lw.WriteFullline(f"Low left lead pt added: {low_pt_left_lead}")
                    pts_for_curves.append(low_pt_left_lead)
                if low_pt_left_trail not in pts_for_curves:
                    # self.lw.WriteFullline(f"Low left trail pt added: {low_pt_left_trail}")
                    pts_for_curves.append(low_pt_left_trail)
            elif len(all_pts_left) == 1:
                pts_for_curves.append(all_pts_left[self.x])
                # self.lw.WriteFullline(f"Single evaluated left pt added: {all_pts_left[self.x]}")

            if len(all_pts_right) > 1:
                pt_right_1 = min(all_pts_right, key=lambda coord: coord[self.x])
                pt_right_2 = max(all_pts_right, key=lambda coord: coord[self.x])
                sep = pt_right_2[self.x] - pt_right_1[self.x]
                # lw.WriteFullline(f"{sep}")

                # Step 1
                if sep < 200:
                    lead_buffer_list = [coord for coord in all_pts_right if coord[self.x] > (pt_right_2[self.x] - 30)]
                else:
                    lead_buffer_list = [coord for coord in all_pts_right if coord[self.x] > (pt_right_2[self.x] - self.buffer_inside_105)]
                lead_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] < (pt_right_2[self.x] + self.buffer_outside_1000)) and (coord[self.x] > pt_right_2[self.x])) and coord[self.y] < (pt_right_2[self.y] + self.buffer_75)]
                lead_buffer_list_final = lead_buffer_list + lead_buffer_list_2

                if sep < 200:
                    trail_buffer_list = [coord for coord in all_pts_right if coord[self.x] < (pt_right_1[self.x] + 30)]
                else:
                    trail_buffer_list = [coord for coord in all_pts_right if coord[self.x] < (pt_right_1[self.x] + self.buffer_inside_105)]
                trail_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.x] > (pt_right_1[self.x] - self.buffer_outside_1000)) and (coord[self.x] < pt_right_1[self.x])) and coord[self.y] < (pt_right_1[self.y] + self.buffer_75)]
                trail_buffer_list_final = trail_buffer_list + trail_buffer_list_2

                # Step 2-3
                low_pt_right_lead = pt_right_2
                low_pt_right_lead_test = min(lead_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_right_lead_test[self.z] < (pt_right_2[self.z] - 7):
                    low_pt_right_lead = low_pt_right_lead_test

                low_pt_right_trail = pt_right_1
                low_pt_right_trail_test = min(trail_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_right_trail_test[self.z] < (pt_right_1[self.z] - 7):
                    low_pt_right_trail = low_pt_right_trail_test

                # for pt in trail_buffer_list_final:
                #     newPt:Point = workPart.Points.CreatePoint(Point3d(pt[self.x], pt[self.y], pt[self.z]))
                #     newPt.SetVisibility(SmartObject.VisibilityOption.Visible)

                # Step 4-7
                if low_pt_right_lead == low_pt_right_trail or low_pt_right_trail[self.x] > low_pt_right_lead[self.x] - 50:
                    trail_buffer_list_final_modified = [coord for coord in all_panel_pts if ((coord[self.x] > (pt_right_1[self.x] - self.buffer_outside_1000)) and (coord[self.x] < (pt_right_1[self.x] - 200))) and coord[self.y] < (pt_right_1[self.y] + self.secondary_buffer_150)]

                    if len(trail_buffer_list_final_modified) > 0:
                        low_pt_right_trail = min(trail_buffer_list_final_modified, key=lambda coord: coord[self.z])
                    else:
                        low_pt_right_trail = low_pt_right_lead

                # Step 8
                if (low_pt_right_lead[self.y] > (far_right[self.y] + self.buffer_50) or low_pt_right_trail[self.y] > (far_right[self.y] + self.buffer_50)) and far_right not in pts_for_curves:
                    if low_pt_right_lead[self.z] > (far_right[self.z] - 10) or low_pt_right_trail[self.z] > (far_right[self.z] - 10):
                        # self.lw.WriteFullline(f"Far right pt added: {far_right}")
                        pts_for_curves.append(far_right)

                if low_pt_right_lead not in pts_for_curves:
                    # self.lw.WriteFullline(f"Low right lead pt added: {low_pt_right_lead}")
                    pts_for_curves.append(low_pt_right_lead)
                if low_pt_right_trail not in pts_for_curves:
                    # self.lw.WriteFullline(f"Low right trail pt added: {low_pt_right_trail}")
                    pts_for_curves.append(low_pt_right_trail)
            elif len(all_pts_right) == 1:
                # self.lw.WriteFullline(f"Single evaluated right pt added: {all_pts_right[self.x]}")
                pts_for_curves.append(all_pts_right[self.x])

            if len(all_pts_leading) > 1:
                pt_leading_1 = max(all_pts_leading, key=lambda coord: coord[self.y])
                pt_leading_2 = min(all_pts_leading, key=lambda coord: coord[self.y])
                sep = pt_leading_1[self.y] - pt_leading_2[self.y]
                # lw.WriteFullline(f"{sep}")

                # Step 1
                if sep < 200:
                    left_buffer_list = [coord for coord in all_pts_leading if coord[self.y] > (pt_leading_1[self.y] - 30)]
                else:
                    left_buffer_list = [coord for coord in all_pts_leading if coord[self.y] > (pt_leading_1[self.y] - self.buffer_inside_105)]
                left_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] < (pt_leading_1[self.y] + self.buffer_outside_1000)) and (coord[self.y] > pt_leading_1[self.y])) and coord[self.x] > (pt_leading_1[self.x] - self.buffer_75)]
                left_buffer_list_final = left_buffer_list + left_buffer_list_2

                if sep < 200:
                    right_buffer_list = [coord for coord in all_pts_leading if coord[self.y] < (pt_leading_2[self.y] + 30)]
                else:
                    right_buffer_list = [coord for coord in all_pts_leading if coord[self.y] < (pt_leading_2[self.y] + self.buffer_inside_105)]
                right_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] > (pt_leading_2[self.y] - self.buffer_outside_1000)) and (coord[self.y] < pt_leading_2[self.y])) and coord[self.x] > (pt_leading_2[self.x] - self.buffer_75)]
                right_buffer_list_final = right_buffer_list + right_buffer_list_2

                # Creating pts
                # for pt in all_pts_leading:
                #     newPt:Point = workPart.Points.CreatePoint(Point3d(pt[self.x], pt[self.y], pt[self.z]))
                #     newPt.SetVisibility(SmartObject.VisibilityOption.Visible)

                # Step 2-3
                low_pt_lead_left = pt_leading_1
                low_pt_lead_left_test = min(left_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_lead_left_test[self.z] < (pt_leading_1[self.z] - 7):
                    low_pt_lead_left = low_pt_lead_left_test

                low_pt_lead_right = pt_leading_2
                low_pt_lead_right_test = min(right_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_lead_right_test[self.z] < (pt_leading_2[self.z] - 7):
                    low_pt_lead_right = low_pt_lead_right_test

                # Step 8
                if (low_pt_lead_left[self.x] < (far_leading[self.x] - self.buffer_50) or low_pt_lead_right[self.x] < (far_leading[self.x] - self.buffer_50)) and (low_pt_left_lead[self.x] < (far_leading[self.x] - self.buffer_50) and low_pt_right_lead[self.x] < (far_leading[self.x] - self.buffer_50)) and far_leading not in pts_for_curves:
                    # if low_pt_lead_left[self.z] > (far_leading[self.z] - 10) or low_pt_lead_right[self.z] > (far_leading[self.z] - 10):
                    # self.lw.WriteFullline(f"Far leading pt added: {far_leading}")
                    pts_for_curves.append(far_leading)

                far_leading_mirror = []
                if (round(low_pt_lead_left[self.x], 1) == round(low_pt_lead_right[self.x], 1) and round(low_pt_lead_left[self.z], 1) == round(low_pt_lead_right[self.z], 1) and abs(round(low_pt_lead_left[self.y], 1)) == abs(round(low_pt_lead_right[self.y], 1))) and far_leading in pts_for_curves:
                    mirror_part = True
                    far_leading_mirror = far_leading.copy()
                    if far_leading_mirror[self.y] > 0:
                        far_leading_mirror[self.y] = -far_leading_mirror[self.y]
                    elif far_leading_mirror[self.y] < 0:
                        far_leading_mirror[self.y] = abs(far_leading_mirror[self.y])
                    # self.lw.WriteFullline(f"Far leading mirror pt added: {far_leading_mirror}")
                    pts_for_curves.append(far_leading_mirror)

                if low_pt_lead_left not in pts_for_curves and low_pt_lead_left[self.x] < (far_leading[self.x] - self.buffer_50):
                    # self.lw.WriteFullline(f"Low lead left pt added: {low_pt_lead_left}")
                    pts_for_curves.append(low_pt_lead_left)
                if low_pt_lead_right not in pts_for_curves and low_pt_lead_right[self.x] < (far_leading[self.x] - self.buffer_50):
                    # self.lw.WriteFullline(f"Low lead right pt added: {low_pt_lead_right}")
                    pts_for_curves.append(low_pt_lead_right)

                # Flange check
                all_pts_leading_flange_check = [coord for coord in all_panel_pts if round(coord[self.x], 2) == round(far_leading[self.x], 2) or round(coord[self.x], 2) > (far_leading[self.x] - self.flange_buffer_150)]
                min_flange_pt = min(all_pts_leading_flange_check, key=lambda coord: coord[self.z])
                if min_flange_pt[self.z] < low_pt_lead_left[self.z] and min_flange_pt[self.z] < low_pt_lead_right[self.z] and not blank:
                    dif = pt_leading_2[self.y] - pt_leading_1[self.y]
                    half_dif = dif / 2

                    left_buffer_list = [coord for coord in all_pts_leading_flange_check if coord[self.y] > (pt_leading_1[self.y] - half_dif)]
                    left_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] < (pt_leading_1[self.y] + self.buffer_outside_1000)) and (coord[self.y] > pt_leading_1[self.y])) and coord[self.x] > (pt_leading_1[self.x] - self.buffer_75)]
                    left_buffer_list_final = left_buffer_list + left_buffer_list_2

                    right_buffer_list = [coord for coord in all_pts_leading_flange_check if coord[self.y] < (pt_leading_2[self.y] + half_dif)]
                    right_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] > (pt_leading_2[self.y] - self.buffer_outside_1000)) and (coord[self.y] < pt_leading_2[self.y])) and coord[self.x] > (pt_leading_2[self.x] - self.buffer_75)]
                    right_buffer_list_final = right_buffer_list + right_buffer_list_2
                    
                    if len(left_buffer_list_final) > 0:
                        low_pt_lead_left_flange = min(left_buffer_list_final, key=lambda coord: coord[self.z])
                        if low_pt_lead_left_flange not in pts_for_curves:
                            # self.lw.WriteFullline(f"Low lead left flange pt added: {low_pt_lead_left_flange}")
                            pts_for_curves.append(low_pt_lead_left_flange)

                    if len(right_buffer_list_final) > 0:
                        low_pt_lead_right_flange = min(right_buffer_list_final, key=lambda coord: coord[self.z])
                        if low_pt_lead_right_flange not in pts_for_curves:
                            # self.lw.WriteFullline(f"Low lead right flange pt added: {low_pt_lead_right_flange}")
                            pts_for_curves.append(low_pt_lead_right_flange)
            elif len(all_pts_leading) == 1:
                # self.lw.WriteFullline(f"Single evaluated lead pt added: {all_pts_leading[self.x]}")
                pts_for_curves.append(all_pts_leading[self.x])

            if len(all_pts_trailing) > 1:
                pt_trailing_1 = max(all_pts_trailing, key=lambda coord: coord[self.y])
                pt_trailing_2 = min(all_pts_trailing, key=lambda coord: coord[self.y])
                sep = pt_trailing_1[self.y] - pt_trailing_2[self.y]
                # lw.WriteFullline(f"{sep}")

                # Step 1
                if sep < 200:
                    left_buffer_list = [coord for coord in all_pts_trailing if coord[self.y] > (pt_trailing_1[self.y] - 30)]
                else:
                    left_buffer_list = [coord for coord in all_pts_trailing if coord[self.y] > (pt_trailing_1[self.y] - self.buffer_inside_105)]
                left_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] < (pt_trailing_1[self.y] + self.buffer_outside_1000)) and (coord[self.y] > pt_trailing_1[self.y])) and coord[self.x] < (pt_trailing_1[self.x] + self.buffer_75)]
                left_buffer_list_final = left_buffer_list + left_buffer_list_2

                if sep < 200:
                    right_buffer_list = [coord for coord in all_pts_trailing if coord[self.y] < (pt_trailing_2[self.y] + 30)]
                else:
                    right_buffer_list = [coord for coord in all_pts_trailing if coord[self.y] < (pt_trailing_2[self.y] + self.buffer_inside_105)]
                right_buffer_list_2 = [coord for coord in all_panel_pts if ((coord[self.y] > (pt_trailing_2[self.y] - self.buffer_outside_1000)) and (coord[self.y] < pt_trailing_2[self.y])) and coord[self.x] < (pt_trailing_2[self.x] + self.buffer_75)]
                right_buffer_list_final = right_buffer_list + right_buffer_list_2

                # for pt in all_pts_trailing:
                #     newPt:Point = workPart.Points.CreatePoint(Point3d(pt[self.x], pt[self.y], pt[self.z]))
                #     newPt.SetVisibility(SmartObject.VisibilityOption.Visible)

                # Step 2-3
                low_pt_trail_left = pt_trailing_1
                low_pt_trail_left_test = min(left_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_trail_left_test[self.z] < (pt_trailing_1[self.z] - 7):
                    low_pt_trail_left = low_pt_trail_left_test

                low_pt_trail_right = pt_trailing_2
                low_pt_trail_right_test = min(right_buffer_list_final, key=lambda coord: coord[self.z])
                if low_pt_trail_right_test[self.z] < (pt_trailing_2[self.z] - 7):
                    low_pt_trail_right = low_pt_trail_right_test

                # Step 8
                if (low_pt_trail_left[self.x] > (far_trailing[self.x] + self.buffer_50) or low_pt_trail_right[self.x] > (far_trailing[self.x] + self.buffer_50)) and (low_pt_left_trail[self.x] > (far_trailing[self.x] + self.buffer_50) and low_pt_right_trail[self.x] > (far_trailing[self.x] + self.buffer_50)) and far_trailing not in pts_for_curves:
                    # if low_pt_trail_left[self.z] > (far_trailing[self.z] - 10) or low_pt_trail_right[self.z] > (far_trailing[self.z] - 10):
                    # self.lw.WriteFullline(f"Far trailing pt added: {far_trailing}")
                    pts_for_curves.append(far_trailing)

                far_trailing_mirror = []
                if mirror_part and far_trailing in pts_for_curves:
                    far_trailing_mirror = far_trailing.copy()
                    if far_trailing_mirror[self.y] > 0:
                        far_trailing_mirror[self.y] = -far_trailing_mirror[self.y]
                    elif far_trailing_mirror[self.y] < 0:
                        far_trailing_mirror[self.y] = abs(far_trailing_mirror[self.y])
                    # self.lw.WriteFullline(f"Far trailing mirror pt added: {far_trailing_mirror}")
                    pts_for_curves.append(far_trailing_mirror)

                if low_pt_trail_left not in pts_for_curves and low_pt_trail_left[self.x] > (far_trailing[self.x] + self.buffer_50):
                    # self.lw.WriteFullline(f"Low trail left pt added: {low_pt_trail_left}")
                    pts_for_curves.append(low_pt_trail_left)
                if low_pt_trail_right not in pts_for_curves and low_pt_trail_right[self.x] > (far_trailing[self.x] + self.buffer_50):
                    # self.lw.WriteFullline(f"Low trail right pt added: {low_pt_trail_right}")
                    pts_for_curves.append(low_pt_trail_right)
            elif len(all_pts_trailing) == 1:
                pts_for_curves.append(all_pts_trailing[self.x])

            if lowest_pt not in pts_for_curves:
                pts_for_curves.append(lowest_pt)
                if mirror_part:
                    lowest_pt_mirror = lowest_pt.copy()
                    if lowest_pt_mirror[self.y] > 0:
                        lowest_pt_mirror[self.y] = -lowest_pt_mirror[self.y]
                    elif lowest_pt_mirror[self.y] < 0:
                        lowest_pt_mirror[self.y] = abs(lowest_pt_mirror[self.y])
                    # self.lw.WriteFullline(f"Lowest mirror pt added: {lowest_pt_mirror}")
                    pts_for_curves.append(lowest_pt_mirror)

        self.lw.Close()
        # self.lw(len(pts_for_curves))
        return pts_for_curves
    
    def RunPanelCurves(self, add_curves=True):
        """
        Adds panel curves to selected panels or will return V180 pt info for curve generation.

        Args:
            add_curves (bool): If True, adds curves. Otherwise, just returns points.

        Returns:
            list (V180):
                - List[list[double, double, double]]: Each pt lives in a list, owned by a list containing all the points for a specific body, owned by a list contating a list for every selected body
                - None: This option is the default return. The list return is only for V180 curve generation
        """
        # Select panel curve to use
        if add_curves:
            selected_curve:Component = self.__SelectCurve("Select Panel Curve")[1]
            curve_proto = selected_curve.Prototype
            self.curve_full_path = curve_proto.FullPath
            self.curve_name = selected_curve.Name
            self.curve_ref_set = selected_curve.ReferenceSet

        # Select panels to place curves on
        pts:list = None
        all_panels_pts:list = []
        selected_bodies:list[Body] = self.__SelectPanelBody("Select Panels")
        panel_body_dict = {}
        for bdy in selected_bodies:
            body_owner = bdy.OwningComponent
            if body_owner not in panel_body_dict.keys():
                panel_body_dict[body_owner] = [bdy]
            else:
                panel_body_dict[body_owner].append(bdy)

        for i, bodies in enumerate(panel_body_dict.values()):
            pts = self.__GetPoints(bodies)
            if add_curves:
                markId1 = self.theSession.SetUndoMark(Session.MarkVisibility.Visible, "Add Curves To Panel")
                self.__AddCurves(pts)
            else:
                if i == len(selected_bodies) - 1:
                    all_panels_pts.append(pts)
                    return all_panels_pts
                else:
                    all_panels_pts.append(pts)
        return None
    
class NXDialogManager():
    """
    Methods:
        NXSelectComponent
        NXSelectComponents
        NXSelectPanels
        NXAsk
        NXAsk3Options
        NXInfoMsg
        NXWarningMsg
        NXErrorMsg
        NXAskStringInput
        NXCustomOpenFileDialog
    """
    def __init__(self, theSession):
        # Session/NX variables
        self.theSession:Session = theSession
        self.theUFSession:UFSession = UFSession.GetUFSession()
        self.theUFUi = NXOpen.UF.Ui()
        self.theUI:UI = UI.GetUI()
        
        self.selManager:Selection = self.theUI.SelectionManager
        self.lw:ListingWindow = self.theSession.ListingWindow

        # Response dictionary mappings
        self.select_comp_response_members = {
            1: "Back",
            2: "Cancel",
            3: "Ok",
            4: "Object Selected By Name",
            5: "Object Selected"
        }
        self.string_input_response_members = {
            1: "Back",
            2: "Cancel",
            3: "Ok",
            5: "Data Entered",
            8: "Disallowed State (call <NXOpen.UF.Ui.LockUgAccess(1)> before creating dialog)"
        }
        self.file_dialog_response_members = {
            2: "Ok",
            3: "Cancel"
        }

    def NXSelectComponent(self, title:str) -> Selection.Response:
        """
        Creates a selection dialog that allows the user to select a single component in an assmebly.

        Args:
            title (str): Message to be displayed within the select component dialog box

        Returns:
            Selection.Response (Tuple):
                - NXOpen.SelectionResponseMemberType: The selection response type
                - NXOpen.Assemblies.Component: The selected component
                - NXOpen.Point3d: Location of object (Not always accurate)
        """
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly
        mask_component:Selection.MaskTriple = Selection.MaskTriple()
        mask_component.Type = UFConstants.UF_component_type
        mask_component.Subtype = UFConstants.UF_component_subtype
        maskArray = [mask_component]
        resp:Selection.Response = self.selManager.SelectTaggedObject("Select Component", title, scope, selAction, includeFeatures, keepHighlighted, maskArray)
        resp_value = resp[0].value
        resp_name = self.select_comp_response_members.get(resp_value, "Unknown")
        resp_final = (resp_name, resp[1], resp[2])
        return resp_final

    def NXSelectComponents(self, title:str) -> Selection.Response:
        """
        Creates a selection dialog that allows the user to select multiple components in an assmebly.

        Args:
            title (str): Message to be displayed within the select component dialog box

        Returns:
            Selection.Response (Tuple):
                - NXOpen.SelectionResponseMemberType: The selection response type
                - list[NXOpen.Assemblies.Component]: List of selected components
        """
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly
        mask_component:Selection.MaskTriple = Selection.MaskTriple()
        mask_component.Type = UFConstants.UF_component_type
        mask_component.Subtype = UFConstants.UF_component_subtype
        maskArray = [mask_component]
        resp:Selection.Response = self.selManager.SelectTaggedObjects("Select Component", title, scope, selAction, includeFeatures, keepHighlighted, maskArray)
        resp_value = resp[0].value
        resp_name = self.select_comp_response_members.get(resp_value, "Unknown")
        resp_final = (resp_name, resp[1])
        return resp_final
    
    def NXSelectPanels(self) -> Selection.Response:
        """
        Creates a selection dialog that allows the user to select multiple solid/sheet bodies in an assmebly.

        Returns:
            Selection.Response (Tuple):
                - NXOpen.SelectionResponseMemberType: The selection response type
                - list[NXOpen.Body]: List of selected bodies
        """
        prompt:str = "Select Panels"
        title:str = "Select Panels"
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly
        resp:Selection.Response

        selMask:Selection.MaskTriple = Selection.MaskTriple()
        selMask.Type = UFConstants.UF_solid_type
        selMask.Subtype = UFConstants.UF_solid_body_subtype
        selMask.SolidBodySubtype = UFConstants.UF_UI_SEL_FEATURE_SHEET_BODY

        selMask2:Selection.MaskTriple = Selection.MaskTriple()
        selMask2.Type = UFConstants.UF_solid_type
        selMask2.Subtype = UFConstants.UF_solid_body_subtype

        selMaskArray:list[Selection.SelectionMaskTriple] = [selMask, selMask2]

        resp = self.selManager.SelectTaggedObjects(prompt, title, scope, selAction, includeFeatures, keepHighlighted, selMaskArray)
        resp_value = resp[0].value
        resp_name = self.select_comp_response_members.get(resp_value, "Unknown")
        resp_final = (resp_name, resp[1])
        return resp_final
    
    def NXSelectFace(self) -> Selection.Response:
        """
        Creates a selection dialog that allows the user to select a single face in an assmebly.

        Returns:
            Selection.Response (Tuple):
                - NXOpen.SelectionResponseMemberType: The selection response type
                - NXOpen.Face: The selected component
                - NXOpen.Point3d: Location of object (Not always accurate)
        """
        title:str = "Select Face"
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly
        resp:Selection.Response

        selMask:Selection.MaskTriple = Selection.MaskTriple()
        selMask.Type = UFConstants.UF_face_type
        # selMask.Subtype = UFConstants.UF_solid_face_subtype
        maskArray = [selMask]
        resp:Selection.Response = self.selManager.SelectTaggedObject("Select Face", title, scope, selAction, includeFeatures, keepHighlighted, maskArray)
        resp_value = resp[0].value
        resp_name = self.select_comp_response_members.get(resp_value, "Unknown")
        resp_final = (resp_name, resp[1], resp[2])
        return resp_final
    
    def NXSelectView(self)  -> Selection.Response:
        """
        Creates a selection dialog that allows the user to select a single drafting view.

        Returns:
            Selection.Response (Tuple):
                - NXOpen.SelectionResponseMemberType: The selection response type
                - NXOpen.Assemblies.Component: The selected component
                - NXOpen.Point3d: Location of object (Not always accurate)
        """
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly
        mask_component:Selection.MaskTriple = Selection.MaskTriple()
        mask_component.Type = UFConstants.UF_view_type
        mask_component.Subtype = UFConstants.UF_view_imported_subtype
        maskArray = [mask_component]
        resp:Selection.Response = self.selManager.SelectTaggedObject("Select View", "Select View", scope, selAction, includeFeatures, keepHighlighted, maskArray)
        resp_value = resp[0].value
        resp_name = self.select_comp_response_members.get(resp_value, "Unknown")
        resp_final = (resp_name, resp[1], resp[2])
        return resp_final

    def NXSelectBalloons(self) -> Selection.Response:
        """
        Creates a selection dialog that allows the user to select multiple balloons in an drafting view.

        Returns:
            Selection.Response (Tuple):
                - NXOpen.SelectionResponseMemberType: The selection response type
                - list[NXOpen.Annotations.IdSymbol]: List of selected components
        """
        includeFeatures:bool = False
        keepHighlighted:bool = False
        selAction:Selection.SelectionAction = Selection.SelectionAction.ClearAndEnableSpecific
        scope:Selection.SelectionScope = Selection.SelectionScope.AnyInAssembly
        mask_component:Selection.MaskTriple = Selection.MaskTriple()
        mask_component.Type = UFConstants.UF_drafting_entity_type
        mask_component.Subtype = UFConstants.UF_draft_id_symbol_subtype
        maskArray = [mask_component]
        resp:Selection.Response = self.selManager.SelectTaggedObjects("Select Balloons", "Select Balloons", scope, selAction, includeFeatures, keepHighlighted, maskArray)
        resp_value = resp[0].value
        resp_name = self.select_comp_response_members.get(resp_value, "Unknown")
        resp_final = (resp_name, resp[1])
        return resp_final

    def NXAsk(self, title:str, question:str, default_option="Yes", secondary_option="No") -> int:
        """
        Creates a message dialog that allows the user to pick one of two options.

        Args:
            title (str): Title of the dialog box
            question (str): Question to be displayed within the message dialog box
            default_option (str: Yes): Text for selectable option (LH side)
            secondary_option (str: No): Text for selectable option (RH side)

        Returns:
            int:
                - 1: The default option response
                - 2: The secondary option response
        """
        message_buttons = self.theUFUi.MessageButtons()
        message_buttons.Button1 = True
        message_buttons.Button2 = False
        message_buttons.Button3 = True
        message_buttons.Label1 = default_option
        message_buttons.Label2 = None
        message_buttons.Label3 = secondary_option
        message_buttons.Response1 = 1
        message_buttons.Response2 = 0
        message_buttons.Response3 = 2

        message_type = self.theUFUi.MessageDialogType.MESSAGE_QUESTION
        message:list[str] = [question]
        num_msgs:int = 1
        translate:bool = True

        resp = self.theUFUi.MessageDialog(title, message_type, message, num_msgs, translate, message_buttons)
        return resp

    def NXAsk3Options(self, title:str, question:str, default_option="Yes", secondary_option="No", third_option="Cancel") -> int:
        """
        Creates a message dialog that allows the user to pick one of three options.

        Args:
            title (str): Title of the dialog box
            question (str): Question to be displayed within the message dialog box
            default_option (str: Yes): Text for selectable option (LH side)
            secondary_option (str: No): Text for selectable option (RH side)
            third_option (str: Cancel): Text for selectable option (Center)

        Returns:
            int:
                - 1: The default option response
                - 2: The secondary option response
                - 3: The third option response
        """
        message_buttons = self.theUFUi.MessageButtons()
        message_buttons.Button1 = True
        message_buttons.Button2 = True
        message_buttons.Button3 = True
        message_buttons.Label1 = default_option
        message_buttons.Label2 = third_option
        message_buttons.Label3 = secondary_option
        message_buttons.Response1 = 1
        message_buttons.Response2 = 3
        message_buttons.Response3 = 2

        message_type = self.theUFUi.MessageDialogType.MESSAGE_QUESTION
        message:list[str] = [question]
        num_msgs:int = 1
        translate:bool = True

        resp = self.theUFUi.MessageDialog(title, message_type, message, num_msgs, translate, message_buttons)
        return resp
    
    def NXInfoMsg(self, msg:str) -> None:
        """
        Creates a message dialog that displays information to the user.

        Args:
            msg (str): Msg to be displayed within the message dialog box

        Returns:
            None
        """
        message_buttons = self.theUFUi.MessageButtons()
        message_buttons.Button1 = False
        message_buttons.Button2 = True
        message_buttons.Button3 = False
        message_buttons.Label1 = None
        message_buttons.Label2 = "OK"
        message_buttons.Label3 = None
        message_buttons.Response1 = 0
        message_buttons.Response2 = 0
        message_buttons.Response3 = 0

        title = "Info"
        message_type = self.theUFUi.MessageDialogType.MESSAGE_INFORMATION
        message:list[str] = [msg]
        num_msgs:int = 1
        translate:bool = True

        self.theUFUi.MessageDialog(title, message_type, message, num_msgs, translate, message_buttons)

    def NXWarningMsg(self, msg:str) -> None:
        """
        Creates a message dialog that displays a warning to the user.

        Args:
            msg (str): Msg to be displayed within the message dialog box

        Returns:
            None
        """
        message_buttons = self.theUFUi.MessageButtons()
        message_buttons.Button1 = False
        message_buttons.Button2 = True
        message_buttons.Button3 = False
        message_buttons.Label1 = None
        message_buttons.Label2 = "OK"
        message_buttons.Label3 = None
        message_buttons.Response1 = 0
        message_buttons.Response2 = 0
        message_buttons.Response3 = 0

        title = "Warning"
        message_type = self.theUFUi.MessageDialogType.MESSAGE_WARNING
        message:list[str] = [msg]
        num_msgs:int = 1
        translate:bool = True

        self.theUFUi.MessageDialog(title, message_type, message, num_msgs, translate, message_buttons)

    def NXErrorMsg(self, msg:str) -> None:
        """
        Creates a message dialog that displays an error to the user.

        Args:
            msg (str): Msg to be displayed within the message dialog box

        Returns:
            None
        """
        message_buttons = self.theUFUi.MessageButtons()
        message_buttons.Button1 = False
        message_buttons.Button2 = True
        message_buttons.Button3 = False
        message_buttons.Label1 = None
        message_buttons.Label2 = "OK"
        message_buttons.Label3 = None
        message_buttons.Response1 = 0
        message_buttons.Response2 = 0
        message_buttons.Response3 = 0

        title = "ERROR"
        message_type = self.theUFUi.MessageDialogType.MESSAGE_ERROR
        message:list[str] = [msg]
        num_msgs:int = 1
        translate:bool = True

        self.theUFUi.MessageDialog(title, message_type, message, num_msgs, translate, message_buttons)

    def NXAskStringInput(self, title:str, prompt:str) -> tuple:
        """
        Creates a text input dialog that allows the user to input a text string.

        Args:
            title (str): Message to be displayed within the select component dialog box
            prompt (str): Placeholder text in the input box
            
        Returns:
            Tuple:
                - str: The text input into the dialog box
                - int: The length of the returned string from the dialog box
                - str: Response type. This is the enum name of the original return int
        """
        self.theUFUi.LockUgAccess(1)
        str_input_result = self.theUFUi.AskStringInput(title, prompt)
        self.theUFUi.UnlockUgAccess(1)
        response_value = str_input_result[2]
        response_type = self.string_input_response_members.get(response_value, "Unknown")
        str_input_result_final = (str_input_result[0], str_input_result[1], response_type)
        return str_input_result_final

    def NXCustomOpenFileDialog(self, title:str="Select a .prt File", prompt:str="Select a file", file_extensions:list[str]=['*.prt'], default_name:str="") -> tuple:
        """
        Creates a customizable OpenFileDialog window.

        Args:
            title (str): Message displayed at top of dialog box
            prompt (str): Message to be displayed in bottom prompt bar of NX
            file_extensions (list[str]): Selectable filters within the dialog box. Follow format of default '*.prt' filter to add more
            default_name (str): Default name to appear in the dialog box

        Returns:
            Tuple:
                - str: Full path of the selected file, including file extension
                - str: Response type. This is the enum name of the original return int
        """
        file_extension_count = len(file_extensions)
        file_box:tuple = self.theUFUi.CreateFileboxWithMultipleFilters(prompt, title, file_extensions, file_extension_count, default_name)
        response_value = file_box[1]
        response_name = self.file_dialog_response_members.get(response_value, "Unknown")
        file_box_final = (file_box[0], response_name)
        return file_box_final



