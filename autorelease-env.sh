INSTALL_AUTORELEASE="python -m pip install autorelease==0.2.3 nose"
PACKAGE_IMPORT_NAME=paths_cli
AUTORELEASE_TEST_TESTPYPI="python -m pip install sqlalchemy dill pytest && py.test --pyargs $PACKAGE_IMPORT_NAME"
