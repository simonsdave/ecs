#!/usr/bin/env python

from ecs.main import Main

if __name__ == '__main__':
    main = Main()
    main.configure()
    main.listen()
