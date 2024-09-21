import pandas as pd

def filter_test_keywords(parsed_results, file_name, tolerance=40, keyword_tolerance=30, skip_lines=1):
    overlay = parsed_results.get("TextOverlay")
    if not overlay:
        print("No overlay data available.")
        return
    
    lines = overlay.get("Lines")
    print(f"Lines: {lines}")

    # List to store top values of lines matching 'Amount'
    top_values_list = []
    amount_list = []

    # Search for 'Amount' and store top values of matching lines
    for line in lines:
        for word in line.get("Words"):
            if word.get("WordText").lower() == 'amount':
                amount_location = word.get("Left")
                amount_width = word.get("Width")
                left_range_amount = (amount_location - 10, amount_location + amount_width)
                print(f"Amount Location: {amount_location}, Width: {amount_width}, Left Range Amount: {left_range_amount}")
                
                # Store top values for lines within the left location range
                for line in lines:
                    if any(left_range_amount[0] <= word.get("Left") <= left_range_amount[1] for word in line.get("Words")):
                        top_values = [word.get("Top") for word in line.get("Words")]
                        top_values_list.extend(top_values)
                        print(f"Top Values: {top_values}")

                        # Assuming the amount is the last word in the line
                        amount_value = line.get("Words")[-1].get("WordText")
                        print(f"Raw Amount Value: {amount_value}")

                        # Convert amount to float if possible, otherwise store as NaN
                        try:
                            amount_value = float(amount_value.replace(",", ""))
                        except ValueError:
                            amount_value = float('nan')
                        print(f"Converted Amount Value: {amount_value}")

                        amount_list.append(amount_value)

    # Calculate the adjusted top values (new_list) with a -4 adjustment
    new_list = []
    for i in range(0, len(top_values_list) - 1):
        new_value = top_values_list[i] + (top_values_list[i + 1] - top_values_list[i] - 4)
        new_list.append(new_value)
        print(f"Adjusted Top Value: {new_value}")

    # Search for each keyword's left location
    keyword_locations = {}
    keywords = ['Test', 'Item', 'Description', 'Particulars']
    keyword_found = False

    for keyword in keywords:
        if keyword_found:
            break

        for line in lines:
            for word in line.get("Words"):
                if keyword.lower() in word.get("WordText").lower():
                    keyword_locations[keyword] = (word.get("Left"), word.get("Width"))
                    keyword_found = True
                    print(f"Found Keyword: {keyword}, Location: {keyword_locations[keyword]}")
                    break
            if keyword_found:
                break

    if not keyword_locations:
        print("None of the keywords found.")
        return

    cnt = 0  
    combined_line = []
    final_combined_lines = []
    final_amounts = []

    for line in lines:
        if cnt >= len(new_list):
            break

        for keyword, (keyword_left, keyword_width) in keyword_locations.items():
            left_range_keyword = (keyword_left - 10, keyword_left + keyword_width + keyword_tolerance)
            if any(left_range_keyword[0] <= word.get("Left") <= left_range_keyword[1] for word in line.get("Words")):
                line_text = " ".join(word.get("WordText") for word in line.get("Words"))
                print(f"Line Text: {line_text}")

                if line.get("Words"):
                    first_word_top_value = line.get("Words")[0].get("Top")
                    print(f"First Word Top Value: {first_word_top_value}")

                    if first_word_top_value < new_list[cnt]:
                        combined_line.append(line_text)
                    else:
                        final_combined_lines.append(" ".join(combined_line))
                        final_amounts.append(amount_list[cnt] if cnt < len(amount_list) else '')
                        combined_line = [line_text]
                        cnt += 1
                        if cnt >= len(new_list):
                            break

    if combined_line:
        final_combined_lines.append(" ".join(combined_line))
        final_amounts.append(amount_list[cnt] if cnt < len(amount_list) else '')

    # Skip the specified number of lines before saving to Excel
    df = pd.DataFrame({
        "File_Name": [file_name] * (len(final_combined_lines) - skip_lines),
        "Item_Name": final_combined_lines[skip_lines:],
        "Item_Amount": final_amounts[skip_lines:]
    })
    print(f"DataFrame before saving: {df}")

    # Ensure that the Item_Amount column is of float type, handling errors gracefully
    df["Item_Amount"] = pd.to_numeric(df["Item_Amount"], errors='coerce')
    print(f"DataFrame after converting Item_Amount: {df}")

    # Write the DataFrame to an Excel file
    df.to_excel("output.xlsx", index=False)
    print(f"Data has been written to output.xlsx with columns File_Name, Item_Name, and Item_Amount.")
