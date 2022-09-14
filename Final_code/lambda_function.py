import boto3
from pprint import pprint
import re


def lambda_handler(event, context):
    s3 = boto3.client("s3")
    bucket = "lambda-comprehend-set"
    key = 'dumpy_user_data.txt'
    file = s3.get_object(Bucket=bucket, Key=key)
    data = str(file["Body"].read())

    # print(data)
    text = "hello"
    comprehend = boto3.client("comprehend")

    # Extracting sentiments using comprehend
    phi_data = []
    comprehendmedical = boto3.client(service_name='comprehendmedical')
    for i in data.split("<EXL>"):

        try:

            dict_entities = {}
            entities = comprehendmedical.detect_phi(Text=str(i))["Entities"]

            for entity in entities:
                if entity["Text"] != "" and entity['Type'] != '':
                    dict_entities[entity["Text"]] = "<" + entity['Type'] + ">"
            pattern = re.compile("|".join(dict_entities.keys()))
            # print(entities)
            i = custom_ssn_contact_layer(i)
            i=custom_email_layer(i)
            i=custom_ip_layer(i)
            text = pattern.sub(lambda m: dict_entities[m.group(0)], str(i))
            text = custom_ssn_contact_layer(text)
            phi_data.append(text)
        except:
            phi_data.append(i)
    # entities = comprehend.detect_entities(Text=text, LanguageCode="en")
    # pprint(phi_data)

    return phi_data

def custom_ip_layer(line):
    pattern = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)([ (\[]?(\.|dot)[ )\]]?(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3})"
    ips = [each[0] for each in re.findall(pattern, line)]
    for item in ips:
        location = ips.index(item)
        ip = re.sub("[ ()\[\]]", "", item)
        ip = re.sub("dot", ".", ip)
        ips.remove(item)
        ips.insert(location, ip)

    for ip in ips:
        line = line.replace(ip, "<IP-ADDRESS>")

    return line

def custom_email_layer(text):
    return re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+',"<EMAIL>", text)
def custom_ssn_contact_layer(text):
    regex_ssn1 = '(\d{3})[-\s*/](\d{2})[-\s*/](\d{4})'
    regex_ssn2 = "\d\s*" * 9
    regex_number = "\d{3,}"
    if re.search(regex_ssn1, text):
        regex_ssn = regex_ssn1
    elif re.search(regex_ssn2, text):
        regex_ssn = regex_ssn2

    elif re.search(regex_number, text):
        return re.sub(regex_number, "<NUMBER_ID>", text)
    else:
        return test
    fetch_pattern = re.findall(regex_ssn, text)

    ssn_digits_list = [tuple(xi for xi in x if xi != '') for x in fetch_pattern]
    if len(ssn_digits_list) == 0:
        return text

    for item in ssn_digits_list:

        is_ssn = False
        if (item[0] != "000" and item[1] != "666") and not (900 < int(item[0]) and int(item[0]) < 999) and item[
            1] != "00" and item[2] != "0000":

            return re.sub(regex_ssn, "<US_SSN>", text)
        else:
            return re.sub(regex_ssn, "<NUMBER_OR_ID_9_DIGIT>", text)




