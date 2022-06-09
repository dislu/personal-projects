from typing import List, Tuple
import shutil
import fitz  # install with 'pip install pymupdf'
import cv2
import pytesseract
from colorthief import ColorThief
import webcolors
import pandas as pd
import enchant
from os.path import isfile, join
from gensim.parsing.preprocessing import remove_stopwords
import numpy as np
colors = {'color1':(200, 245, 244),'color2':(249, 244, 167),'color3':(186, 167, 242)}
d = enchant.Dict("en_US")
def extract_text(file_name):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    image = cv2.imread(file_name,cv2.IMREAD_GRAYSCALE)
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    result = 255 - thresh
    data = pytesseract.image_to_string(result, lang='eng',config='--psm 10 ')
    return data

def make_text(words):
    line_dict = {} 
    words.sort(key=lambda w: w[0])
    for w in words:  
        y1 = round(w[3], 1)  
        word = w[4] 
        line = line_dict.get(y1, [])  
        line.append(word)  
        line_dict[y1] = line  
    lines = list(line_dict.items())
    lines.sort()  

    return "n".join([" ".join(line[1]+['/']) for line in lines])
def textract(file_name):
    custom_config = r'-c preserve_interword_spaces=1 --oem 1 --psm 1 -l eng+ita'
    d = pytesseract.image_to_data(Image.open(file_name), config=custom_config, output_type=Output.DICT)
    df = pd.DataFrame(d)

    # clean up blanks
    df1 = df[(df.conf!='-1')&(df.text!=' ')&(df.text!='')]
    # sort blocks vertically
    sorted_blocks = df1.groupby('block_num').first().sort_values('top').index.tolist()
    for block in sorted_blocks:
        curr = df1[df1['block_num']==block]
        sel = curr[curr.text.str.len()>3]
        char_w = (sel.width/sel.text.str.len()).mean()
        prev_par, prev_line, prev_left = 0, 0, 0
        text = ''
        for ix, ln in curr.iterrows():
            # add new line when necessary
            if prev_par != ln['par_num']:
                text += '\n'
                prev_par = ln['par_num']
                prev_line = ln['line_num']
                prev_left = 0
            elif prev_line != ln['line_num']:
                text += '\n'
                prev_line = ln['line_num']
                prev_left = 0

            added = 0  # num of spaces that should be added
            if ln['left']/char_w > prev_left + 1:
                added = int((ln['left'])/char_w) - prev_left
                text += ' ' * added 
            text += ln['text'] + ' '
            prev_left += len(ln['text']) + added + 1
        text += '\n'
        return text
def Form_List(Doc):
    form_list = []
    prev_form = ''
    count = 1
    prev_count = 1
    for page in range(len(Doc)):
        form = ''
        words = Doc[page].get_text('words')
        line_list = make_text(words).split('/n')
        #print(line_list)
        for item in line_list:
            #print(item[0:4])
            if item[0:4]=='Form':
            #print('prev_form',prev_form)
               if prev_form == '':
                  prev_form = item
                  print(prev_form)
                  print('inside empty')
               elif:
                  item == prev_form:
                  count = count+1
                  print('inside count')
               else:
                  prev_form = item
                  count = count + 1
                  form_list.append((prev_count,count))
                  prev_count = count
                  print(prev_count,count)
    return form_list                       
def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name
dominant_color = color_thief.get_color(quality=1)
palette = color_thief.get_palette(color_count=6)
requested_colour = (119, 172, 152)
actual_name, closest_name = get_colour_name(requested_colour)

print "Actual colour name:", actual_name, ", closest colour name:", closest_name

