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
                        line = l.split(",")

                        if len(line) < 2:
                            print("bad line in secrets")
                            continue

                        key, value = line

                        # remove the new line if present
                        # todo improve
                        if value[-1] == '\n':
                            value = value[:-1]
                        if value[0] == ' ':
                            value = value[1:]
                        if key[0] == ' ':
                            key = key[1:]

                        Secrets.store[key] = value
