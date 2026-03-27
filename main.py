import collections

class User:
    """Represents a user in the system."""
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

class Expense:
    """Represents a single expense."""
    def __init__(self, description, amount, paid_by, splits):
        self.description = description
        self.amount = amount
        self.paid_by = paid_by  # User object
        self.splits = splits    # List of tuples (User, amount)

class SplitwiseApp:
    """The main application class to manage users, groups, and expenses."""
    def __init__(self):
        self.users = {}
        self.next_user_id = 1
        self.balances = collections.defaultdict(lambda: collections.defaultdict(float))

    def add_user(self, name):
        """Adds a new user to the system."""
        user = User(self.next_user_id, name)
        self.users[self.next_user_id] = user
        self.next_user_id += 1
        print(f"User '{name}' added with ID {user.user_id}.")
        return user

    def add_expense(self, description, amount, paid_by_id, split_type, split_data):
        """
        Adds an expense and updates balances.
        split_data format:
        - EQUAL: [user_id_1, user_id_2, ...]
        - EXACT: [(user_id_1, amount_1), (user_id_2, amount_2), ...]
        - PERCENT: [(user_id_1, percent_1), (user_id_2, percent_2), ...]
        """
        if paid_by_id not in self.users:
            print(f"Error: Payer with ID {paid_by_id} not found.")
            return

        paid_by_user = self.users[paid_by_id]
        splits = []
        total_split_amount = 0

        if split_type == 'EQUAL':
            num_users = len(split_data)
            if num_users == 0:
                print("Error: No users to split with.")
                return
            split_amount = round(amount / num_users, 2)
            for user_id in split_data:
                if user_id not in self.users:
                    print(f"Error: User with ID {user_id} not found in split data.")
                    return
                splits.append((self.users[user_id], split_amount))
            total_split_amount = sum(s[1] for s in splits)
        
        elif split_type == 'EXACT':
            for user_id, split_amount in split_data:
                if user_id not in self.users:
                    print(f"Error: User with ID {user_id} not found in split data.")
                    return
                splits.append((self.users[user_id], split_amount))
            total_split_amount = sum(s[1] for s in splits)

        elif split_type == 'PERCENT':
            total_percent = sum(p[1] for p in split_data)
            if abs(total_percent - 100.0) > 0.01:
                print(f"Error: Percentages must add up to 100, but they add up to {total_percent}.")
                return
            for user_id, percent in split_data:
                if user_id not in self.users:
                    print(f"Error: User with ID {user_id} not found in split data.")
                    return
                split_amount = round((amount * percent) / 100, 2)
                splits.append((self.users[user_id], split_amount))
            total_split_amount = sum(s[1] for s in splits)
        
        else:
            print("Error: Invalid split type.")
            return

        # Handle potential rounding issues by adjusting the last split
        if total_split_amount != amount:
            diff = amount - total_split_amount
            splits[-1] = (splits[-1][0], round(splits[-1][1] + diff, 2))
            
        expense = Expense(description, amount, paid_by_user, splits)
        self._update_balances(expense)
        print(f"Expense '{description}' of ${amount:.2f} added.")

    def _update_balances(self, expense):
        """Internal method to update the balances based on an expense."""
        payer = expense.paid_by
        for participant, amount_owed in expense.splits:
            if payer.user_id != participant.user_id:
                # participant owes payer
                self.balances[participant.user_id][payer.user_id] += amount_owed
                # payer is owed by participant
                self.balances[payer.user_id][participant.user_id] -= amount_owed
    
    def show_balances(self, user_id=None):
        """
        Shows the balances for a specific user or for all users.
        A positive balance means the user is owed money.
        A negative balance means the user owes money.
        """
        if not self.users:
            print("No users in the system.")
            return

        print("\n--- Balances ---")
        if user_id:
            if user_id not in self.users:
                print(f"Error: User with ID {user_id} not found.")
                return
            self._show_user_balance(user_id)
        else:
            for uid in self.users:
                self._show_user_balance(uid)
        print("----------------\n")
    
    def _show_user_balance(self, user_id):
        """Helper to print balances for a single user."""
        user_name = self.users[user_id].name
        total_balance = 0
        has_balance = False

        # Create a copy to iterate over to avoid issues with defaultdict creating keys
        balance_items = list(self.balances[user_id].items())

        for other_user_id, amount in balance_items:
            # Also check the reverse relationship
            reverse_amount = self.balances[other_user_id].get(user_id, 0)
            net_amount = amount - reverse_amount
            
            if abs(net_amount) < 0.01:
                continue
            
            has_balance = True
            other_user_name = self.users[other_user_id].name
            if net_amount < 0:
                print(f"{user_name} owes {other_user_name}: ${-net_amount:.2f}")
            else: 
                print(f"{other_user_name} owes {user_name}: ${net_amount:.2f}")

        # Recalculate total balance from simplified view
        net_balance = sum(self.balances[other_id][user_id] - self.balances[user_id][other_id] for other_id in self.users if other_id != user_id)
        
        if not has_balance and abs(net_balance) < 0.01:
             print(f"{user_name} is all settled up.")
        else:
            if net_balance > 0:
                print(f"  -> {user_name} gets back ${net_balance:.2f} in total.")
            elif net_balance < 0:
                 print(f"  -> {user_name} owes ${-net_balance:.2f} in total.")
            else:
                 print(f"  -> {user_name} is settled up overall.")
        print("-" * 15)


    def simplify_debts(self):
        """Calculates and prints the minimum number of transactions to settle all debts."""
        print("\n--- Simplified Debts ---")
        net_balances = collections.defaultdict(float)
        
        # Calculate net balance for each user
        for user_id in self.users:
            balance = sum(self.balances[other_id][user_id] - self.balances[user_id][other_id] for other_id in self.users)
            net_balances[user_id] = balance

        debtors = []
        creditors = []

        for user_id, balance in net_balances.items():
            if balance < 0:
                debtors.append({'id': user_id, 'amount': -balance})
            elif balance > 0:
                creditors.append({'id': user_id, 'amount': balance})

        transactions = []
        
        # Use a greedy approach to settle debts
        while debtors and creditors:
            debtors.sort(key=lambda x: x['amount'], reverse=True)
            creditors.sort(key=lambda x: x['amount'], reverse=True)

            debtor = debtors[0]
            creditor = creditors[0]
            
            transfer_amount = min(debtor['amount'], creditor['amount'])
            
            transactions.append(
                f"{self.users[debtor['id']].name} pays {self.users[creditor['id']].name}: ${transfer_amount:.2f}"
            )
            
            debtor['amount'] -= transfer_amount
            creditor['amount'] -= transfer_amount
            
            if abs(debtor['amount']) < 0.01:
                debtors.pop(0)
            if abs(creditor['amount']) < 0.01:
                creditors.pop(0)

        if not transactions:
            print("Everyone is all settled up!")
        else:
            for t in transactions:
                print(t)
        print("------------------------\n")

