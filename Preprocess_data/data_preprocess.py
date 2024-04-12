import json
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('stopwords')

class CourseDataProcessor:
    def __init__(self, input_filename, output_filename):
        """Initialize the processor with file paths."""
        self.input_filename = input_filename
        self.output_filename = output_filename

    def load_data(self):
        """Load JSON data from a file."""
        with open(self.input_filename, 'r', encoding='utf-8') as file:
            return json.load(file)

    def clean_text(self, text):
        """Clean and preprocess text by removing non-alphabetical characters,
        converting to lower case, and removing stopwords."""
        # Remove non-letter characters and convert to lowercase
        text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text)
        return ' '.join(word for word in words if word not in stop_words)

    def extract_info(self, course_data):
        """Extract and process key information from course descriptions."""
        cleaned_data = []
        for course in course_data:
            description = self.clean_text(course['Description'])
            course['CleanedDescription'] = description
            # Additional processing can be added here
            cleaned_data.append(course)
        return cleaned_data

    def save_data(self, data):
        """Save the processed data to a JSON file."""
        with open(self.output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def process(self):
        """Process the course data by loading, cleaning, extracting, and saving."""
        data = self.load_data()
        cleaned_data = self.extract_info(data)
        self.save_data(cleaned_data)

# Example usage
if __name__ == '__main__':
    processor = CourseDataProcessor('data/transformed_course_info.json', 'data/cleaned_data/cleaned_course_info.json')
    processor.process()