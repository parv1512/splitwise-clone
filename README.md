# Splitwise Clone (CLI Based)

A simple command-line based Splitwise clone built in Python that helps users track shared expenses, manage balances, and simplify debts efficiently.

## Features

- Add users to the system
- Add expenses with multiple split types:
  - Equal split
  - Exact split
  - Percentage-based split
- Track balances between users
- View individual or overall balances
- Simplify debts to minimize transactions

## Tech Stack

- Python
- Collections (defaultdict)
- Command Line Interface (CLI)

## How It Works

The application maintains a balance sheet between users. When an expense is added:
- The payer is recorded
- The expense is split among participants
- Balances are updated accordingly

A debt simplification algorithm minimizes the number of transactions required to settle all balances.

## Project Structure

- `User` → Represents a user
- `Expense` → Represents an expense
- `SplitwiseApp` → Core logic for managing users, expenses, and balances
- CLI Interface → Handles user interaction

## Installation & Usage

1. Clone the repository

```bash
git clone https://github.com/your-username/splitwise-clone.git
cd splitwise-clone
```

2. Run the application

```bash
python main.py
```

## Menu Options

```
1. Add a new user
2. Add a new expense
3. Show balances for all users
4. Show balances for a specific user
5. Simplify all debts
6. Exit
```

## Example

- Add users: Alice, Bob, Charlie  
- Add expense: Alice paid $120 split equally  
- Output:
  - Bob owes Alice
  - Charlie owes Alice

## Debt Simplification

The app uses a greedy algorithm to:
- Identify debtors and creditors
- Minimize total number of transactions
- Provide simplified settlement instructions

## Limitations

- CLI-based (no GUI)
- No persistent storage (data resets on restart)
- No authentication system

## Future Improvements

- Add database support (SQLite / Firebase)
- Build a web or mobile UI
- Add group-based expense tracking
- Export reports (CSV / PDF)

## Author

Built as a learning project to understand system design, data structures, and real-world problem solving.
