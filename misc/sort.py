def sort_txt_list(filepath):
   """
   Reads a list of lines from a text file, sorts them alphabetically,
   and returns the sorted list.

   Args:
       filepath (str): The path to the text file containing the list. Each line
                       in the file is assumed to be an item in the list.

   Returns:
       list: A list containing the sorted lines from the file.
             Returns an empty list if the file doesn't exist or is empty.
             Returns None if there's an error reading the file.
   """
   try:
       with open(filepath, 'r') as f:
           lines = f.readlines()  # Read all lines into a list
   except FileNotFoundError:
       print(f"Error: File not found at {filepath}")
       return []  # Return an empty list if the file doesn't exist
   except Exception as e:
       print(f"Error reading file: {e}")
       return None  # Return None if there's another error

   # Remove leading/trailing whitespace from each line and remove empty lines
   lines = [line.strip() for line in lines if line.strip()]

   # Sort the list alphabetically
   lines.sort()

   return lines


# Example Usage:
if __name__ == "__main__":
    sorted_list = sort_txt_list("./misc/NounList.txt")

    if sorted_list is not None:
        if sorted_list:  # Check if the list is not empty
            print("Sorted List:")
            for item in sorted_list:
                print(item)

            # Save the sorted list back to a new text file
            with open("sorted_nouns.txt", "w") as f:
                for item in sorted_list:
                    f.write(item + "\n")  # Write each item to a new line
            print("Sorted list saved to sorted_nouns.txt")
        else:
            print("The file is empty.")
    else:
        print("An error occurred while processing the file.")