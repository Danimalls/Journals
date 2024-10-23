import os
import NXOpen
import NXOpen.UF
import NXOpen.Assemblies

def main():
    theSession = NXOpen.Session.GetSession()
    workPart = theSession.Parts.Work
    displayPart = theSession.Parts.Display
    theUFSession = NXOpen.UF.UFSession.GetUFSession()
    lw = theSession.ListingWindow
    lw.Open()

    all_binder_assemblies = []
    def findParent(comp):
        parent_comp = comp.OwningComponent
        parent_comp_name = parent_comp.Name
        if "blankholder_asm" in parent_comp_name.lower():
            if parent_comp not in all_binder_assemblies:
                all_binder_assemblies.append(parent_comp)

        return parent_comp, parent_comp_name

    def AskAllBodies(thePart, op, die_ref):
        current_die_directory = os.path.dirname(theSession.Parts.Work.FullPath)
        NULLTAG = 0
        objectTag = 0
        the_bodies = []

        objectTag = theUFSession.Obj.CycleObjsInPart(thePart.Tag, NXOpen.UF.UFConstants.UF_solid_type, objectTag)

        while objectTag != NULLTAG:
            objType = 0
            objSubType = 0

            objType, objSubType = theUFSession.Obj.AskTypeAndSubtype(objectTag)
            if objSubType == NXOpen.UF.UFConstants.UF_solid_body_subtype:
                try:
                    nxBody = NXOpen.TaggedObjectManager.GetTaggedObject(objectTag)
                except:
                    continue
                name_tree = ""
                comp_tree = []
                owning_part = nxBody.OwningPart
                parent_part = nxBody.OwningComponent
                owning_part_name = owning_part.Name
                parent_part_name = parent_part.Name
                while parent_part_name != owning_part_name:
                    if len(parent_part_name) != 0:
                        name_tree = f"{name_tree} - {parent_part_name}"
                        comp_tree.append(parent_part)
                    try:
                        parent_part, parent_part_name = findParent(parent_part)
                    except:
                        parent_part_name = owning_part_name
                name_tree = f"{name_tree} - {owning_part_name}"
                comp_tree.append(owning_part)
                name_tree = name_tree[3:]
                if "pad_asm" in name_tree.lower():
                    find_pad = name_tree.split("- ")
                    for count, comp in enumerate(find_pad):
                        if "pad_asm" in comp.lower():
                            pad_asm_comp = comp_tree[count]
                            pad_location = pad_asm_comp.GetPosition()[0]
                            if pad_location.Z != 0:
                                the_bodies.append(nxBody)
                else:
                    if "blankholder" not in name_tree.lower():
                        the_bodies.append(nxBody)
            objectTag = theUFSession.Obj.CycleObjsInPart(thePart.Tag, NXOpen.UF.UFConstants.UF_solid_type, objectTag)

        the_binder_bodies = []
        if op == "OP20" and die_ref == "lower":
            if len(all_binder_assemblies) > 0 :
                binder_objectTag = 0

                binder_assembly_locations = {}
                for binder_assembly in all_binder_assemblies:
                    binder_assembly_locations[binder_assembly] = binder_assembly.GetPosition()[0].Z

                lowest_height_binder = min(binder_assembly_locations, key=lambda x: binder_assembly_locations[x])
                lw.WriteLine(f"Binder assembly zero position: {lowest_height_binder.GetPosition()[0]}")
                binder_to_export = lowest_height_binder.Prototype

                try:
                    theSession.Parts.OpenActiveDisplay(f"{current_die_directory}\\{binder_to_export.Name}.prt", NXOpen.DisplayPartOption.AllowAdditional)
                except:
                    theSession.Parts.SetActiveDisplay(binder_to_export, NXOpen.DisplayPartOption.AllowAdditional, NXOpen.PartDisplayPartWorkPartOption.SameAsDisplay)
                newDisplayPart = theSession.Parts.Display
                binder_objectTag = theUFSession.Obj.CycleObjsInPart(newDisplayPart.Tag, NXOpen.UF.UFConstants.UF_solid_type, binder_objectTag)

                while binder_objectTag != NULLTAG:
                    binder_objType = 0
                    binder_objSubType = 0

                    binder_objType, binder_objSubType = theUFSession.Obj.AskTypeAndSubtype(binder_objectTag)
                    if binder_objSubType == NXOpen.UF.UFConstants.UF_solid_body_subtype:
                        binder_nxBody = NXOpen.TaggedObjectManager.GetTaggedObject(binder_objectTag)
                        the_binder_bodies.append(binder_nxBody)

                    binder_objectTag = theUFSession.Obj.CycleObjsInPart(newDisplayPart.Tag, NXOpen.UF.UFConstants.UF_solid_type, binder_objectTag)

        return the_bodies, the_binder_bodies
    
    def export(location, the_bodies):
        options = NXOpen.UF.Part.ExportOptions()
        options.NewPart = True
        options.ParamsMode = NXOpen.UF.Part.ExportParamsMode.REMOVE_PARAMS
        options.ExpressionMode = NXOpen.UF.Part.ExportExpMode.COPY_EXP_SHALLOWLY

        if os.path.exists(location) or os.path.exists(location + ".prt"):
            pass
        else:
            theUFSession.Part.ExportWithOptions(f"{location}", len(the_bodies), the_bodies, options)

    die_asm_to_new_file_dict = {
        "OP20": {
            "lower": "OP20 LOWER DIE.prt",
            "upper": "OP20 UPPER DIE.prt"
        },
        "OP30": {
            "lower": "OP30 LOWER DIE.prt",
            "upper": "OP30 UPPER DIE.prt"
        },
        "OP40": {
            "lower": "OP40 LOWER DIE.prt",
            "upper": "OP40 UPPER DIE.prt"
        },
        "OP50": {
            "lower": "OP50 LOWER DIE.prt",
            "upper": "OP50 UPPER DIE.prt"
        },
        "OP60": {
            "lower": "OP60 LOWER DIE.prt",
            "upper": "OP60 UPPER DIE.prt"
        },
        "OP70": {
            "lower": "OP70 LOWER DIE.prt",
            "upper": "OP70 UPPER DIE.prt"
        }
    }

    job_directory = os.path.dirname(workPart.FullPath)
    sim_directory = f"{job_directory[:23]}\\Simulations\\"
    job_number = job_directory[19:23]
    die_data = f"{job_directory}\\Die Data\\"
    theSession.Parts.LoadOptions.UsePartialLoading = True
    theSession.Parts.LoadOptions.UseLightweightRepresentations = True

    die_folders = [folder for folder in os.listdir(die_data) if "OP" in folder and "study" not in folder.lower()]
    for die_folder in die_folders:
        op = die_folder[:4]
        files = []
        all_die_comps = os.listdir(f"{die_data}{die_folder}")
        lower = ""
        upper = ""
        for die_comp in all_die_comps:
            if "lower_die_asm" in die_comp.lower() or "lowe_die_asm" in die_comp.lower():
                lower = die_comp
            elif "upper_die_asm" in die_comp.lower():
                upper = die_comp
        lower_file = f"{die_data}{die_folder}\\{lower}"
        files.append(lower_file)
        upper_file = f"{die_data}{die_folder}\\{upper}"
        files.append(upper_file)

        for count, file in enumerate(files):
            if count == 0:
                die_ref = "lower"
            else:
                die_ref = "upper"
            try:
                theSession.Parts.OpenActiveDisplay(file, NXOpen.DisplayPartOption.AllowAdditional)
            except:
                theSession.Parts.SetActiveDisplay(file, NXOpen.DisplayPartOption.AllowAdditional, NXOpen.PartDisplayPartWorkPartOption.SameAsDisplay)
            
            newDisplayPart = theSession.Parts.Display
            newWorkPart = theSession.Parts.Work

            # Tries to load file from folder and as saved
            theSession.Parts.LoadOptions.ComponentLoadMethod = NXOpen.LoadOptions.LoadMethod.FromDirectory
            partLoadStatus1, openStatus1 = newWorkPart.ComponentAssembly.OpenComponents(NXOpen.Assemblies.ComponentAssembly.OpenOption.WholeAssembly, [newWorkPart.ComponentAssembly.RootComponent])
            partLoadStatus1.Dispose()

            theSession.Parts.LoadOptions.ComponentLoadMethod = NXOpen.LoadOptions.LoadMethod.AsSaved
            partLoadStatus2, openStatus2 = newWorkPart.ComponentAssembly.OpenComponents(NXOpen.Assemblies.ComponentAssembly.OpenOption.WholeAssembly, [newWorkPart.ComponentAssembly.RootComponent])
            partLoadStatus2.Dispose()

            assm_bodies, binder_bodies = AskAllBodies(newDisplayPart, op, die_ref)
            binder_comp = False
            if binder_bodies:
                binder_comp = True

            obj_tags = []
            for x in assm_bodies:
                obj_tags.append(x.Tag)
            binder_obj_tags = []
            if binder_comp:
                for x in binder_bodies:
                    binder_obj_tags.append(x.Tag)

            if binder_obj_tags:
                export(f"{sim_directory}AS-{job_number} OP20 LOWER BINDER", binder_obj_tags)
            export(f"{sim_directory}AS-{job_number} {die_asm_to_new_file_dict[op][die_ref]}", obj_tags)
            # theUFSession.Ui.DisplayMessage(f"{file} has been exported to {sim_directory}", 1)

            newWorkPart.Close(NXOpen.BasePart.CloseWholeTree.TrueValue, NXOpen.BasePart.CloseModified.CloseModified, None)

    theSession.Parts.LoadOptions.UseLightweightRepresentations = False
    lw.Close()

if __name__ == "__main__":
    main()

