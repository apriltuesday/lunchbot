from allergen import Allergen
from functools import reduce

class Meal:
    """ A meal is composed of a name and a list of allergens """
    def __init__(self, name: str = "", allergens: str = ""):
        self.name = name
        self.allergens = allergens


    @classmethod
    def from_menu(cls, name: str, contains: list[str], may_contains: list[str]):
        """ Construct a list of Meals from a menu"""

        contains_allergens: list[Allergen] = []
        for allergen in contains:           
            contains_allergens.append(Allergen(allergen, 'contains'))

        may_contains_allergens: list[Allergen] = []
        for allergen in may_contains:
            may_contains_allergens.append(Allergen(allergen, 'may_contain'))

        allergen_list: list[list[Allergen]] = [[x, y] for x, y in zip(contains_allergens, may_contains_allergens)] 

        meal_list: list[Meal] = []
        for i, allergen in enumerate(allergen_list):            
            meal_list.append(cls(name[i], allergen))            

        return meal_list


    def __repr__(self):
        return f'Meal({self.name, self.allergens !r})'


    def is_gluten_free(self):
        # oats don't contain gluten but they're normally cross contaminated with wheat 
        gluten: set[str] = {'Wheat', 'Rye', 'Barley', 'Oats'}        
        names: list[list[str]] = [x.name for x in self.allergens]  

        if gluten.intersection(reduce(lambda x, y: x + y, names)):
            return False
        else:
            return True