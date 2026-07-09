# CLASS_SN B1


def calculate_total(*prices):
    """
    Summary: takes any number and returns the total sum
    args(float/int)
    """
    total = 0
    for price in prices:
        try:
            total += price
        except TypeError:
            print("That is not a valid number. skipping it.")
        except Exception as e:
            print(f"Something unexpected happened with {e}, check if you inputed a text or an undefined character")
        continue
    return total
    
        
    

# print(calculate_total(3,2,4))
# print(calculate_total(12.3,23,"3"))

def apply_discount(total,discount_percent=0):
    """Summary
    total(float/int): the total price of goods or items
    discount_percent(float/int): the percentage to be applied as discount, must be between 0 and 100"""
    try:
        if not isinstance(discount_percent, (int, float)):
            raise TypeError(discount_percent)
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError(discount_percent)
        discount_dec = discount_percent / 100
        discounted_price = total - (total * discount_dec)
        return discounted_price
    except ValueError as v:
        print(f"Discount Percentage must be between 0 and 100 — invalid value: {v}")
    except TypeError as t:
        print(f"Please input a number for discount_percent: {t}")
    except Exception as e:
        print(f"Something unexpected happened with {e}")

#print(apply_discount("i","this"))

def add_vat(price, vat_rate=7.5):
    """Summary:
    price(float/int): The price of items
    vat_rate(float/int): the value added tax for the items in percentage 
    """
    try:
        if vat_rate <0:
            raise ValueError
        price_vat = round(price + (price*(vat_rate/100)),2)
        return price_vat
    except ValueError:
        return "vat_rate cannot be negative, input a positive number"
        
# print(add_vat(218632.323,-98))

prices = (1500, 2000, 3500, 800)
total   = calculate_total(*prices)      # 7800
after_d = apply_discount(total, 10)     # 7020.0
final   = add_vat(after_d)              # 7546.5
print(f"Total: ₦{final}")               # Total: ₦7546.5
# Error cases
apply_discount(5000, 110)   # ValueError: Discount cannot exceed 100%
print(calculate_total(200, 'abc', 300))  # skips 'abc', returns 500



