class ReadTXT:
    @staticmethod
    def read_file(file_path):
        """
        Reads and returns the content of a text file.

        Args:
            file_path (str): The path to the text file to be read.

        Returns:
            str: The content of the file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return "File not found."
        except Exception as e:
            return f"An error occurred: {e}"
    
if __name__ == "__main__":
    file_path = "src/data/job_description/job_description.txt"
    file_content = ReadTXT.read_file(file_path)
    print(file_content)