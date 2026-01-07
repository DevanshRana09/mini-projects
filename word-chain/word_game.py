import json
import random

# ---------------- LOAD CATEGORIES ----------------

with open("categories.json", "r") as f:
    raw_data = json.load(f)

CATEGORIES = {k: set(v) for k, v in raw_data.items()}

if not CATEGORIES:
    raise ValueError("No categories found in file.")

# ---------------- CATEGORY SELECTION ----------------

print("Available categories:")
for cat in CATEGORIES:
    print("-", cat)

while True:
    category = input("\nChoose a category: ").strip().lower()
    if category in CATEGORIES:
        break
    print("Invalid category. Try again.")

WORD_SET = CATEGORIES[category]
TOTAL_WORDS = len(WORD_SET)

# ---------------- GAME SETTINGS ----------------

while True:
    try:
        requested_rounds = int(input("Enter number of rounds: "))
        if requested_rounds > 0:
            break
    except ValueError:
        pass
    print("Please enter a positive number.")

MAX_ROUNDS = min(requested_rounds, TOTAL_WORDS)

lives = max(1, MAX_ROUNDS // 4)


used_words = set()
rounds_completed = 0

# ---------------- HELPER FUNCTIONS ----------------

def has_valid_word(letter):
    return any(
        word.startswith(letter) and word not in used_words
        for word in WORD_SET
    )

def get_new_valid_letter():
    letters = {word[0] for word in WORD_SET if word not in used_words}
    return random.choice(list(letters)) if letters else None

# ---------------- GAME START ----------------

start_with = get_new_valid_letter()

print("\n🎮 GAME STARTED")
print(f"Category: {category}")
print(f"Rounds to win: {MAX_ROUNDS}")
print(f"Lives: {lives}")
print("Type 'skip' to skip a letter (costs 1 life)")
print("Type 'exit' to quit\n")

# ---------------- GAME LOOP ----------------

while lives > 0 and rounds_completed < MAX_ROUNDS:
    if not has_valid_word(start_with):
        new_letter = get_new_valid_letter()
        if new_letter is None:
            break
        print(f"⚠️ No words for '{start_with}'. Switching to '{new_letter}'.")
        start_with = new_letter

    user_input = input(
        f"\nRound {rounds_completed + 1}/{MAX_ROUNDS} | "
        f"Lives: {lives} | "
        f"Letter: '{start_with}'\n"
        "Enter word (or 'skip'): "
    ).strip().lower()

    if user_input == "exit":
        print("You quit the game.")
        break

    if user_input == "skip":
        lives -= 1
        print("⏭️ Skipped! Lost 1 life.")
        start_with = get_new_valid_letter()
        if start_with is None:
            break
        continue

    if user_input in used_words:
        print("❌ Already used!")
        lives -= 1
        continue

    if user_input not in WORD_SET:
        print("❌ Invalid word for this category!")
        lives -= 1
        continue

    if not user_input.startswith(start_with):
        print(f"❌ Must start with '{start_with}'!")
        lives -= 1
        continue

    # VALID MOVE
    used_words.add(user_input)
    rounds_completed += 1
    print(f"✅ Accepted: {user_input}")
    start_with = user_input[-1]

# ---------------- GAME RESULT ----------------

print("\n🏁 GAME OVER")
print(f"Rounds completed: {rounds_completed}/{MAX_ROUNDS}")

if rounds_completed == MAX_ROUNDS:
    print("🎉 YOU WIN!")
elif lives == 0:
    print("💀 YOU LOST (no lives left).")
else:
    print("⚠️ No more words left in this category.")
print("Thanks for playing!")