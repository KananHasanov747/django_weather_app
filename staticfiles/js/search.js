function citySearch() {
  return {
    query: "",
    cities: [],
    highlightedIndex: 0,

    fetchCities() {
      if (this.query.length > 0) {
        fetch(`search/${this.query}/`)
          .then((response) => response.text())
          .then((list) => {
            this.cities = JSON.parse(list);
            this.highlightedIndex = 0;
          });
      } else {
        this.cities = [];
      }
    },

    highlightNext() {
      if (this.highlightedIndex < this.cities.length - 1) {
        this.highlightedIndex++;
      } else {
        this.highlightedIndex = 0;
      }
    },

    highlightPrevious() {
      if (this.highlightedIndex > 0) {
        this.highlightedIndex--;
      } else {
        this.highlightedIndex = this.cities.length - 1;
      }
    },

    selectCity(index = null) {
      const selectedCity = this.cities[index ?? this.highlightedIndex];
      if (selectedCity) {
        this.url = new URL(window.location.href);
        this.url.searchParams.set("city", selectedCity.city);
        this.url.searchParams.set("country", selectedCity.country);
        window.history.pushState({}, "", this.url);
        htmx.ajax("GET", this.url.toString(), { target: "#content" });
      }
    },
  };
}
