#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Pies, Orders
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User, Pies=Pies, Orders=Orders)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def deploy(make_menu=False, seed=False):
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Pies, User, Orders

    # migrate database to latest revision
    upgrade()
    # if deploying for the first time, create the pie menu
    if make_menu:
        # build the menu of pies
        Pies.add_menu()

    # seed the database with data
    if seed:
        # create fake users so there's some data in the DB
        User.generate_fake(200)

        # create some orders too
        Orders.generate_orders(600)

if __name__ == '__main__':
    manager.run()
