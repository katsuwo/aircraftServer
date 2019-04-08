import xlrd

class ACCSectorReader:
    def __iadd__(self, other):
        pass
    def getAllSectors(self):
        wb = xlrd.open_workbook("ACCSector.xlsx")

        retlist = []
        for sheetname in wb.sheet_names():
            dict = {}
            sheet = wb.sheet_by_name(sheetname)
            all_points = ""
            for y in range(0, sheet.nrows):
                if str(sheet.cell(y, 0).value) == "":
                    break
                line = str(sheet.cell(y, 0).value).replace("*1", "").replace("*2", "").replace("*3", "").replace("*4", "").replace("*5", "")
                all_points = all_points + line
            points = all_points.split(",")

            coordinates = []
            for pt in points:
                pt2 = pt.replace("E", "").strip().replace("\t", "").replace(" ", "")
                tmpstr = pt2.split("N")
                lat_str = tmpstr[0]
                lng_str = tmpstr[1]
                lat = self.convert_degminsec_to_deg(lat_str[:2], lat_str[2:])
                lng = self.convert_degminsec_to_deg(lng_str[:3], lng_str[3:])
                coordinates.append(lat)
                coordinates.append(lng)
            dict[sheetname] = coordinates
            retlist.append(dict)
        return {"acc_sectors":retlist}

    def convert_degminsec_to_deg(self, deg_str, minsec_str):
        min = float(minsec_str[:2])
        sec = float(minsec_str[2:])
        deg = float(deg_str)
        deg = deg + (min / 60.0) + (sec / 3600.0)
        return deg
