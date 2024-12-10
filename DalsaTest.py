import os
from vstars import VSTARS
import time

# set this to the path to the original bmps
origBmps = R"C:\Dump\NoBackup\Projects\00 Genie 12M compression pics 22-05-18\test - bmps"


def savePic(frame, power, lights, shutter):
    V = VSTARS()
    for i in range(1, 4):
        V.FileSaveImageAs(filename=f"F{frame}-P{power}-T{shutter}-{lights}_sl{i}.gsi")
        V.FileSaveImageAs(filename=f"F{frame}-P{power}-T{shutter}-{lights}_arr_sl{i}.gsi")


def cleanScans():

    V = VSTARS()

    clouds = V.GetProjectCloudNames()

    for cloud in clouds:

        try:
            V.UnSelectPointsAll()
            V.SelectPointsByLabel(filename=cloud, labels="SCAN*")
            V.DeleteSelection()
        except:
            pass


def CompareFiles():

    V = VSTARS()

    clouds = V.GetProjectCloudNames()

    # the 3D files will have the same name as the image
    for cloud in clouds:

        # ignore empty clouds
        V.Get3D(filename=cloud)
        if len(V.cloud.points) == 0:
            continue

        # set the view
        V.XYZImportViewSettings(filename=cloud, source="ViewSettings")

        # if this is a child file
        if "__sl" in cloud:
            try:
                # find the parent file
                pos = cloud.rfind("__")
                parentFile = cloud[:pos]

                # import parent data to design of the child
                V.XYZImportToDesign(filename=cloud, design=parentFile, delete_existing=True)

                # set the view
                V.XYZImportViewSettings(filename=cloud, source="ViewSettings")

                # save the diffs
                V.XYZAlignmentResidualsQuick(filename=cloud, rejection=0.00000001, save=f"{cloud}.txt", ok=True, hideDialog=True)


            except:
                pass
            
            continue


def CompareFilesWithRename():

    V = VSTARS()

    clouds = V.GetProjectCloudNames()

    relabelFile = None

    # the 3D files will have the same name as the image
    for cloud in clouds:

        # if this is a child file
        if relabelFile and "_sl" in cloud:
            try:
                # relabel the child files
                V.XYZAutoRelabel(filename=cloud, desiredLabels=relabelFile, nearnessThreshold=0.1, doAlignment=True, onlyAutoMatched=False)

                # find the parent file
                pos = cloud.rfind("__")
                # pos = cloud.rfind("_", 0, cloud.rfind("_"))
                parentFile = cloud[:pos]

                # import parent data to design of the child
                V.XYZImportToDesign(filename=cloud, design=parentFile, delete_existing=True)

                # set the view
                V.XYZImportViewSettings(filename=cloud, source="ViewSettings")

                # save the diffs
                V.XYZAlignmentResidualsQuick(filename=cloud, save=f"{cloud}.txt", ok=True, hideDialog=True)

            except:
                pass
            
            continue

        # rename the scans in the parent files
        try:
            # the first non capon parent file is the relabel file
            if relabelFile is None and "capon" not in cloud:
                V.UnSelectPointsAll()
                V.SelectPointsByLabel(filename=cloud, labels="SCAN*")
                V.RelabelSelectedPoints(prefix="T")
                relabelFile = cloud
            else:
                # rename all other parents using the first
                V.XYZAutoRelabel(filename=cloud, desiredLabels=relabelFile, nearnessThreshold=0.1, doAlignment=True, onlyAutoMatched=False)

            # set the view
            V.XYZImportViewSettings(filename=cloud, source="ViewSettings")
        except:
            pass

# create the gsi files from the bmps using the new rle compression
# a special version of vstars will key off of the file name to determine
# which type of rle and sumlimit to use
#
# oldrc - will use the original RLE algorithm, otherwise the new one will be used
# sl## - will set the sumlimit
def MakeImages():

    V = VSTARS()

    V.CloseAllPictures()

    V.PicturesSetImagePath(path=origBmps)

    npics = V.GetNumberofPictures()

    for pic in range(1, npics+1):

        V.PicturesInformation(index=pic)

        imageName = os.path.splitext(V.getValue("v.imageName"))[0]

        # open the original image, usually a bmp from the camera
        V.PictureFromDisk(index=pic)

        # save that bmp using the rle compression
        for i in sumLimits:
            # V.FileSaveImageAs(index=pic, filename=f"{imageName}_oldrc_sl{i:02}.gsi")
            # time.sleep(0.25)
            V.FileSaveImageAs(index=pic, filename=f"{imageName}_sl{i:02}.gsi")
            time.sleep(0.25)

        # close the bmp
        V.CloseAllPictures()

    projPath = V.ProjectPath()
    V.PicturesSetImagePath(path=projPath)


