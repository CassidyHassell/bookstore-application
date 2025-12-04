from faker.providers import BaseProvider
import random as _random

class BookTitleProvider(BaseProvider):
    """Generate varied, plausible book titles.

    Use `fake.book_title()` after adding this provider to a Faker instance.
    """

    ADJECTIVES = [
        "Lost", "Hidden", "Dark", "Silver", "Final", "Silent", "Broken", "Secret",
        "Lonely", "Last", "Brave", "Strange", "Empty", "Wild", "Sacred", "Forgotten"
    ]

    NOUNS = [
        "Kingdom", "City", "Garden", "House", "River", "Forest", "Light", "Night",
        "Memory", "Song", "Book", "Promise", "Sea", "Shadow", "Road", "Letter"
    ]

    PLACES = [
        "Autumn", "Eden", "Avalon", "Atlantis", "Hollow", "Ridge", "Harbor", "Heights"
    ]

    TEMPLATES = [
        "The {adj} {noun}",
        "{noun} of the {noun2}",
        "The {noun} and the {noun2}",
        "A {adj} {noun}",
        "{noun}: A {adj} Tale",
        "{noun} of {place}",
        "The {adj} {noun} Trilogy",
        "{noun} in the {place}",
        "{adj} {noun}: A Novel",
        "The {adj} {noun} and Other Stories"
    ]

    def book_title(self):
        g = self.generator
        rnd = getattr(g, "random", _random)

        # local copies to avoid repeated attribute lookups
        templates = self.TEMPLATES
        adj_list = self.ADJECTIVES

        tmpl = rnd.choice(templates)
        adj = rnd.choice(adj_list)

        # Generate nouns/places using helper but pass the Random instance
        noun = self._make_noun(g, rnd)
        noun2 = self._make_noun(g, rnd, avoid=noun)
        place = self._make_place(g, rnd)

        title = tmpl.format(adj=adj, noun=noun, noun2=noun2, place=place)

        # Occasionally append a subtitle for variety (approx 20% chance)
        if rnd.randint(1, 10) > 8:
            # Use generator sentence for naturalness but keep it short
            subtitle = g.sentence(nb_words=3).rstrip(".")
            title = f"{title}: {subtitle}"

        return title.title()

    def _make_noun(self, g, rnd=None, avoid=None):
        """Return a noun string. Prefer curated list but sometimes compose words.

        Accepts an optional Random instance `rnd` to keep sampling deterministic
        when Faker is seeded.
        """
        if rnd is None:
            rnd = getattr(g, "random", _random)

        nouns = self.NOUNS

        # 60% curated, 40% generated
        if rnd.randint(1, 10) <= 6:
            choice = rnd.choice(nouns)
            if avoid and choice == avoid:
                choice = next((n for n in nouns if n != avoid), choice)
            return choice

        # generated: sometimes compound, sometimes single
        if rnd.randint(1, 10) > 6:
            # Use faker.words to get two words when available
            try:
                parts = g.words(nb=2)
                return " ".join(parts).replace("_", " ")
            except Exception:
                w1 = g.word()
                w2 = g.word()
                return f"{w1} {w2}".replace("_", " ")
        else:
            try:
                return g.word().replace("_", " ")
            except Exception:
                return rnd.choice(nouns)

    def _make_place(self, g, rnd=None):
        """Return a place name. Prefer curated list, else faker city or composed."""
        if rnd is None:
            rnd = getattr(g, "random", _random)

        places = self.PLACES
        r = rnd.randint(1, 10)
        if r <= 5:
            return rnd.choice(places)
        if r <= 8:
            try:
                return g.city()
            except Exception:
                pass
        # fallback: composed place
        try:
            p1, p2 = g.words(nb=2)
            return f"{p1.capitalize()} {p2.capitalize()}"
        except Exception:
            part1 = g.word().capitalize()
            part2 = g.word().capitalize()
            return f"{part1} {part2}"

class KeywordsProvider(BaseProvider):
    """Generate random keywords for books.

    Use `fake.keywords(n)` after adding this provider to a Faker instance.
    """

    KEYWORDS = [
        "Adventure", "Romance", "Mystery", "Fantasy", "Science Fiction", "Horror",
        "Thriller", "Historical", "Biography", "Self-Help", "Philosophy", "Travel",
        "Cooking", "Health", "Art", "Music", "Education", "Technology", "Business",
        "Psychology", "Poetry", "Drama", "Children", "Young Adult", "Classic"
    ]

    def keywords(self, n=3):
        """Return a list of n unique keywords.

        Uses the provider's RNG to keep results deterministic when Faker is seeded.
        """
        n = min(n, len(self.KEYWORDS))
        rnd = getattr(self.generator, "random", _random)
        return rnd.sample(self.KEYWORDS, k=n)
    
    def unique_keyword_count(self):
        return len(self.KEYWORDS)

    def keyword(self):
        """Return a single keyword string (use with `fake.keyword()` or `fake.unique.keyword()`)."""
        rnd = getattr(self.generator, "random", _random)
        return rnd.choice(self.KEYWORDS)
    
    def all_keywords(self):
        """Return the full list of keywords."""
        return self.KEYWORDS.copy()