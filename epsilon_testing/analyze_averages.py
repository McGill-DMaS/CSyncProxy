def calculate_average(filename):
    total_sum = 0
    count = 0

    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.strip():
                    try:
                        number = float(line.strip())
                        total_sum += number
                        count += 1
                    except ValueError:
                        print(f"Warning: error at '{line.strip()}'. Skipping line.")

        if count == 0:
            return 0.0

        return total_sum / count

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    filename = "averages.txt"
    average = calculate_average(filename)

    if average is not None:
        print(f"The average is: {average:.4f}")
        with open(f"../values.txt", 'a') as f:
            f.write(f"{average} ")