# file:   main.py
# author: Alex Krosney
# date:   December 14, 2022
#
# description: this is the main entrypoint for the application.
# For implementation details, see App.py.

from classes.App import App

def main():
    app = App()
    app.run()

if __name__ == '__main__':
    main()
