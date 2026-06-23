# CLASS_SN B1

def power_summary(**daily_hours):
    """
    accepts keyword arguments where each key is a day name 
    and each value is the number of power hours that day (0-24). 
    Prints a summary table showing each day, hours with power, and hours without power. 
    Returns a dictionary of the same data.
    """
    result = {}

    # to validate the data and build up the result dictionary.
    for day, hours in daily_hours.items():
        try:
            hours = float(hours)
        except (TypeError, ValueError):
            print(f"Warning: {hours} is not a valid number for {day}. Skipping.")
            continue

        if hours < 0 or hours > 24:
            raise ValueError(f"Hours for {day} must be between 0 and 24")

        outage = 24 - hours
        result[day] = {"power": hours, "outage": outage}

    #to print a table of the valid days only.
    print(f"{'Day':<12} | {'Power (hrs)':^11} | {'Outage (hrs)'}")
    print("-" * 40)
    for day, hours in result.items():
        print(f"{day:<12} | {hours['power']:^11.0f} | {hours['outage']:.0f}")

    return result

def fuel_cost(hours_without_power, litres_per_hour=0.8, price_per_litre=1200):
    """
    — calculates total generator fuel cost. 
    hours_without_power is a list of daily outage hours. 
    litres_per_hour and price_per_litre have default values. 
    Returns the total cost rounded to 2 decimal places
    """
    if litres_per_hour <= 0:
        raise ValueError("litres_per_hour must be greater than 0")
    if price_per_litre <= 0:
        raise ValueError("price_per_litre must be greater than 0")
    total_gen_fuel_cost = sum(hours_without_power) * litres_per_hour * price_per_litre
    return total_gen_fuel_cost

if __name__ == "__main__":
    summary = power_summary(
        Monday=6, Tuesday=10, Wednesday="unknown", Thursday=8, Friday=14
    )

    outage_hours = [summary[day]["outage"] for day in summary]
    cost = fuel_cost(outage_hours)
    print(f"Estimated fuel cost: \u20a6{cost}")




