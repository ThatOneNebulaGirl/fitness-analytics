from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))
from tools_for_cleaning import extract_health_records



PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "apple_export.xml"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "apple_data_raw_extract"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)






def discover_record_types(INPUT_FILE):

    import xml.etree.ElementTree as ET

    record_types = set()

    for event, elem in ET.iterparse(
        INPUT_FILE,
        events=("end",)
    ):

        if elem.tag == "Record":

            record_type = elem.attrib.get("type")

            if record_type:
                record_types.add(record_type)

        elem.clear()

    return sorted(record_types)



types = discover_record_types(INPUT_FILE)

print("\nAvailable Record Types:\n")

for t in types:
    print(t)








def find_types_by_keyword(record_types, keywords):

    matches = []

    for record_type in record_types:

        for keyword in keywords:

            if keyword.lower() in record_type.lower():
                matches.append(record_type)
                break

    return matches


types = discover_record_types(INPUT_FILE)

keywords = [
    "Body",
    "Energy",
    "Exercise",
    "Walking",
    "Flights",
    "Waist",
    "Step",
    "Count",
    "Rate",
    "Heart",
    "Sleep"
]
matches = find_types_by_keyword(types, keywords)
exclude = {
    "HKQuantityTypeIdentifierDietaryEnergyConsumed",
    "HKCategoryTypeIdentifierLowHeartRateEvent",
    "HKQuantityTypeIdentifierBodyFatPercentage",
    "HKQuantityTypeIdentifierLeanBodyMass",
    "HKDataTypeSleepDurationGoal",
    "HKCategoryTypeIdentifierSleepChanges"
}
matches = sorted([
    record_type
    for record_type in matches
    if record_type not in exclude
])


for record_type in matches:

    file_name = (
        record_type
        .replace("HKQuantityTypeIdentifier", "")
        .replace("HKCategoryTypeIdentifier", "")
        .lower()
    )
    output_file = OUTPUT_DIR / f"{file_name}_raw2.csv"
    extract_health_records(
        INPUT_FILE,
        output_file,
        record_type
    )
print("\nDatasets to extract:\n")

for record_type in matches:
    print(record_type)

print(f"\nTotal datasets: {len(matches)}\n")       