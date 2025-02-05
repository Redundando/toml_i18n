from toml_i18n import TomlI18n, i18n

def main():
    TomlI18n.initialize(directory="i18n_test")
    print(i18n("test.greeting"))

if __name__ == '__main__':
    main()