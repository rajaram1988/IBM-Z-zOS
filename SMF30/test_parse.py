from smf30_binary_parser import SMFBinaryParser

parser = SMFBinaryParser('dumpsample.bin')
records = parser.parse_dump_file()

print(f'\n--- FINAL RESULTS ---')
print(f'Parsed {sum(len(r) for r in records.values())} total Type 30 records')
for st, recs in records.items():
    if recs:
        print(f'  Subtype {st}: {len(recs)} records')
        for i, rec in enumerate(recs[:3]):
            rec_dict = rec.to_dict()
            print(f'    Record {i+1}: {rec_dict}')
