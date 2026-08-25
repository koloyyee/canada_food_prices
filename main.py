from db import create_ont_protein_view, piping_prices, view_to_csv

def main():
    piping_prices()
    create_ont_protein_view()
    view_to_csv(filename="ontario_protein_prices", view="view_ontario_protein_prices")


if __name__ == "__main__":
    main()
