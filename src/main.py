"""
main.py
The entry point for the application. Run this via: python src/main.py
"""
# Past Electricity Bills Tracker
# A CLI app to record and analyze your electricity bills
# Made for Python class machine project

from statistics import mean


# =====================
# PRICING TIERS
# =====================

# Tiered pricing: first 100 kWh at lower rate, rest at higher rate
TIER_1_LIMIT = 100       # kWh
TIER_1_RATE = 8.50       # pesos per kWh
TIER_2_RATE = 12.00      # pesos per kWh above 100 kWh


# =====================
# CLASS DEFINITIONS
# =====================

class Meter:
    # This class handles calculations between two meter readings

    def __init__(self, previous_reading: float, current_reading: float):
        self.previous_reading = previous_reading
        self.current_reading = current_reading

    def get_kwh_used(self) -> float:
        # Base case: current reading must be higher than previous
        if self.current_reading < self.previous_reading:
            print("❌ Error: Current reading cannot be less than previous reading.")
            return 0.0
        return self.current_reading - self.previous_reading

    def compute_bill(self) -> float:
        # Data processing: tiered pricing algorithm
        kwh = self.get_kwh_used()

        if kwh <= 0:
            return 0.0
        elif kwh <= TIER_1_LIMIT:
            # All usage falls within tier 1
            total = kwh * TIER_1_RATE
        else:
            # First 100 kWh at tier 1 rate, the rest at tier 2
            tier1_cost = TIER_1_LIMIT * TIER_1_RATE
            tier2_cost = (kwh - TIER_1_LIMIT) * TIER_2_RATE
            total = tier1_cost + tier2_cost

        return round(total, 2)


class Bill:
    # This class stores all info about one electricity bill

    def __init__(self, billing_period: str, previous_reading: float,
                 current_reading: float, date_paid: str):
        self.billing_period = billing_period        # e.g. "January 2025"
        self.date_paid = date_paid                  # e.g. "2025-02-10"

        # Use the Meter class to compute values
        meter = Meter(previous_reading, current_reading)
        self.kwh_used = meter.get_kwh_used()
        self.total_amount = meter.compute_bill()

        # Tags stored as a set - unique labels for each bill
        self.tags = set()

    def add_tag(self, tag: str):
        self.tags.add(tag.strip().lower())

    def __str__(self):
        tag_str = ", ".join(self.tags) if self.tags else "none"
        return (f"[{self.billing_period}] | "
                f"{self.kwh_used:.2f} kWh | "
                f"P{self.total_amount:.2f} | "
                f"Paid: {self.date_paid} | "
                f"Tags: {tag_str}")


