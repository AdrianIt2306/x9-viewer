import codecs
import json
import logging
from PIL import Image
import io

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(levelname)s - %(lineno)d : %(message)s')

BATCH_FLAG = False
check_list = []
bundle_list = []
x9_structure = {}
file_header_record = {}
cash_letter_record = {}
credit_record = {}
bundle_record = {}  

#TODO Define a class to handle the X9 file
#TODO Check if the file is a X9 file
#TODO Load configuration from a file
with codecs.open('TEST.x9', 'rb') as input_file:
    line = input_file.read()
    #TODO Separator into constant    
    ctrl_ln = line.split(b'\x00\x00\x00P')
    #TODO Group the records from 25 until the next 25
    for index,line_num in enumerate(ctrl_ln):
        if (line_num[0:2] == b'\xf0\xf1'):
            #logging.debug(line_num.decode('cp500')[0:80])
            file_header_record = {'Record': line_num.decode('cp500')[0:80]}
        elif (line_num[0:2] == b'\xf1\xf0'):
            #logging.debug(line_num.decode('cp500')[0:80])
            cash_letter_record = {'Record': line_num.decode('cp500')[0:80]}
        elif (line_num[0:2] == b'\xf2\xf0'):
            #logging.debug(line_num.decode('cp500')[0:80])
            bundle_record['header'] = line_num.decode('cp500')[0:80]
            logging.debug(bundle_record)
        elif (line_num[0:2] == b'\xf6\xf1'):
            #logging.debug(line_num.decode('cp500')[0:80])
            bundle_record['credit'] = line_num.decode('cp500')[0:80]
        elif (line_num[0:2] == b'\xf2\xf5'):
            #logging.debug(line_num.decode('cp500')[0:80])
            check_list.append(line_num.decode('cp500')[0:80])
        elif (line_num[0:2] == b'\xf2\xf6'):
            #logging.debug(line_num.decode('cp500')[0:80])
            check_list.append(line_num.decode('cp500')[0:80])
        elif (line_num[0:2] == b'\xf7\xf0'):
            #logging.debug(len(check_list))
            bundle_record['check_list'] = check_list
            bundle_record['check_list_len'] = len(check_list)/2
            logging.debug(bundle_record)
            bundle_list.append(bundle_record)
            check_list = []
            bundle_record = {}               
        elif (line_num[0:2] == b'\xf5\xf0'):                                
            logging.info("Image content : {} - len {} - Index {}".format((line_num),len(line_num),index))    
            try:
                image_record = line_num[80:]
                logging.info(image_record[121:])
                logging.info(len(image_record[121:]))
                image = Image.open(io.BytesIO(image_record[121:]))
                image.save("img/output_{}.tiff".format(index))
                
            except Exception as e :
                #TODO Check if the image is broken and handle possible exceptions into the image
                logging.error("Record break by separator, trying 2nd way to recreate image {} {}".format(index,e))
                intento = image_record[121:] + b'\x00\x00\x00P' + ctrl_ln[index+1]
                image = Image.open(io.BytesIO(intento))
                image.save("img/output_ext{}.tiff".format(index))                
        else:
            #TODO Add the trailer record to the json
            logging.info("Trailers")
            logging.info("{} {}".format(line_num[0:2],index))

    #TODO Create a JSON object with the X9 structure with the records and the images location or base 64 image)
    
    x9_structure = {'x9-header':file_header_record, 'cash_letter':cash_letter_record,'bundles':bundle_list}
    json_object = json.dumps(x9_structure, indent = 10)
    logging.info(json_object)