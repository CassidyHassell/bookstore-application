from faker.providers import BaseProvider

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
        tmpl = g.random_element(self.TEMPLATES)
        # pick words
        adj = g.random_element(self.ADJECTIVES)
        # Generate nouns dynamically to increase variety: sometimes pick from list, sometimes create compound or faker words
        noun = self._make_noun(g)
        noun2 = self._make_noun(g, avoid=noun)
        place = self._make_place(g)

        title = tmpl.format(adj=adj, noun=noun, noun2=noun2, place=place)

        # Occasionally append a subtitle for variety
        if g.random_int(1, 10) > 8:
            subtitle = g.sentence(nb_words=3).rstrip(".")
            title = f"{title}: {subtitle}"

        # Clean up spacing and return title-cased string
        return title.title()

    def _make_noun(self, g, avoid=None):
        """Return a noun string. Occasionally compose multi-word nouns or use faker-generated words."""
        # 60% pick from curated list, 40% generate
        if g.random_int(1, 10) <= 6:
            choice = g.random_element(self.NOUNS)
            if avoid and choice == avoid:
                # try again but safe fallback
                choice = next((n for n in self.NOUNS if n != avoid), choice)
            return choice

        # generate compound noun or single faker word
        if g.random_int(1, 10) > 6:
            # two-word compound (e.g., "Silver Road")
            w1 = g.word()
            w2 = g.word()
            return f"{w1} {w2}".replace("_", " ")
        else:
            return g.word().replace("_", " ")

    def _make_place(self, g):
        """Return a place name. Prefer curated list, else use faker city or combine words."""
        # 50% curated, 30% faker.city(), 20% composed
        r = g.random_int(1, 10)
        if r <= 5:
            return g.random_element(self.PLACES)
        if r <= 8:
            try:
                return g.city()
            except Exception:
                pass
        # fallback: composed place
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
        """Return a list of n unique keywords."""
        n = min(n, len(self.KEYWORDS))
        return self.generator.random_elements(self.KEYWORDS, length=n, unique=True)
    
    def unique_keyword_count(self):
        return len(self.KEYWORDS)

    def keyword(self):
        """Return a single keyword string (use with `fake.keyword()` or `fake.unique.keyword()`)."""
        return self.generator.random_element(self.KEYWORDS)
    
    def all_keywords(self):
        """Return the full list of keywords."""
        return self.KEYWORDS.copy()