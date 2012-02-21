import Image
import traceback
import os
import sys
import math

##-----------------------------------------------
##Flat3",  [(0, 180), (92, 180), (92, 272), (0, 272)]
##Flat3",  [(92, 180), (184, 180), (184, 272), (92, 272)]
##Flat3",  [(184, 180), (276, 180), (276, 272), (184, 272)]
##Flat3",  [(276, 180), (368, 180), (368, 272), (276, 272)]
##Flat3",  [(368, 180), (460, 180), (460, 272), (368, 272)]
##Flat3",  [(460, 180), (552, 180), (552, 272), (460, 272)]
##Flat3",  [(644, 180), (644, 180), (644, 272), (644, 272)]
##LeftH",  [(0, 160), (10, 162), (10, 288), (0, 290)]
##LeftI",  [(133, 162), (184, 180), (184, 272), (133, 288)]
##LeftJ",  [(256, 162), (276, 180), (276, 272), (256, 288)]
##RightJ",  [(368, 180), (379, 162), (379, 288), (368, 272)]
##RightK",  [(460, 180), (502, 162), (502, 288), (460, 272)]
##RightL",  [(552, 180), (502, 162), (502, 288), (552, 272)]
##Flat2",  [(-113, 162), (10, 162), (10, 288), (-113, 288)]
##Flat2",  [(10, 162), (133, 162), (133, 288), (10, 288)]
##Flat2",  [(133, 162), (256, 162), (256, 288), (133, 288)]
##Flat2",  [(256, 162), (379, 162), (379, 288), (256, 288)]
##Flat2",  [(379, 162), (502, 162), (502, 288), (379, 288)]
##Flat2",  [(502, 162), (625, 162), (625, 288), (502, 288)]
##Flat2",  [(625, 162), (748, 162), (748, 288), (625, 288)]
##LeftM",  [(10, 162), (92, 180), (92, 272), (10, 288)]
##LeftN",  [(44, 133), (133, 162), (133, 288), (44, 319)]
##LeftO",  [(228, 133), (256, 162), (256, 288), (228, 319)]
##RightO",  [(379, 162), (412, 133), (412, 319), (379, 288)]
##RightP",  [(502, 162), (596, 133), (596, 319), (502, 288)]
##RightQ",  [(650, 160), (625, 162), (625, 288), (650, 290)]
##Flat1",  [(-140, 133), (44, 133), (44, 319), (-140, 319)]
##Flat1",  [(44, 133), (228, 133), (228, 319), (44, 319)]
##Flat1",  [(228, 133), (412, 133), (412, 319), (228, 319)]
##Flat1",  [(412, 133), (596, 133), (596, 319), (412, 319)]
##Flat1",  [(596, 133), (780, 133), (780, 319), (596, 319)]
##LeftR",  [(0, 117), (44, 133), (44, 319), (0, 333)]
##LeftS",  [(138, 37), (228, 133), (228, 319), (138, 413)]
##RightS",  [(412, 133), (513, 37), (513, 413), (412, 319)]
##RightT",  [(596, 133), (650, 117), (650, 333), (596, 319)]
##Flat1",  [(-237, 37), (138, 37), (138, 413), (-237, 413)]
##Flat1",  [(138, 37), (513, 37), (513, 413), (138, 413)]
##Flat1",  [(513, 37), (888, 37), (888, 413), (513, 413)]
##LeftU",  [(0, -80), (138, 37), (138, 413), (0, 530)]
##RightU",  [(513, 37), (650, -80), (650, 530), (513, 413)]

######FilesAndCoordinates = [
######("Flat3",[(276, 180), (368, 180), (368, 272), (276, 272)]),
######("Flat2",[(256, 162), (379, 162), (379, 288), (256, 288)]),
######("Flat1",[(228, 133), (412, 133), (412, 319), (228, 319)]),
######("Flat0", [(138, 37), (513, 37), (513, 413), (138, 413)]),
########("LeftH", [(0, 160), (10, 162), (10, 288), (0, 290)]),
########("LeftI",  [(133, 162), (184, 180), (184, 272), (133, 288)]),
########("LeftJ",  [(256, 162), (276, 180), (276, 272), (256, 288)]),
######("RightJ",  [(368, 180), (379, 162), (379, 288), (368, 272)], "LeftJ"),
######("RightK",  [(460, 180), (502, 162), (502, 288), (460, 272)], "LeftI"),
######("RightL",  [(552, 180), (502, 162), (502, 288), (552, 272)], "LeftH"),
########("LeftM",  [(10, 162), (92, 180), (92, 272), (10, 288)]),
########("LeftN",  [(44, 133), (133, 162), (133, 288), (44, 319)]),
########("LeftO",  [(228, 133), (256, 162), (256, 288), (228, 319)]),
######("RightO",  [(379, 162), (412, 133), (412, 319), (379, 288)], "LeftO"),
######("RightP",  [(502, 162), (596, 133), (596, 319), (502, 288)], "LeftN"),
######("RightQ",  [(650, 160), (625, 162), (625, 288), (650, 290)], "LeftM"),
########("LeftR",  [(0, 117), (44, 133), (44, 319), (0, 333)]),
########("LeftS",  [(138, 37), (228, 133), (228, 319), (138, 413)]),
######("RightS",  [(412, 133), (513, 37), (513, 413), (412, 319)], "LeftS"),
######("RightT",  [(596, 133), (650, 117), (650, 333), (596, 319)], "LeftR"),
########("LeftU",  [(0, -80), (138, 37), (138, 413), (0, 530)]),
######("RightU",  [(513, 37), (650, -80), (650, 530), (513, 413)], "LeftU"),
######]

