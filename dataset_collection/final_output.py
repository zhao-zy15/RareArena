import json


with open("data/leakage_removed.json") as f:
    data = [json.loads(l) for l in f.readlines()]

with open("RDS.json", "w") as f:
    for dat in data:
        if dat['case_leakage'] == "yes":
            continue
        f.write(json.dumps({"_id": dat['_id'], 
                            "case_report": dat['rewritten_case_report'], 
                            'diagnosis': dat['Final Diagnosis'], 
                            'Orpha_name': dat['OrphaName'] if 'OrphaName' in dat else dat['Final Diagnosis'], 
                            'Orpha_id': dat['OrphaID'], 
                            "age": dat['age'], 
                            "gender": dat['gender'],
                            "pub_date": dat['pub_date']}, ensure_ascii = False) + '\n')

with open("RDC.json", "w") as f:
    for dat in data:
        if dat['case_leakage'] == "yes":
            continue
        if dat['Diagnostic_examination'] == "NA" or dat["Cleaned_examination_results"] == "NA":
            continue
        if dat['result_leakage'] == 'yes':
            continue
        f.write(json.dumps({"_id": dat['_id'], 
                            "case_report": dat['rewritten_case_report'], 
                            "test_results": dat['Cleaned_examination_results'], 
                            'diagnosis': dat['Final Diagnosis'], 
                            'Orpha_name': dat['OrphaName'] if 'OrphaName' in dat else dat['Final Diagnosis'], 
                            'Orpha_id': dat['OrphaID'], 
                            "age": dat['age'], 
                            "gender": dat['gender'],
                            "pub_date": dat['pub_date']}, ensure_ascii = False) + '\n')