def create_ROIs(file_name,path):
    image = cv2.imread(file_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.threshold(blur,0,255,cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    cnts = cv2.findContours(opening, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] #if len(cnts) == 2 else cnts[1]
    ROI_number = 0
    for c in cnts:
        area = cv2.contourArea(c)
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        x,y,w,h = cv2.boundingRect(approx)
        if len(approx) == 4 and (area > 1000) and (area < 80000):
           ROI = image[y:y+h, x:x+w]
           cv2.imwrite('ROI_{}.png'.format(ROI_number), ROI)

def create_folder_form(Work_Dir):
    files = os.listdir(Work_Dir)
    #files[0:3]
    count = 1
    for item in form_list:
        count_len = len(str(count))
        folder = Work_Dir+'\\form'+'0'*(2-count_len)+str(count)
        os.makedirs(folder)
        for i in files[item[0]-1:item[1]-1]:
            source = os.path.join(Work_Dir,i)
            dest = os.path.join(folder,i)
            shutil.copy(source,dest)
            count = count + 1
    folder = Work_Dir+'\\form'+str(count)
    os.makedirs(folder)
    source = os.path.join(Work_Dir,files[len(files)-1])
    dest = os.path.join(folder,files[len(files)-1])
    shutil.copy(source,dest)

def extract_text(file_name):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    image = cv2.imread(file_name,cv2.IMREAD_GRAYSCALE)
    thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    result = 255 - thresh
    data = pytesseract.image_to_string(result, lang='eng',config='--psm 10 ')
    return data

def X_split(element):
    Y = element.split('.')[0]
    return int(Y.split('_')[1])
def annotation(text):
    text = remove_stopwords(text)
    results = []
    word_list = text.split(' ')
    if len(word_list)==1:
       results.append(text) 
       if text.find('=')==-1: 
          return results,''
       else:
          return results,text 
    else:             
       for item in word_list:
           if item =='':
              continue 
           if d.check(item)==False:
              print(item) 
              results.append(item.strip()) 
         
               
       return results,text
def color_classification(Forms):
    count =1
    for item in Forms:
        if count==1:
           count=2
           continue 
        path1 = item+'\color1'
        path2 = item+'\color2'
        path3 = item+'\color3'
        os.makedirs(path1)
        os.makedirs(path2)
        os.makedirs(path3)
        for file in os.listdir(item):
            file_name = os.path.join(item,file)
            print(file_name)
            if file_name.split('.')[-1]=='png':
               color_thief = ColorThief(file_name)
               dominant_color = color_thief.get_color(quality=1)
               D_1 = sum(((np.array(colors['color1'])-np.array(dominant_color))*0.3)**2)
               D_2 = sum(((np.array(colors['color2'])-np.array(dominant_color))*0.59)**2)
               D_3 = sum(((np.array(colors['color3'])-np.array(dominant_color))*0.11)**2)
               if D_1<D_2:
                  if D_1<D_3:
                     shutil.copy(file_name,os.path.join(path1,file))   
                  else:
                      shutil.copy(file_name,os.path.join(path3,file))
               else:
                  if D_2<D_3:
                      shutil.copy(file_name,os.path.join(path2,file))
                  else:
                      shutil.copy(file_name,os.path.join(path3,file))

def create_CSV_table(Forms,df):
    for item in Forms:
        #print(item)
        path = [item + '/color1',item + '/color2',item + '/color3']
        for p in path:
            data = {'Domain': '', 'Domain_Label': '', 'Variable': '','Variable_Level_value':'','Annotation Types':''}
            text_list = []
            print(item)
            ROI_list = [f for f in os.listdir(p) if f.split('.')[-1]=='png']
            ROI_list.sort(key = X_split)
            try:
               black = ROI_list[-1]
            except:
               continue 
            print(black)   
            file_name = os.path.join(p,black)
            #text = extract_text(file_name)
            text = textract(file_name) 
            if text is None:
               text = extract_text(file_name)    
            if text.find('[') !=-1:
               continue 
            print(len(text.split('=')))
            print(text)
            try:
               domain = text.split('=')
               data['Domain'] =domain[0].strip()
               data['Domain_Label'] = domain[1].strip()
               text_list.append(text)
            except:
               continue 
            for file in ROI_list[:-1]:
                file_name = os.path.join(p,file)
                if file_name.split('.')[-1]=='png':
                   print(file_name)
                   text = textract(file_name)
                   if text is None:
                      text = extract_text(file_name) 
                   print(text)   
                   if text.find('[') !=-1:
                      continue  
                   if text not in text_list:
                      var_list,annot=annotation(text)
                   for i in var_list:
                       if i.find('=') == -1:
                          data['Variable']= i.strip()
                          data['Variable_Level_value']=''
                          data['Annotation Types']=annot.strip()
                       else:
                          print('p',i) 
                          ii = i.split('=') 
                          data['Variable']= ii[0].strip()
                          data['Variable_Level_value']=text.split('=')[1].strip()
                          data['Annotation Types']=annot.strip()
                       df = df.append(data, ignore_index = True)           
                       text_list.append(text)
    return df
def main(filepath: str) -> List:
    doc = fitz.open(filepath)
    form_list = form_list(Doc)
    Forms = form_list
    Work_Dir = os.getcwd()
    create_folder_form(Work_Dir)
    count =1
    for item in Forms:
        if count==1:
           count=2
           continue 
        print(item)
        for file in os.listdir(item):
            file_name = os.path.join(item,file)
            print(file_name)
            create_ROIs(file_name,item+'\\')
    
    #data = {'Domain': '', 'Domain_Label': '', 'Variable': '','Variable_Level_value':'','Annotation Types':''}
    #df = df.append(data, ignore_index = True)    
    columns = ['Domain','Domain_Label','Variable','Variable_Level_value','Annotation Types']
    df = pd.DataFrame(columns = columns) 
    table = create_CSV_table(Forms,df)
    table.to_csv('acrf_2002_26113.csv',index=False)
    return 


if __name__ == "__main__":
    print(main("acrf_2002_26113.pdf"))
