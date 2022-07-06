class Allergen:
    """ An allergen can contain multiple allergens of the same type (e.g. contains). """
    def __init__(self, name: str = "", type: str = ""):
        # TODO: assert allergens are one of the big 14
        # https://www.food.gov.uk/business-guidance/allergen-guidance-for-food-businesses
        # how to handle a failure to parse allergens?
        self.name = name
        assert type in ["contains", "may_contain"], "Invalid allergen type"
        self.type = type
    
    
    def __repr__(self):
        return f'Allergens({self.type, self.name !r})'