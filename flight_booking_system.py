import os
from abc import ABC, abstractmethod
from datetime import datetime


# Absztrakt Járat osztály
class Flight(ABC):
    def __init__(self, flight_number, destination, ticket_price, max_seats):
        self.flight_number = flight_number
        self.destination = destination
        self.ticket_price = ticket_price
        self.max_seats = max_seats
        self.booked_seats = 0

    def is_available(self):
        return self.booked_seats < self.max_seats

    def book_seat(self):
        if self.is_available():
            self.booked_seats += 1
            return True
        return False

    def cancel_seat(self):
        if self.booked_seats > 0:
            self.booked_seats -= 1
            return True
        return False

    @abstractmethod
    def get_flight_info(self):
        pass


# Belföldi járatok osztálya
class DomesticFlight(Flight):
    def __init__(self, flight_number, destination, ticket_price, max_seats):
        super().__init__(flight_number, destination, ticket_price * 0.8, max_seats)

    def get_flight_info(self):
        return f"Belföldi járat: {self.flight_number}, Célállomás: {self.destination}, Jegyár: {self.ticket_price} Ft, Szabad helyek: {self.max_seats - self.booked_seats}"


# Nemzetközi járatok osztálya
class InternationalFlight(Flight):
    def __init__(self, flight_number, destination, ticket_price, max_seats):
        super().__init__(flight_number, destination, ticket_price * 1.5, max_seats)

    def get_flight_info(self):
        return f"Nemzetközi járat: {self.flight_number}, Célállomás: {self.destination}, Jegyár: {self.ticket_price} Ft, Szabad helyek: {self.max_seats - self.booked_seats}"


# LégiTársaság osztály, amely a járatokat kezeli
class Airline:
    def __init__(self, name):
        self.name = name
        self.flights = []

    def add_flight(self, flight):
        self.flights.append(flight)

    def get_flights(self):
        return [flight.get_flight_info() for flight in self.flights]


# JegyFoglalás osztály a foglalások kezelésére
class Booking:
    def __init__(self, customer_name, flight, travel_date):
        self.customer_name = customer_name
        self.flight = flight
        self.travel_date = travel_date

    def is_date_valid(self):
        travel_date_obj = datetime.strptime(self.travel_date, '%Y-%m-%d')
        return travel_date_obj > datetime.now()

    def get_booking_info(self):
        return f"{self.customer_name},{self.flight.flight_number},{self.flight.destination},{self.flight.ticket_price},{self.travel_date}"

    @staticmethod
    def from_string(data, flights):
        customer_name, flight_number, destination, ticket_price, travel_date = data.split(',')
        for flight in flights:
            if flight.flight_number == flight_number and flight.destination == destination:
                return Booking(customer_name, flight, travel_date)
        return None


# Fájlba írás és olvasás
def save_bookings(bookings, filename='foglalasok.txt'):
    with open(filename, 'w') as file:
        for booking in bookings:
            file.write(booking.get_booking_info() + '\n')


def load_bookings(filename='foglalasok.txt', flights=[]):
    bookings = []
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
            for line in lines:
                booking = Booking.from_string(line.strip(), flights)
                if booking:
                    bookings.append(booking)
    return bookings


# Fő program, amely kezeli a felhasználói interakciókat
def main():
    airline = Airline("Wizz Air")  # Létrehozzuk a légitársaságot Wizz Air névvel
    flight1 = DomesticFlight("DF123", "Budapest", 10000, 10)
    flight2 = DomesticFlight("DF456", "Debrecen", 8000, 8)
    flight3 = InternationalFlight("IF789", "London", 20000, 5)

    airline.add_flight(flight1)
    airline.add_flight(flight2)
    airline.add_flight(flight3)

    # Betöltjük a korábbi foglalásokat
    bookings = load_bookings(flights=airline.flights)

    print(f"Üdvözöljük a {airline.name} Repülőjegy Foglalási Rendszerben!")

    while True:
        print("\nVálasszon az alábbi lehetőségek közül:")
        print("1. Jegy foglalása")
        print("2. Foglalás lemondása")
        print("3. Foglalások listázása")
        print("4. Kilépés")

        choice = input("Kérem, válasszon: ")

        if choice == "1":
            customer_name = input("Kérem, adja meg a nevét: ")
            for idx, flight_info in enumerate(airline.get_flights(), 1):
                print(f"{idx}. {flight_info}")
            flight_choice = int(input("Válassza ki a járatot: ")) - 1

            if 0 <= flight_choice < len(airline.flights):
                flight = airline.flights[flight_choice]
                if flight.is_available():
                    travel_date = input("Adja meg az utazás dátumát (ÉÉÉÉ-HH-NN formátumban): ")
                    booking = Booking(customer_name, flight, travel_date)

                    if booking.is_date_valid():
                        if flight.book_seat():
                            bookings.append(booking)
                            save_bookings(bookings)
                            print("Foglalás sikeres!")
                        else:
                            print("Hiba a foglalás során.")
                    else:
                        print("Az utazás dátuma nem lehet korábbi, mint a mai nap.")
                else:
                    print("A kiválasztott járaton nincs több szabad hely.")
            else:
                print("Érvénytelen járatválasztás!")

        elif choice == "2":
            if bookings:
                for idx, booking in enumerate(bookings, 1):
                    print(f"{idx}. {booking.get_booking_info()}")
                booking_choice = int(input("Válassza ki a törlendő foglalást: ")) - 1

                if 0 <= booking_choice < len(bookings):
                    booking = bookings[booking_choice]
                    if booking.flight.cancel_seat():
                        del bookings[booking_choice]
                        save_bookings(bookings)
                        print("Foglalás sikeresen törölve!")
                    else:
                        print("Hiba történt a foglalás törlésekor.")
                else:
                    print("Érvénytelen foglalás választás!")
            else:
                print("Nincsenek foglalások.")

        elif choice == "3":
            if bookings:
                print("Aktuális foglalások:")
                for booking in bookings:
                    print(booking.get_booking_info())
            else:
                print("Nincsenek foglalások.")

        elif choice == "4":
            print("Kilépés... Köszönjük, hogy a Wizz Air Repülőjegy Foglalási Rendszert használta!")
            break

        else:
            print("Érvénytelen választás! Próbálja újra.")


if __name__ == "__main__":
    main()
