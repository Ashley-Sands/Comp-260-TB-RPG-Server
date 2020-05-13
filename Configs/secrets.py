import os


class Secrets:

    loaded = False
    store = {}

    @staticmethod
    def load(reload=False):

        if Secrets.loaded and not reload:
            return

        # Secrets file are in CSV format. ie
        # secret key one, secrete value one
        # secret key two, secrete value two
        files = os.listdir( "Configs/Secrets/" )

        for f in files:
            if f != "SHOWFILE":
                with open("Configs/Secrets/"+f) as file:
                    secrets_lines = file.readlines()  # format key, value
                    # add the values to the secrets store.
                    for l in secrets_lines:
                        key, value = l.split(",")
                        Secrets.store[key] = value