def print_menu():
    """Prints the main menu options."""
    print("\nWhat would you like to do?")
    print("1. Add a new user")
    print("2. Add a new expense")
    print("3. Show balances for all users")
    print("4. Show balances for a specific user")
    print("5. Simplify all debts")
    print("6. Exit")

def get_user_ids_from_input(app, prompt):
    """Helper function to get a list of user IDs from user input."""
    ids = []
    while True:
        id_str = input(prompt)
        if not id_str:
            break
        try:
            user_id = int(id_str)
            if user_id not in app.users:
                print("Error: Invalid user ID.")
            else:
                ids.append(user_id)
        except ValueError:
            print("Invalid input. Please enter a number.")
    return ids

def main():
    """Main function to run the command-line interface."""
    app = SplitwiseApp()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            name = input("Enter the new user's name: ")
            if name:
                app.add_user(name)
            else:
                print("Name cannot be empty.")
        
        elif choice == '2':
            if not app.users:
                print("Error: No users in the system. Please add users first.")
                continue

            print("Users in the system:")
            for uid, user in app.users.items():
                print(f"  ID: {uid}, Name: {user.name}")
            
            try:
                description = input("Enter expense description: ")
                amount = float(input("Enter total amount: "))
                paid_by_id = int(input("Enter the user ID of the person who paid: "))
                
                if paid_by_id not in app.users:
                    print("Error: Payer ID not found.")
                    continue
                
                split_type = input("Enter split type (EQUAL, EXACT, PERCENT): ").upper()
                
                split_data = []
                if split_type == 'EQUAL':
                    print("Enter user IDs to split with (one per line, press Enter to finish):")
                    participants = get_user_ids_from_input(app, "User ID: ")
                    split_data = participants
                elif split_type == 'EXACT':
                    print("Enter user IDs and their exact share (press Enter to finish):")
                    while True:
                        user_id_str = input("User ID: ")
                        if not user_id_str:
                            break
                        user_id = int(user_id_str)
                        if user_id in app.users:
                            exact_amount = float(input(f"Amount for {app.users[user_id].name}: "))
                            split_data.append((user_id, exact_amount))
                        else:
                            print("Invalid User ID.")
                elif split_type == 'PERCENT':
                    print("Enter user IDs and their percentage share (press Enter to finish):")
                    while True:
                        user_id_str = input("User ID: ")
                        if not user_id_str:
                            break
                        user_id = int(user_id_str)
                        if user_id in app.users:
                            percent = float(input(f"Percentage for {app.users[user_id].name}: "))
                            split_data.append((user_id, percent))
                        else:
                            print("Invalid User ID.")
                else:
                    print("Invalid split type.")
                    continue
                
                app.add_expense(description, amount, paid_by_id, split_type, split_data)

            except ValueError:
                print("Invalid input. Please enter a valid number for amounts and IDs.")

        elif choice == '3':
            app.show_balances()

        elif choice == '4':
            try:
                user_id = int(input("Enter the user ID to show balances for: "))
                app.show_balances(user_id)
            except ValueError:
                print("Invalid input. Please enter a valid user ID.")
        
        elif choice == '5':
            app.simplify_debts()

        elif choice == '6':
            print("Exiting application. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")


if __name__ == "__main__":
    main()

