import re
import usaddress
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import pandas as pd

analyzer = AnalyzerEngine()
more_masked_data = []
data=["Mr Steve Beahan has  stomach ache . Patient SSN 789-21-8631 . He came on 10 july 2001 . Patient home address is  188 Baumbach Arcade Apt 78 Lunenburg , 1119 .we gave him http://soundcloud.com/decksharks-records/daniel-dittrich-sommer-pinch . Patient account number 6188776513 . Medical record Id MR7637312 . Patient 048-0795635 Email is KeenanHoeger@mail2wine.com Patient Id 4982800 . Here is the IP 83.138.50.0",
      "Mr Jenell Deckow is suffering from cancer . Patient SSN 81178409 . He arrived on 16.1.2023 . Patient is from 189 Jerde Mews Unit 75 North Brookfield , 2139 .Advised him to reach http://tweetphoto.com/31204893 . Patient account number 4087981266 . Medical record Id ID7699751 . Patient 06-894 382 Email is GoldenPollich@netposta.net Patient Id U3123225 . IP address 163.47.19.0",
"Mrs Drew Hegmann is suffering from heart attack . Her SSN 742-65-1447 . She contacted on 12/7/1972 . Patient is from 208 Stehr Port Peabody , 2122 .Advised her to reach http://www.youtube.com/v/6P4IxZtR_mo&hl=en_US&fs=1&""></param><param . Patient account number is  7951466186 . Medical record Id CA9235785 . Her 061854 0462487 Email is TanekaLeuschke@mail2eddie.com Patient Id 582126483 . IP address 192.152.44.0",
"Mrs Cecila Feil is suffering from heart attack . Her SSN 612-43-5824 . She contacted on 1934-7-4 . Patient is from 105 Hodkiewicz Port Westport , 2721 .",
"Mr Cheryll Mann is suffering from heart attack . Patient SSN 780 46 6236 . He arrived on 14/8/1949 . Patient is from 788 Connelly Highlands Billerica , 2186 .Advised him to reach http://tweetphoto.com/30980625 . Patient account number 1897684089 . Medical record Id CA1420545 . Patient 0326 92 3042 Email is SandaRogahn@honduras.com Patient Id 2383854 . IP address 152.100.0.0",
"Mr Izola Ebert is suffering from cancer . Patient SSN 663-30-8781 . He arrived on 12/7/1972 . Patient is from 712 Schuppe Ramp Unit 0 West Tisbury , 1604 .Advised him to reach http://imgur.com/M2v2H.png . Patient account number 0324390751 . Medical record Id MR0518554 . Patient 026 439 25 29 Email is JoMcCullough@mail2kiss.com Patient Id K542760 . IP address 15.0.0.0"]


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


def custom_address_layer(text):
    address_entities = usaddress.parse(text)
    for entity in address_entities:

        if entity[1] in ['StreetName', 'StreetNamePostType', 'SubaddressType', 'AddressNumber', 'SubaddressIdentifier']:
            text = text.replace(entity[0], "<" + entity[1] + ">")
    return text


def custom_email_layer(text):
    return re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', "<EMAIL>", text)


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
        return text
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


def presidio_deidentify_model(text):
    results = analyzer.analyze(text=text,
                               entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "MEDICAL_LICENSE", "URL", "US_SSN",
                                         "DATE_TIME", "AU_MEDICARE", "FIN/NRIC", "LOCATION", 'US_DRIVER_LICENSE',
                                         'IP_ADDRESS', 'NRP', 'CREDIT_CARD', 'CRYPTO', 'IBAN_CODE', 'US_PASSPORT', ],
                               language='en')
    anonymizer = AnonymizerEngine()
    anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
    return str(anonymized_text).split("\nitems:\n")[0].replace("text: ", "")


def custom_contact_layer(text):
    return re.sub('(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',
                  "<CONTACT>", text)


for i in data:
    de_identified_data = presidio_deidentify_model(i)
    masked_data = custom_address_layer(de_identified_data)
    masked_data = custom_ssn_contact_layer(masked_data)
    masked_data = custom_ip_layer(masked_data)
    masked_data = custom_email_layer(masked_data)
    masked_data = custom_contact_layer(masked_data)
    more_masked_data.append(masked_data)