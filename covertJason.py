import json

def load_data(file_path):
    """Load JSON data from a file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def transform_data(original_data):
    """Transform the original data into a more structured format."""
    transformed_data = []
    for course in original_data:
        course_info = {
            "Program": course['title'],
            "URL": course['url'],
            "Description": [],
            "Requirements": [],
            "Courses": []
        }

        # Iterate through paragraphs to categorize them
        for paragraph in course['paragraphs']:
            if "requirement" in paragraph.lower():
                course_info["Requirements"].append(paragraph)
            elif "course" in paragraph.lower() or "module" in paragraph.lower():
                course_info["Courses"].append(paragraph)
            else:
                course_info["Description"].append(paragraph)

        # Convert lists to strings for better readability
        for key in ["Description", "Requirements", "Courses"]:
            course_info[key] = " ".join(course_info[key])

        transformed_data.append(course_info)
    return transformed_data

def save_data(transformed_data, output_file_path):
    """Save the transformed data to a JSON file."""
    with open(output_file_path, 'w', encoding='utf-8') as file:
        json.dump(transformed_data, file, ensure_ascii=False, indent=4)

def main():
    # Paths to the input and output files
    input_file_path = 'data/course_info.json'
    output_file_path = 'data/transformed_course_info.json'
    
    # Load, transform, and save the data
    original_data = load_data(input_file_path)
    transformed_data = transform_data(original_data)
    save_data(transformed_data, output_file_path)

    print("Data transformation complete. Check 'transformed_course_info.json' for the output.")

# Entry point of the script
if __name__ == "__main__":
    main()
