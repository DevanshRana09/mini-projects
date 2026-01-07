import random
import string


# set needs more animal names for better gameplay
ANIMAL_SET = {
    "ant", "bear", "cat", "dog", "elephant", "fox", "giraffe", "horse",
    "iguana", "jaguar", "kangaroo", "lion", "monkey", "newt", "owl", "penguin",
    "quail", "rabbit", "snake", "tiger", "urchin", "vulture", "wolf", "xenops",
    "yak", "zebra", "alligator", "bat", "camel", "dolphin", "eagle", "flamingo",
    "goat", "hedgehog", "ibis", "jellyfish", "koala", "lemur", "moose", "narwhal",
    "octopus", "parrot", "quokka", "raccoon", "seal", "toucan", "urial", "vole",
    "walrus", "xerus", "yellowthroat", "zorilla"
}

used_words=set()
start_with=random.choice(string.ascii_lowercase)

while True:
    if start_with not in ANIMAL_SET:
        start_with=random.choice(string.ascii_lowercase)
    user_input = input(f"Please enter an animal name starting with '{start_with}' (or 'exit' to quit): ").strip().lower()
    if user_input == 'exit':
        print("Thanks for playing!")
        break

    elif user_input in used_words:
        print(f"Rejected: {user_input} (already used)")

    elif user_input in ANIMAL_SET:
        if user_input.startswith(start_with):
            print(f"Accepted: {user_input}")
            start_with=user_input[-1]
        else :
            print(f"Rejected: {user_input} (does not start with '{start_with}')")
    else:
        print(f"Rejected: {user_input} (either already used or not a valid animal name)")

