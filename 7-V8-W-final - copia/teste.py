from save_data import *

dic = {"1" : 2, "3" : 4}

dic_para = {}
with open("test.csv", "r", newline='') as file:
        reader = csv.reader(file)
        lines = list(reader)
        # Parse parameter dictionary from header (lines 0-30)
        for line in lines[4:31]:
            print(line)
            try :
                if ':' in line[0]:
                    parts = line[0].split(":", 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    dic_para[key] = value
            except:
                pass
print(dic_para)
#save_data_init("test", dic)
#save_data("test", [[1, 2, 3]])