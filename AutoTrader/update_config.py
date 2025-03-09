import re

# Configuration file name (update this if needed)
CONFIG_FILE = "config.py"  # Replace with the actual filename


def update_headers():
    # Get user input
    new_cookie = input("Enter your Cookie: ")
    new_x_session_id = input("Enter your x-sessionId: ")

    # Read the existing config file
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    # Regex pattern to find and replace the 'Cookie' and 'x-sessionId' values
    content = re.sub(
        r"('Cookie':\s*)'[^']*'",  # Matches 'Cookie': 'SOMETHING'
        fr"\1'{new_cookie}'",  # Replace with new Cookie value
        content
    )

    content = re.sub(
        r"('x-sessionId':\s*)'[^']*'",  # Matches 'x-sessionId': 'SOMETHING'
        fr"\1'{new_x_session_id}'",  # Replace with new x-sessionId value
        content
    )

    # Write back the updated content
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        file.write(content)

    print("Configuration updated successfully!")


if __name__ == "__main__":
    update_headers()
