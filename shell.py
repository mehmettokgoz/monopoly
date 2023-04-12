import cmd


class MonopolyShell(cmd.Cmd):
    intro = 'Welcome to the Monopoly shell. Type help or ? to list commands.\n'
    prompt = 'monopoly> '
    file = None

    def close(self):
        if self.file:
            self.file.close()
            self.file = None


def parse(arg):
    return tuple(map(int, arg.split()))


if __name__ == '__main__':
    MonopolyShell().cmdloop()