class BillTracker:
    # This class manages all the bills and user operations

    def __init__(self, name: str):
        self.name = name
        self.bills = []              # List - stores all Bill objects
        self.monthly_totals = {}     # Dictionary - period -> amount
        self.all_tags = set()        # Set - all unique tags used

    def add_bill(self, billing_period: str, previous_reading: float,
                 current_reading: float, date_paid: str, tags: str = ""):

        new_bill = Bill(billing_period, previous_reading, current_reading, date_paid)

        if new_bill.kwh_used <= 0:
            print("⚠️  Bill not added due to invalid readings.")
            return

        # Add tags if provided
        if tags:
            for tag in tags.split(","):
                new_bill.add_tag(tag)
                self.all_tags.add(tag.strip().lower())

        self.bills.append(new_bill)

        # Save to dictionary for quick lookup by period
        self.monthly_totals[billing_period] = new_bill.total_amount

        print(f"\n✅ Bill added: {new_bill}")

    def show_all_bills(self, sort_by: str = "period"):
        # Sorting algorithm - sort by period (default) or by amount
        if not self.bills:
            print("\n⚠️  No bills recorded yet!")
            return

        if sort_by == "amount_high":
            sorted_bills = sorted(self.bills, key=lambda b: b.total_amount, reverse=True)
            label = "Highest to Lowest Cost"
        elif sort_by == "amount_low":
            sorted_bills = sorted(self.bills, key=lambda b: b.total_amount)
            label = "Lowest to Highest Cost"
        elif sort_by == "kwh":
            sorted_bills = sorted(self.bills, key=lambda b: b.kwh_used, reverse=True)
            label = "Highest to Lowest kWh"
        else:
            # Default: keep original entry order (chronological)
            sorted_bills = self.bills
            label = "Chronological Order"

        print(f"\n========== ALL BILLS ({label}) ==========")
        for i, b in enumerate(sorted_bills, 1):
            print(f"{i}. {b}")
        print("===========================================")

    def show_summary(self):
        # Data processing: calculate averages, totals, trends
        if not self.bills:
            print("\n⚠️  No bills recorded yet!")
            return

        amounts = [b.total_amount for b in self.bills]
        kwh_list = [b.kwh_used for b in self.bills]

        total_paid = sum(amounts)
        avg_bill = mean(amounts)
        avg_kwh = mean(kwh_list)
        highest = max(amounts)
        lowest = min(amounts)

        print("\n========== SUMMARY REPORT ==========")
        print(f"Account Name:     {self.name}")
        print(f"Total Bills:      {len(self.bills)}")
        print(f"Total Amount Paid: P{total_paid:.2f}")
        print(f"Average Bill:     P{avg_bill:.2f}")
        print(f"Average kWh Used: {avg_kwh:.2f} kWh")
        print(f"Highest Bill:     P{highest:.2f}")
        print(f"Lowest Bill:      P{lowest:.2f}")
        print(f"All Tags:         {self.all_tags if self.all_tags else 'none'}")
        print("=====================================")

    def trend_analysis(self):
        # Trend analysis algorithm: compare each bill to the previous one
        if len(self.bills) < 2:
            print("\n⚠️  Need at least 2 bills to show trends.")
            return

        print("\n========== TREND ANALYSIS ==========")
        print("(Comparing each bill to the one before it)\n")

        for i in range(1, len(self.bills)):
            current = self.bills[i]
            previous = self.bills[i - 1]

            # Base case: avoid division by zero
            if previous.kwh_used == 0:
                print(f"  {current.billing_period}: Cannot compare (previous kWh is 0)")
                continue

            # Percentage change formula
            kwh_change = current.kwh_used - previous.kwh_used
            percent_change = (kwh_change / previous.kwh_used) * 100
            percent_change = round(percent_change, 2)

            # Show direction of change
            if percent_change > 0:
                direction = f"📈 UP {percent_change}%"
            elif percent_change < 0:
                direction = f"📉 DOWN {abs(percent_change)}%"
            else:
                direction = "➡️  No Change"

            print(f"  {previous.billing_period} → {current.billing_period}: "
                  f"{direction} "
                  f"({previous.kwh_used:.2f} → {current.kwh_used:.2f} kWh)")

        print("=====================================")

    def search_by_tag(self, search_tag: str):
        # Search algorithm - find bills with a matching tag
        search_tag = search_tag.strip().lower()
        results = [b for b in self.bills if search_tag in b.tags]

        print(f"\n🔍 Bills tagged '{search_tag}':")
        if results:
            for b in results:
                print(f"  - {b}")
        else:
            print("  No bills found with that tag.")

    def show_tier_breakdown(self):
        # Show how each bill was calculated using tiered pricing
        if not self.bills:
            print("\n⚠️  No bills recorded yet!")
            return

        print("\n========== TIER PRICING BREAKDOWN ==========")
        print(f"  Tier 1: First {TIER_1_LIMIT} kWh at P{TIER_1_RATE}/kWh")
        print(f"  Tier 2: Above {TIER_1_LIMIT} kWh at P{TIER_2_RATE}/kWh\n")

        for b in self.bills:
            kwh = b.kwh_used
            if kwh <= TIER_1_LIMIT:
                breakdown = f"All {kwh:.2f} kWh @ Tier 1"
            else:
                t1 = TIER_1_LIMIT
                t2 = kwh - TIER_1_LIMIT
                breakdown = f"{t1:.0f} kWh @ Tier 1 + {t2:.2f} kWh @ Tier 2"

            print(f"  {b.billing_period}: {breakdown} = P{b.total_amount:.2f}")

        print("============================================")


# =====================
# MAIN CLI LOOP
# =====================

def main():
    print("========================================")
    print("   PAST ELECTRICITY BILLS TRACKER      ")
    print("========================================")
    name = input("Enter account holder name: ").strip()

    if not name:
        name = "User"

    tracker = BillTracker(name)
    print(f"\nWelcome, {tracker.name}! Let's track your electricity bills.\n")

    while True:
        print("\n----- MENU -----")
        print("1. Add a Bill")
        print("2. View All Bills")
        print("3. View Summary")
        print("4. Trend Analysis")
        print("5. Tier Price Breakdown")
        print("6. Search by Tag")
        print("7. Exit")
        print("----------------")

        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            print("\n-- ADD ELECTRICITY BILL --")
            try:
                billing_period = input("Billing Period (e.g. January 2025): ").strip()
                prev = float(input("Previous Meter Reading (kWh): "))
                curr = float(input("Current Meter Reading (kWh): "))
                date_paid = input("Date Paid (e.g. 2025-02-10): ").strip()
                tags = input("Tags (optional, comma-separated e.g. summer,high): ").strip()
                tracker.add_bill(billing_period, prev, curr, date_paid, tags)
            except ValueError:
                print("❌ Invalid input. Please enter valid numbers for readings.")

        elif choice == "2":
            print("\nSort by:")
            print("  1. Chronological (default)")
            print("  2. Highest to Lowest Cost")
            print("  3. Lowest to Highest Cost")
            print("  4. Highest kWh Usage")
            sort_choice = input("Choose sort (1-4): ").strip()

            sort_map = {
                "1": "period",
                "2": "amount_high",
                "3": "amount_low",
                "4": "kwh"
            }
            sort_by = sort_map.get(sort_choice, "period")
            tracker.show_all_bills(sort_by)

        elif choice == "3":
            tracker.show_summary()

        elif choice == "4":
            tracker.trend_analysis()

        elif choice == "5":
            tracker.show_tier_breakdown()

        elif choice == "6":
            tag = input("Enter tag to search: ").strip()
            tracker.search_by_tag(tag)

        elif choice == "7":
            print(f"\nGoodbye, {tracker.name}! Stay on top of your electricity usage! ⚡")
            break

        else:
            print("❌ Invalid choice. Please pick 1-7.")


# Run the program
if __name__ == "__main__":
    main()