# convert the images in the project to bmps in a bmps folder
# so they can be compared with the ImageCompare script
def MakeBitmaps():

    V = VSTARS()

    V.CloseAllPictures()

    npics = V.GetNumberofPictures()

    for pic in range(1, npics+1):

        V.PicturesInformation(index=pic)

        imageName = os.path.splitext(V.getValue("v.imageName"))[0]

        V.PictureFromDisk(index=pic)
        V.FileSaveImageAs(index=pic, filename=f"bmps-new\\{imageName}.bmp")
        time.sleep(0.25)

        V.CloseAllPictures()


def MakeImagesTimesX(times):

    V = VSTARS()

    V.CloseAllPictures()

    npics = V.GetNumberofPictures()

    for pic in range(1, npics+1):

        V.PicturesInformation(index=pic)
        imageName = os.path.splitext(V.getValue("v.imageName"))[0]

        V.PictureFromDisk(index=pic)

        for i in sumLimits:
            for j in range(0,times):
                V.FileSaveImageAs(index=pic, filename=f"{imageName}__sl{i:02}.gsi")
                time.sleep(0.25)

        V.CloseAllPictures()


def LoadImagesTimesX(times):

    V = VSTARS()

    V.CloseAllPictures()

    npics = V.GetNumberofPictures()

    for pic in range(1, npics+1):

        V.PicturesInformation(index=pic)
        imageName = V.getValue("v.imageName")

        if ".bmp" in imageName:
            continue

        for j in range(0,times):
            V.PictureFromDisk(index=pic)
            time.sleep(0.1)
            V.CloseAllPictures()
            time.sleep(0.1)



def MeasurePics():

    V = VSTARS()

    npics = V.GetNumberofPictures()

    for pic in range(1, npics+1):

        V.PictureFromDisk(index=pic)
        V.PictureSuperStart()
        V.CloseAllPictures()


# priorPath = R"C:\Dump\Projects\Genie 5G compression test pics 21-10-25\1 - bmp processing - GSI prior pixel"
# priorPath = R"C:\Dump\Projects\Genie 5G compression test pics 21-10-25\1 - bmp processing - 69H"
# priorPath = R"C:\Dump\Projects\Genie 5G compression test pics 21-10-25\1 - bmp - SM No Loss"
# priorPath = R"C:\Dump\Projects\Genie 5M compression pics 21-11-13\Test - SMNL1 - SM2 - SC0 - 16JDB"
#priorPath = R"C:\Dump\Projects\Genie 5M compression pics 21-11-13\Test - bmp"
#priorPath = R"C:\Dump\Projects\Genie 5M compression pics 21-11-13\Test - genie"

priorPath = R"C:\Dump\Projects\00 Genie 12M compression pics 22-05-18\test - 128old"

def ComparePrevious():

    V = VSTARS()

    clouds = V.GetProjectCloudNames()

    # the 3D files will have the same name as the image
    for cloud in clouds:

        # ignore empty clouds
        V.Get3D(filename=cloud)
        if len(V.cloud.points) == 0:
            continue

        # import the same cloud from the previous project to design of this cloud

        previousCloud = os.path.join(priorPath, cloud) + ".3D"

        #previousCloud = previousCloud.replace("__raw_sl01", "-genie")
        #previousCloud = previousCloud.replace("-genie", "")

        V.XYZImportToDesign(filename=cloud, design=previousCloud, delete_existing=True)

        # save the diffs
        V.XYZAlignmentResidualsQuick(filename=cloud, rejection=0.00000001, save=f"{cloud}.txt", ok=True, hideDialog=True)


sumLimits = { 1, 2, 3, 4, 5, 10 }

def main():

    V = VSTARS()
    V.init()

    #MakeBitmaps()

    # MakeImagesTimesX(25)
    # LoadImagesTimesX(25)

    MakeImages()
    #MeasurePics()
    MakeBitmaps()

    #V.Message(message="Convert pics to 3D files", modeless=True)
    # cleanScans()
    #ComparePrevious()
    # CompareFiles()


if __name__ == "__main__":
    main()