FilesAndCoordinates = [
##("Flat3", [(0, 179), (93, 179), (93, 272), (0, 272)]),
##("Flat3", [(93, 179), (186, 179), (186, 272), (93, 272)]),
##("Flat3", [(186, 179), (279, 179), (279, 272), (186, 272)]),
("Flat3", [(279, 179), (372, 179), (372, 272), (279, 272)]),
##("Flat3", [(372, 179), (465, 179), (465, 272), (372, 272)]),
##("Flat3", [(465, 179), (558, 179), (558, 272), (465, 272)]),
##("Flat3", [(651, 179), (651, 179), (651, 272), (651, 272)]),
##("LeftH", [(0, 160), (12, 162), (12, 287), (0, 290)]),
##("LeftI", [(137, 162), (186, 179), (186, 272), (137, 287)]),
##("LeftJ", [(262, 162), (279, 179), (279, 272), (262, 287)]),
("RightJ",[(372, 179), (387, 162), (387, 287), (372, 272)],"LeftJ"),
("RightK",[(465, 179), (512, 162), (512, 287), (465, 272)],"LeftI"),
("RightL",[(558, 179), (637, 162), (637, 287), (558, 272)],"LeftH"),
##("Flat2", [(-113, 162), (12, 162), (12, 287), (-113, 287)]),
##("Flat2", [(12, 162), (137, 162), (137, 287), (12, 287)]),
##("Flat2", [(137, 162), (262, 162), (262, 287), (137, 287)]),
("Flat2", [(262, 162), (387, 162), (387, 287), (262, 287)]),
##("Flat2", [(387, 162), (512, 162), (512, 287), (387, 287)]),
##("Flat2", [(512, 162), (637, 162), (637, 287), (512, 287)]),
##("Flat2", [(637, 162), (762, 162), (762, 287), (637, 287)]),
##("LeftM", [(12, 162), (93, 179), (93, 272), (12, 287)]),
##("LeftN", [(42, 131), (137, 162), (137, 287), (42, 318)]),
##("LeftO", [(230, 131), (262, 162), (262, 287), (230, 318)]),
("RightO",[(387, 162), (418, 131), (418, 318), (387, 287)],"LeftO"),
("RightP",[(512, 162), (606, 131), (606, 318), (512, 287)],"LeftN"),
("RightQ",[(650, 160), (637, 162), (637, 287), (650, 290)],"LeftM"),
##("Flat1", [(-146, 131), (42, 131), (42, 318), (-146, 318)]),
##("Flat1", [(42, 131), (230, 131), (230, 318), (42, 318)]),
("Flat1", [(230, 131), (418, 131), (418, 318), (230, 318)]),
##("Flat1", [(418, 131), (606, 131), (606, 318), (418, 318)]),
##("Flat1", [(606, 131), (794, 131), (794, 318), (606, 318)]),
##("LeftR", [(0, 117), (42, 131), (42, 318), (0, 333)]),
##("LeftS", [(137, 37), (230, 131), (230, 318), (137, 412)]),
("RightS",[(419, 131), (512, 37), (512, 412), (419, 318)],"LeftS"),
("RightT",[(606, 131), (650, 117), (650, 333), (606, 318)],"LeftR"),
##("Flat0", [(-238, 37), (137, 37), (137, 412), (-238, 412)]),
("Flat0", [(137, 37), (512, 37), (512, 412), (137, 412)]),
##("Flat0", [(512, 37), (887, 37), (887, 412), (512, 412)]),
##("LeftU", [(0, -98), (137, 37), (137, 412), (0, 548)]),
("RightU",[(512, 37), (650, -98), (650, 548), (512, 412)],"LeftU"),]

def GetWallPictures():
    for Tuple in FilesAndCoordinates:
        FileName = Tuple[0]
        OutputFileName = FileName+".png"
        try:
            TheImage = Image.open(os.path.join("work", FileName+".png"))
            print TheImage.format, TheImage.mode
            Points = Tuple[1]
            X1 = min(Points[0][0],Points[1][0],Points[2][0],Points[3][0])            
            X2 = max(Points[0][0],Points[1][0],Points[2][0],Points[3][0])
            Y1 = min(Points[0][1],Points[1][1],Points[2][1],Points[3][1])
            Y2 = max(Points[0][1],Points[1][1],Points[2][1],Points[3][1])
            Box = (X1, Y1, X2, Y2)
            SubImage = TheImage.crop(Box)
            SubImage.save(OutputFileName,"PNG")
            if len(Tuple)>2:
                SubImage = SubImage.transpose(Image.FLIP_LEFT_RIGHT)
                OutputFileName2 = Tuple[2]+".png"
                SubImage.save(OutputFileName2,"PNG")
            ##TheImage.show()
        except:
            traceback.print_exc()
            

GetWallPictures()            